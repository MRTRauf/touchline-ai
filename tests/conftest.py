import pytest
import pandas as pd
from test_features import fixtures
from src.features import build_player_seasons, score_players


@pytest.fixture(autouse=True)
def research_mode_for_existing_regressions(monkeypatch):
    # Technical workflow tests retain their original mode; public tests opt in explicitly.
    monkeypatch.setenv('TOUCHLINE_MODE','research')


@pytest.fixture
def scored():
    p, l = fixtures()
    p = pd.concat([p, p.assign(match_id=p.match_id + 5)], ignore_index=True)
    l = pd.concat([l, l.assign(match_id=l.match_id + 5)], ignore_index=True)
    df = score_players(build_player_seasons(p, l, min_minutes=900))
    df['known_issue_matches'] = 0
    return df
