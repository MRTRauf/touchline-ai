"""Transparent player-season feature engineering from openplay player-match stats.

Never infer market value or transfer availability from on-field performance alone.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RAW_METRICS = [
    'progressive_passes', 'passes_into_box', 'passes_final_third',
    'key_passes', 'xa', 'npxg', 'dribbles_completed',
    'ball_recoveries', 'interceptions', 'tackles_won',
    'crosses_completed', 'shots', 'non_penalty_goals',
    'clearances', 'aerials_won', 'passes_completed',
]

ROLE_WEIGHTS = {
    'CB': {'progressive_passes': .27, 'interceptions': .20, 'aerials_won': .16,
           'ball_recoveries': .20, 'tackles_won': .17},
    'FB/WB': {'progressive_passes': .23, 'passes_into_box': .16, 'xa': .17,
              'ball_recoveries': .18, 'tackles_won': .13, 'dribbles_completed': .13},
    'CM/DM': {'progressive_passes': .25, 'passes_final_third': .15, 'key_passes': .15,
              'ball_recoveries': .20, 'interceptions': .15, 'xa': .10},
    'AM/W': {'xa': .22, 'key_passes': .20, 'dribbles_completed': .20,
             'passes_into_box': .16, 'npxg': .12, 'progressive_passes': .10},
    'ST': {'npxg': .33, 'shots': .24, 'non_penalty_goals': .15,
           'xa': .12, 'key_passes': .08, 'dribbles_completed': .08},
}

MIN_MINUTES = 900
EXPOSURE_PRIOR = 900
KEYS = ['comp', 'season', 'player_id', 'team_id']


def require_columns(df, columns, name):
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f'{name} missing required columns: {missing}')


def validate_match_rows(df, name):
    require_columns(df, KEYS + ['match_id', 'minutes_played'], name)
    if df[KEYS + ['match_id']].isna().any().any():
        raise ValueError(f'{name}: missing identity')
    if df.duplicated(KEYS + ['match_id']).any():
        raise ValueError(f'{name}: duplicate player-match rows')
    # Source explicitly flags event players absent from lineups; their minutes are unknown.
    known = df['in_lineup'] if 'in_lineup' in df else pd.Series(True, index=df.index)
    minutes = pd.to_numeric(df.loc[known, 'minutes_played'], errors='coerce')
    if not np.isfinite(minutes.to_numpy(dtype=float)).all() or not minutes.between(0, 150).all():
        raise ValueError(f'{name}: invalid expanded minutes (expected 0..150)')


def role_of_position(position: object) -> str:
    """Map openplay starting lineup position codes to a broad comparable role.

    Uncertain/substitutes are Unknown, never silently classified as a striker.
    """
    if pd.isna(position):
        return 'Unknown'
    p = str(position).upper().replace(' ', '').replace('(', '').replace(')', '')
    if p in ('SUB', 'UNKNOWN', '', 'NAN'):
        return 'Unknown'
    if p.startswith('GK'):
        return 'GK'
    if p in ('DC', 'DCR', 'DCL', 'CB', 'CBR', 'CBL'):
        return 'CB'
    if p.startswith(('DL','DR','DML','DMR','WBL','WBR')) or p in ('LB','RB','LWB','RWB'):
        return 'FB/WB'
    if p.startswith(('DMC','MC','MCL','MCR')) or p in ('DM','CM','CDM'):
        return 'CM/DM'
    if p.startswith(('AMC', 'AML', 'AMR', 'ML', 'MR')) or p in ('LW','RW','AM','CAM','LM','RM'):
        return 'AM/W'
    if p in ('FWL', 'FWR'):
        return 'AM/W'
    if p.startswith(('FW','ST','FC')) or p in ('CF',):
        return 'ST'
    return 'Unknown'


def most_common_non_sub(values: pd.Series) -> str:
    vals = values.dropna().astype(str)
    vals = vals[~vals.str.upper().isin(['SUB', 'UNKNOWN', 'NAN', ''])]
    if vals.empty:
        return 'Unknown'
    return vals.mode().iloc[0]


def build_player_seasons(player_matches: pd.DataFrame,
                         lineups: pd.DataFrame,
                         min_minutes: int = 900) -> pd.DataFrame:
    """Aggregate match-level events with role and age information from lineups.

    Cohort age is approximate age reported in the last matchday squad of a season;
    age is NOT an exact birthdate or age on a fixed calendar date.
    """
    k = ['comp', 'season', 'player_id', 'team_id']
    identity = ['player', 'team']
    if min_minutes <= 0:
        raise ValueError('min_minutes must be positive')
    required_p = k + identity + ['match_id', 'minutes_played']
    required_l = k + ['match_id', 'minutes_played', 'age', 'position', 'date']
    for col in required_p:
        if col not in player_matches.columns:
            raise ValueError(f'player_match_stats missing required column: {col}')
    for col in required_l:
        if col not in lineups.columns:
            raise ValueError(f'lineups missing required column: {col}')
    p = player_matches.copy()
    l = lineups.copy()
    validate_match_rows(p, 'player_match_stats')
    validate_match_rows(l, 'lineups')
    l['date'] = pd.to_datetime(l['date'], errors='raise')
    if l.date.isna().any():
        raise ValueError('Missing lineup date')
    for c in RAW_METRICS:
        if c not in p.columns:
            raise ValueError(f'player_match_stats missing required metric {c}; check openplay version')
        p[c] = pd.to_numeric(p[c], errors='coerce')
        if not np.isfinite(p[c].to_numpy(dtype=float)).all() or (p[c] < 0).any():
            raise ValueError(f'Unexpected missing values in {c}; inspect source coverage rather than assuming zero')
    p['minutes_played'] = pd.to_numeric(p['minutes_played'], errors='raise')
    if 'in_lineup' in p:
        p = p[p.in_lineup]
    p = p[p['minutes_played'] > 0]
    group = p.groupby(k, dropna=False, observed=True)
    agg = group[RAW_METRICS + ['minutes_played']].sum().reset_index()
    names = group[identity].last().reset_index()
    agg = agg.merge(names, on=k, validate='one_to_one')
    # Position is from named starting XI because substitutes are 'Sub'.
    # Determine broad role by starting minutes, not alphabetic ties between positions.
    l['mapped_role'] = l.position.map(role_of_position)
    starts = l[(l.mapped_role != 'Unknown') & (l.minutes_played > 0)].copy()
    role_minutes = starts.groupby(k + ['mapped_role'], observed=True).minutes_played.sum().reset_index()
    start_roles = (role_minutes.sort_values(['minutes_played', 'mapped_role'], ascending=[False, True])
                   .drop_duplicates(k).rename(columns={'mapped_role': 'role'})[k + ['role']])
    positions = (l.groupby(k, observed=True)['position'].apply(most_common_non_sub)
                 .rename('position_code').reset_index())
    latest_age = (l.sort_values(['date', 'match_id'])
                  .groupby(k, dropna=False, observed=True).tail(1)[k+['age']]
                  .rename(columns={'age':'age_last_recorded'}))
    agg = agg.merge(start_roles, on=k, how='left', validate='one_to_one')
    agg = agg.merge(positions, on=k, how='left', validate='one_to_one')
    agg = agg.merge(latest_age, on=k, how='left', validate='one_to_one')
    agg['role'] = agg['role'].fillna('Unknown')
    agg['age_last_recorded'] = pd.to_numeric(agg['age_last_recorded'], errors='coerce')
    agg['minutes'] = agg.pop('minutes_played')
    agg = agg[agg['minutes'] >= min_minutes].copy()
    for c in RAW_METRICS:
        agg[c + '_p90'] = 90 * agg[c] / agg['minutes']
    agg['is_youth_candidate'] = agg['age_last_recorded'].lt(23) # under 23, approximate only
    agg['exposure_weight'] = agg['minutes'] / (agg['minutes'] + EXPOSURE_PRIOR)
    return agg.sort_values(['role','minutes'], ascending=[True,False]).reset_index(drop=True)


def score_players(df: pd.DataFrame) -> pd.DataFrame:
    """Heuristic within-role scouting percentile screen, not ML probability/value."""
    if df.season.nunique() > 1:
        return pd.concat([score_players(g) for _, g in df.groupby('season', observed=True)]).sort_index()
    out = df.copy()
    out['screening_score'] = np.nan
    for role, weights in ROLE_WEIGHTS.items():
        mask = out['role'] == role
        if mask.sum() < 2:
            continue
        scores = pd.Series(0.0, index=out.index[mask])
        reliability = out.loc[mask, 'minutes'] / (out.loc[mask, 'minutes'] + EXPOSURE_PRIOR)
        for metric, weight in weights.items():
            col = metric + '_p90'
            values = out.loc[mask, col]
            if not np.isfinite(values.to_numpy(dtype=float)).all():
                raise ValueError(f'Unavailable scoring metric: {col}')
            pct = 100 * (values.rank(method='average') - .5) / len(values)
            out.loc[mask, metric + '_percentile'] = pct
            contribution = weight * (50 + reliability * (pct - 50))
            out.loc[mask, metric + '_contribution'] = contribution
            scores += contribution
        out.loc[mask, 'screening_score'] = scores
    return out
