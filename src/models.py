"""Descriptive role comparisons; no prediction or private player attributes."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.features import ROLE_WEIGHTS, EXPOSURE_PRIOR


def select_anchor(df, player_id, team_id, comp, season=None):
    mask = (df.player_id == player_id) & (df.team_id == team_id) & (df.comp == comp)
    if season is not None:
        mask &= df.season == season
    rows = df.loc[mask]
    if len(rows) != 1:
        raise ValueError('Select one player/team/competition/season identity')
    return rows.iloc[0]


def role_percentiles(df, player_id, team_id, comp, season=None):
    a = select_anchor(df, player_id, team_id, comp, season)
    weights = ROLE_WEIGHTS.get(a.role, {})
    pool = df[(df.role == a.role) & (df.season == a.season)]
    if len(pool) < 2:
        return pd.DataFrame()
    rows = []
    for metric, weight in weights.items():
        values = pool[metric + '_p90'].astype(float)
        if not np.isfinite(values).all():
            raise ValueError(f'Unavailable metric: {metric}')
        value = float(a[metric + '_p90'])
        pct = 100 * ((values < value).sum() + .5 * (values == value).sum()) / len(values)
        exposure = float(a.minutes) / (float(a.minutes) + EXPOSURE_PRIOR)
        rows.append(dict(metric=metric, per90=value, percentile=pct, weight=weight,
                         contribution=weight * (50 + exposure * (pct - 50)), peers=len(pool)))
    return pd.DataFrame(rows)


def find_similar_players(df, player_id, team_id, comp, role=None, top_k=8, season=None):
    a = select_anchor(df, player_id, team_id, comp, season)
    if role is not None and role != a.role:
        raise ValueError('Similarity must use the anchor role')
    if a.role not in ROLE_WEIGHTS or top_k <= 0:
        return pd.DataFrame()
    pool = df[(df.role == a.role) & (df.season == a.season)].reset_index(drop=True)
    if len(pool) < 3:
        return pd.DataFrame()
    metrics = [m + '_p90' for m in ROLE_WEIGHTS[a.role]]
    X = pool[metrics].astype(float)
    if not np.isfinite(X.to_numpy()).all():
        raise ValueError('Unavailable similarity metrics; no implicit imputation')
    reliability = pool.minutes / (pool.minutes + EXPOSURE_PRIOR)
    mean = np.average(X, axis=0, weights=pool.minutes)
    adjusted = (X - mean).mul(reliability, axis=0) + mean
    scaled = StandardScaler().fit_transform(adjusted)
    anchor_index = pool.index[(pool.player_id == player_id) & (pool.team_id == team_id)
                              & (pool.comp == comp)][0]
    norms = np.linalg.norm(scaled, axis=1)
    if norms[anchor_index] < 1e-12:
        return pd.DataFrame()
    terms = scaled * scaled[anchor_index] / np.maximum(norms[:, None] * norms[anchor_index], 1e-12)
    pool['cosine_similarity'] = cosine_similarity(scaled[anchor_index:anchor_index+1], scaled).ravel()
    pool['similarity_contributions'] = [
        '; '.join(f'{m}: {v:+.3f}' for m, v in zip(ROLE_WEIGHTS[a.role], row)) for row in terms]
    pool = pool[(pool.player_id != player_id) & (norms > 1e-12)]
    cols = ['player_id', 'team_id', 'season', 'player', 'team', 'comp', 'age_last_recorded',
            'minutes', 'role', 'cosine_similarity', 'similarity_contributions']
    return (pool.sort_values(['cosine_similarity', 'player_id', 'team_id'], ascending=[False, True, True])
            .head(top_k)[cols].reset_index(drop=True))
