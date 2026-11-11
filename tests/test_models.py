import numpy as np
import pandas as pd
import pytest
from src.features import ROLE_WEIGHTS, score_players
from src.models import find_similar_players, role_percentiles


def test_explanations_reconstruct_score(scored):
    row = scored[scored.role == 'AM/W'].iloc[0]
    pct = role_percentiles(scored, row.player_id, row.team_id, row.comp, row.season)
    assert np.isclose(pct.contribution.sum(), row.screening_score)
    assert np.isclose(pct.weight.sum(), 1)
    assert pct.percentile.between(0, 100).all()


def test_exposure_shrinks_toward_midpoint(scored):
    low = scored.copy()
    low['minutes'] = 900
    high = low.copy()
    high['minutes'] = 3600
    lo, hi = score_players(low), score_players(high)
    mask = lo.role == 'AM/W'
    assert (abs(lo.loc[mask, 'screening_score'] - 50) <= abs(hi.loc[mask, 'screening_score'] - 50)).all()


def test_similarity_role_self_and_missing(scored):
    row = scored[scored.role == 'AM/W'].iloc[0]
    sim = find_similar_players(scored, row.player_id, row.team_id, row.comp)
    assert (sim.role == row.role).all()
    assert (sim.player_id != row.player_id).all()
    assert sim.cosine_similarity.between(-1, 1).all()
    for r in sim.itertuples():
        terms = [float(term.split(': ')[1]) for term in r.similarity_contributions.split('; ')]
        assert abs(sum(terms) - r.cosine_similarity) < .004
    with pytest.raises(ValueError, match='anchor role'):
        find_similar_players(scored, row.player_id, row.team_id, row.comp, role='CB')
    scored.loc[scored.role == 'AM/W', 'xa_p90'] = np.nan
    with pytest.raises(ValueError, match='imputation'):
        find_similar_players(scored, row.player_id, row.team_id, row.comp)


def test_season_disambiguation_and_reference_isolation(scored):
    other = scored.copy()
    other['season'] = '2526'
    other['xa_p90'] *= 100
    combined = pd.concat([scored, other], ignore_index=True)
    with pytest.raises(ValueError, match='identity'):
        role_percentiles(combined, 1, 1, 'eng')
    a = role_percentiles(scored, 1, 1, 'eng', '2425')
    b = role_percentiles(combined, 1, 1, 'eng', '2425')
    pd.testing.assert_frame_equal(a, b)
    rescored = score_players(combined)
    np.testing.assert_allclose(rescored.iloc[:len(scored)].screening_score, scored.screening_score, equal_nan=True)


def test_constant_role_vectors_have_no_cosine(scored):
    for m in ROLE_WEIGHTS['AM/W']:
        scored.loc[scored.role == 'AM/W', m + '_p90'] = 1
    assert find_similar_players(scored, 1, 1, 'eng').empty


def test_singleton_role_has_no_percentile_screen(scored):
    assert role_percentiles(scored, 6, 6, 'eng').empty
