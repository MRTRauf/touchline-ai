"""Read-only scouting operations over approved release bytes plus explicit QA flags."""
import numpy as np
import pandas as pd
from src.features import ROLE_WEIGHTS, KEYS
from src.models import find_similar_players
from src.public_exports import public_csv

METRICS = {
 'xa':'Chance quality created (xA)', 'npxg':'Non-penalty chance quality (npxG)',
 'key_passes':'Passes leading to a shot', 'progressive_passes':'Progressive passes',
 'passes_into_box':'Passes into penalty area', 'passes_final_third':'Final-third passes',
 'dribbles_completed':'Successful dribbles', 'ball_recoveries':'Ball recoveries',
 'interceptions':'Interceptions', 'tackles_won':'Tackles won', 'shots':'Shots',
 'non_penalty_goals':'Non-penalty goals', 'clearances':'Clearances',
 'aerials_won':'Aerial duels won', 'passes_completed':'Completed passes',
 'crosses_completed':'Completed crosses',
}
NAV = ['Scout Board','Player Intelligence','Compare Players','Similar Profiles','Forecast Lab','My Shortlist','Methodology & Limitations','Player Stories']
LEGACY = dict(zip(['Explore players','Compare statistical profiles','Understand next-season estimates','Two player stories','How to read the evidence'],[NAV[0],NAV[3],NAV[4],NAV[7],NAV[6]]))


def record_key(row):
    return '|'.join(str(row[k]) for k in KEYS)


def safe_board(records, flags):
    """Suppress identified invalid observations, not negatives in general. No imputation."""
    out = pd.DataFrame(records).copy()
    out['record_key'] = out.apply(record_key, axis=1)
    warnings=[]
    for i,row in out.iterrows():
        bad=flags['records'].get(row.record_key,[])
        out.loc[i, bad] = np.nan
        reasons=[]
        if bad: reasons.append('Derived rate unavailable after arithmetic audit: '+', '.join(METRICS.get(f.removesuffix('_p90'),f) for f in bad))
        if row.role in flags['unranked_roles']:
            out.loc[i,'screening_score']=np.nan
            reasons.append('Score unavailable: role reference pool uses an invalid derived rate')
        if not np.isfinite(row.minutes) or row.minutes<=0:
            out.loc[i,'screening_score']=np.nan
            reasons.append('Invalid exposure; excluded')
        for col in [c for c in out if c.endswith('_p90')]:
            v=out.at[i,col]
            if pd.notna(v) and (not np.isfinite(v) or v<0):
                out.at[i,col]=np.nan;reasons.append('Invalid nonnegative metric: '+col)
        if pd.notna(out.at[i,'screening_score']) and not 0<=out.at[i,'screening_score']<=100:
            out.at[i,'screening_score']=np.nan;reasons.append('Invalid descriptive score')
        if row.minutes<1800:reasons.append('Limited minutes: below 1,800; descriptive floor is 900')
        if row.known_issue_matches:reasons.append('Source issue flagged: '+str(int(row.known_issue_matches))+' match(es)')
        warnings.append('; '.join(reasons) or 'League context unadjusted')
    out['evidence_warning']=warnings
    return out


def ranked(board,role,leagues,min_minutes=900,query='',sort='screening_score',ascending=False,metric=None,threshold=None):
    rows=board[board.role.eq(role)&board.comp.isin(leagues)&board.minutes.ge(min_minutes)&board.screening_score.notna()].copy()
    if query:rows=rows[rows.player.str.contains(query,case=False,regex=False)|rows.player_id.astype(str).eq(query)]
    if metric and threshold is not None:rows=rows[rows[metric].notna()&rows[metric].ge(threshold)]
    rows=rows[np.isfinite(pd.to_numeric(rows[sort],errors='coerce'))]
    rows=rows.sort_values([sort,'player_id','team_id','comp','season'],ascending=[ascending,True,True,True,True],kind='stable').reset_index(drop=True)
    rows.insert(0,'rank',np.arange(1,len(rows)+1))
    return rows


def profile(board,row):
    """Finite metric-specific same-role/season pools; no recomputed screening rating."""
    pool=board[board.role.eq(row.role)&board.season.eq(row.season)]
    records=[]
    for m in ROLE_WEIGHTS.get(row.role,{}):
        field=m+'_p90';values=pool[field].dropna();v=row[field]
        pct=100*((values<v).sum()+.5*(values==v).sum())/len(values) if pd.notna(v) and len(values)>=2 else np.nan
        records.append({'metric':METRICS[m],'field':field,'per90':v,'percentile':pct,'peers':len(values)})
    return pd.DataFrame(records,columns=['metric','field','per90','percentile','peers'])


def similar(board,row,leagues,min_minutes=900,top_k=10):
    metrics=[m+'_p90' for m in ROLE_WEIGHTS.get(row.role,{})]
    if not metrics or row[metrics].isna().any():return pd.DataFrame()
    pool=board[board.role.eq(row.role)&board.season.eq(row.season)].dropna(subset=metrics).copy()
    result=find_similar_players(pool.assign(age_last_recorded=np.nan),int(row.player_id),int(row.team_id),row.comp,season=row.season,top_k=len(pool))
    if result.empty:return result
    return result[result.comp.isin(leagues)&result.minutes.ge(min_minutes)].head(top_k)


EXPORT_COLUMNS = set(['rank','record_key','player_id','team_id','player','team','comp','role','season','minutes','screening_score','evidence_warning','priority','review_note','metric','per90','percentile','peers','cosine_similarity','similarity_contributions'])|{m+'_p90' for m in METRICS}


def scouting_csv(frame):
    return public_csv(frame[[c for c in frame if c in EXPORT_COLUMNS]])


def shortlist_add(state,row):
    state.setdefault(row.record_key, {'record_key':row.record_key,'priority':'Standard','review_note':''})


def shortlist_table(state,board):
    if not state:return pd.DataFrame(columns=['record_key','player','priority','review_note'])
    return board.merge(pd.DataFrame(list(state.values())),on='record_key',how='inner',validate='one_to_one')

METRIC_HELP = {
 'xa':'Upstream expected-assist chance-quality estimate, not actual assists; historical model timing is uncertain.',
 'npxg':'Upstream non-penalty expected-goal chance quality, not goals scored or future finishing ability.',
 'key_passes':'Recorded passes leading to a shot.',
 'progressive_passes':'Source-defined progressive passing events; this app does not invent a distance threshold.',
 'passes_into_box':'Recorded completed passes into the penalty area.',
 'passes_final_third':'Recorded final-third passing rate; flagged overflow observations are unavailable.',
 'dribbles_completed':'Recorded successful dribbling events; no assessment of technical skill is implied.',
 'ball_recoveries':'Recorded recoveries of possession; event volume depends on team context.',
 'interceptions':'Recorded intercepted passes; not adjusted for possession or opportunities.',
 'tackles_won':'Recorded won tackle events, not a complete measure of defending.',
 'shots':'Recorded shot attempts per expanded 90 minutes.',
 'non_penalty_goals':'Recorded goals excluding penalties per expanded 90.',
 'clearances':'Recorded clearance events; more can reflect defensive workload.',
 'aerials_won':'Recorded won aerial duels; opportunity volume is unadjusted.',
 'passes_completed':'Recorded completed-pass rate; flagged overflow observations are unavailable.',
 'crosses_completed':'Recorded completed crosses; no inference about crossing decisions or tactical fit.',
}
