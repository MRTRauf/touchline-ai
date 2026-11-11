import numpy as np
import pandas as pd
from src.features import RAW_METRICS,build_player_seasons,score_players,role_of_position
from src.models import find_similar_players,role_percentiles


def fixtures():
    players=[]; squads=[]
    for i,role in enumerate(['AMC','AMR','AMC','DC','DC','FW'],start=1):
        for match in range(1,6):
            x={c: 0 for c in RAW_METRICS}
            x.update({'progressive_passes': i+match, 'key_passes':i, 'xa':float(i)/10,
                      'npxg':float(i)/10, 'dribbles_completed': match, 'ball_recoveries':i*2})
            players.append({'comp':'eng','season':'2425','player_id':i,'team_id':i,
                            'match_id':match,
                            'player':f'Fixture Player {i}', 'team':f'Fixture Team {i}',
                            'minutes_played':90,**x})
            squads.append({'comp':'eng','season':'2425','player_id':i,'team_id':i,
                           'match_id':match, 'minutes_played':90,
                           'date':f'2025-01-{match:02}', 'position':role,'age':19+i})
    return pd.DataFrame(players),pd.DataFrame(squads)


def test_roles():
    assert role_of_position('AMC')=='AM/W'
    assert role_of_position('DMC')=='CM/DM'
    assert role_of_position('DC')=='CB'
    assert role_of_position('Sub')=='Unknown'


def test_aggregation_and_rates():
    p,l=fixtures()
    df=build_player_seasons(p,l,min_minutes=400)
    assert len(df)==6
    assert (df.minutes==450).all()
    assert np.isclose(df.loc[df.player_id==1,'xa_p90'].iloc[0],0.1)
    assert df.loc[df.player_id==1,'is_youth_candidate'].iloc[0]
    assert df.loc[df.player_id==1,'role'].iloc[0]=='AM/W'


def test_scores_and_similarity():
    p,l=fixtures()
    df=score_players(build_player_seasons(p,l,min_minutes=400))
    assert df[df.role=='AM/W'].screening_score.notna().all()
    sim=find_similar_players(df,1,1,'eng',top_k=5)
    # The middle fixture is exactly the role mean: cosine is undefined for its zero vector.
    assert len(sim)==1
    assert all(sim.player != 'Fixture Player 1')
    pct=role_percentiles(df,1,1,'eng')
    assert len(pct)>0 and pct.percentile.between(0,100).all()


def test_minimum_minutes_and_no_market_value():
    p,l=fixtures()
    df=build_player_seasons(p,l,min_minutes=500)
    assert df.empty
