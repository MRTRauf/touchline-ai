"""Public scouting workspace. Session-only notes; immutable release and forecasts."""
import json
from textwrap import wrap
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.features import ROLE_WEIGHTS
from src.scouting import (METRICS,METRIC_HELP,NAV,LEGACY,safe_board,ranked,profile,similar,scouting_csv,shortlist_add,shortlist_table)
from src.public_theme import sidebar_brand,hero,kicker,player_card,role_radar
from src.public_exports import public_csv
from src.public_evidence import stories,methodology,vocabulary

LEAGUES={'eng':'England','esp':'Spain','ita':'Italy','ger':'Germany','fra':'France'}
ROLES={'AM/W':'Attacking midfielders / wingers','ST':'Strikers','CM/DM':'Central / defensive midfielders','FB/WB':'Fullbacks / wingbacks','CB':'Centre-backs','GK':'Goalkeepers (unscored)'}

@st.cache_data(show_spinner=False)
def prepare(content,quality_content):
    return safe_board(json.loads(content)['board'],json.loads(quality_content))


def go_to(page,key=None):
    st.session_state['workspace_nav']=page
    if key is not None:
        st.session_state['active_player']=key
        if page=='Player Intelligence':
            st.session_state['profile_select']=key
            st.session_state['profile_search']=''


def select_player(board,key='profile_select',options=None):
    rows=board if options is None else options
    labels={r.record_key:f'{r.player} | {r.team} | {r.comp.upper()} | ID {r.player_id}' for _,r in rows.iterrows()}
    if not labels:return None
    active=st.session_state.get('active_player')
    keys=list(labels)
    if active in keys and key not in st.session_state:st.session_state[key]=active
    selected=st.selectbox('Choose a player and team record',keys,format_func=labels.get,key=key)
    return rows[rows.record_key.eq(selected)].iloc[0]


def action_buttons(row,prefix):
    a,b,c=st.columns(3)
    a.button('Inspect profile',key=prefix+'_inspect',on_click=go_to,args=('Player Intelligence',row.record_key))
    if b.button('Add to shortlist',key=prefix+'_add'):
        shortlist_add(st.session_state['shortlist'],row);st.success('Added to this session’s shortlist.')
    c.button('Compare player',key=prefix+'_compare',on_click=queue_compare,args=(row.record_key,))


def queue_compare(key):
    values=st.session_state.get('comparison_selection',[])
    st.session_state['comparison_selection']=list(dict.fromkeys([key]+values))[:3]
    st.session_state['workspace_nav']='Compare Players'


def evidence(row):
    st.caption('Historical evidence · '+str(row.evidence_warning))
    st.caption('Age not verified · Nationality not verified. No age or nationality filter is available.')


def export_button(label,frame,name,key):
    st.download_button(label,scouting_csv(frame),file_name=name,mime='text/csv',key=key)


def scout_board(board):
    kicker('Player rankings / within your filtered role cohort')
    st.write('Descriptive performance screening, not talent, transfer availability or recruitment advice. League strength and possession are not adjusted.')
    a,b=st.columns(2)
    role=a.selectbox('Playing role',list(ROLE_WEIGHTS),format_func=ROLES.get,key='rank_role')
    countries=b.multiselect('Leagues',list(LEAGUES),default=list(LEAGUES),format_func=LEAGUES.get,key='rank_leagues')
    minimum=st.slider('Minimum recorded minutes',900,4000,900,100,key='rank_minutes')
    query=st.text_input('Find a player by name or player ID',key='rank_query')
    metrics=[m+'_p90' for m in ROLE_WEIGHTS[role]]
    options=['screening_score','minutes']+metrics
    labels={'screening_score':'Descriptive screening score','minutes':'Recorded minutes',**{m+'_p90':label+' /90' for m,label in METRICS.items()}}
    a,b,c=st.columns(3)
    sort=a.selectbox('Sort by',options,format_func=labels.get)
    asc=b.selectbox('Sort direction',['Highest first','Lowest first'])=='Lowest first'
    limit=c.selectbox('Show records',['Top 10','Top 25','Top 50','All eligible players'])
    with st.expander('Role-specific metric filter'):
        metric=st.selectbox('Minimum statistic',['None']+metrics,format_func=lambda v:labels.get(v,v))
        threshold=st.number_input('Minimum per 90',min_value=0.0,value=0.0,step=0.1,disabled=metric=='None')
    st.caption('Age not verified · Nationality not verified. Biographical filtering is disabled; no values are inferred.')
    rows=ranked(board,role,countries,minimum,query,sort,asc,None if metric=='None' else metric,threshold)
    eligible=board[board.role.eq(role)&board.comp.isin(countries)&board.minutes.ge(minimum)]
    st.caption(f'{len(rows):,} eligible matching records from {len(eligible):,} exposed records. Rank is order within this filtered cohort and selected statistic; ties break by player ID, team ID, league and season. Percentile reference pools do not follow board filters.')
    if role=='CM/DM':st.warning('CM/DM score rankings unavailable: the frozen role reference pool uses corrupted final-third-pass rates. Scores are not repaired or recomputed. Use Player Intelligence to inspect the available statistics.')
    if rows.empty:
        st.warning('No players match the ranking criteria. Missing or invalid scores never receive a rank. Try another role or less restrictive filters.');return
    view=rows if limit=='All eligible players' else rows.head(int(limit.split()[1]))
    cols=['rank','player','team','comp','role','season','minutes','screening_score']+metrics[:5]+['evidence_warning']
    st.dataframe(view[cols].rename(columns={'rank':'Rank','player':'Player','team':'Recorded club','comp':'League','role':'Role','season':'Season','minutes':'Minutes','screening_score':'Descriptive screen /100',**{m+'_p90':label+' /90' for m,label in METRICS.items()},'evidence_warning':'Evidence notes'}),hide_index=True,width='stretch')
    st.caption('Season code 2425 = 2024/25. Scores are preserved analyst-weighted descriptive heuristics. Below 1,800 minutes is flagged as limited exposure; the inclusion floor remains 900.')
    featured=st.selectbox('Open a ranked record',view.record_key.tolist(),format_func=lambda k: f"#{int(rows.loc[rows.record_key.eq(k),'rank'].iloc[0])} · {rows.loc[rows.record_key.eq(k),'player'].iloc[0]}")
    row=rows[rows.record_key.eq(featured)].iloc[0];st.metric('Rank in filtered cohort',int(row['rank']));player_card(row);evidence(row);action_buttons(row,'rank')
    export_button('Download filtered rankings',rows[cols],'touchline-rankings.csv','rank_download')


def intelligence(board):
    kicker('Player intelligence / evidence to investigate on video')
    query=st.text_input('Search players or recorded clubs',key='profile_search')
    rows=board[board.player.str.contains(query,case=False,regex=False)|board.team.str.contains(query,case=False,regex=False)]
    row=select_player(board,options=rows)
    if row is None:st.warning('No players match this search.');return
    player_card(row);evidence(row);action_buttons(row,'profile');vocabulary()
    a,b=st.columns(2);a.metric('Recorded minutes',f'{row.minutes:,.0f}');b.metric('Descriptive screen /100','Unavailable' if pd.isna(row.screening_score) else f'{row.screening_score:.1f}')
    st.caption('The saved screen is an analyst-defined checklist, not a probability, talent or future-ability measure.')
    p=profile(board,row)
    st.caption(f'Role pool: {int((board.role.eq(row.role)&board.season.eq(row.season)).sum())} same-role/season records before metric exclusions. Each percentile uses its own finite, valid metric pool; the Peers column gives that sample size. This does not recompute the saved score.')
    if p.empty:st.info('No outfield screening percentiles are defined for this role.')
    else:
        role_radar(p)
        st.dataframe(p[['metric','per90','percentile','peers']].rename(columns={'metric':'Statistic','per90':'Per 90','percentile':'Role percentile','peers':'Peers'}),hide_index=True,width='stretch')
        valid=p.dropna(subset=['percentile']).sort_values('percentile')
        if not valid.empty:
            st.write('Higher observed tendencies: '+', '.join(valid.tail(2).metric)+'.')
            st.write('Lower observed tendencies: '+', '.join(valid.head(2).metric)+'.')
            st.caption('Relative event output, not proof of technical ability, mentality or potential. Defensive volume can reflect low possession. Review receiving zones, pressure, role and off-ball work on video.')
            fig=go.Figure(go.Bar(x=valid.percentile,y=valid.metric,orientation='h',marker_color='#c8f743'))
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(range=[0,100],title='Percentile in the valid same-role metric pool'),margin=dict(l=10,r=10,t=10,b=40),height=360)
            st.plotly_chart(fig,width='stretch',key='profile_bars')
    with st.expander('What do these statistics mean?'):
        for m in ROLE_WEIGHTS.get(row.role,{}):st.write(f'{METRICS[m]}: {METRIC_HELP[m]}')
        st.caption('All rates use recorded minutes including stoppage time. These are descriptive event outputs, not an observation of talent.')
    with st.expander('All available recorded rates and quality flags'):
        st.dataframe(pd.DataFrame([{'Statistic':label,'Per 90':row[m+'_p90']} for m,label in METRICS.items()]),hide_index=True,width='stretch')
        st.caption('Corrupted rates are unavailable, not zero. Both negative and positive overflows were excluded; original release bytes remain intact.')
    export_button('Download this public player profile',pd.DataFrame([row]),'touchline-player.csv','profile_download')


def comparison(board):
    kicker('Comparison studio / two or three records')
    choices=board.set_index('record_key')
    labels={k:f'{r.player} | {r.team} | {r.role}' for k,r in choices.iterrows()}
    if 'comparison_selection' not in st.session_state:st.session_state['comparison_selection']=list(labels)[:2]
    keys=st.multiselect('Choose two or three players',list(labels),format_func=labels.get,max_selections=3,key='comparison_selection')
    if len(keys)<2:st.info('Choose at least two records. Players opened from rankings or your shortlist appear here.');return
    rows=choices.loc[keys].reset_index()
    same_role=rows.role.nunique()==1
    if not same_role:st.warning('Different roles: raw event rates are shown side by side, but a shared percentile radar is not defensible. These are not like-for-like roles.')
    if rows.comp.nunique()>1:st.warning('Different leagues: league strength, team possession and competitive context are unadjusted.')
    for col,(_,row) in zip(st.columns(len(rows)),rows.iterrows()):
        with col:player_card(row);evidence(row)
    metrics=list(ROLE_WEIGHTS.get(rows.role.iloc[0],{})) if same_role else ['xa','npxg','key_passes','progressive_passes','tackles_won']
    table=[];profiles=[]
    for _,row in rows.iterrows():
        p=profile(board,row);profiles.append((row,p))
        for m in metrics:
            match=p[p.field.eq(m+'_p90')]
            table.append({'player':row.player,'player_id':row.player_id,'team':row.team,'comp':row.comp,'role':row.role,'season':row.season,'minutes':row.minutes,'metric':METRICS[m],'per90':row[m+'_p90'],'percentile':match.percentile.iloc[0] if len(match) else np.nan,'evidence_warning':row.evidence_warning})
    table=pd.DataFrame(table);st.dataframe(table,hide_index=True,width='stretch')
    if same_role and metrics:
        st.caption('Percentiles use finite valid same-role/season metric pools, independent of candidate filters; unavailable observations are not zero.')
        fig=go.Figure()
        for row,p in profiles:
            if p.percentile.isna().any():continue
            # Short labels avoid cropping; complete metric names remain in the table.
            theta=['<br>'.join(wrap(METRICS[m],width=14)) for m in metrics]
            fig.add_trace(go.Scatterpolar(r=p.percentile.tolist()+p.percentile.tolist()[:1],theta=theta+theta[:1],name=f'{row.player} ({row.team})'))
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',polar=dict(bgcolor='rgba(0,0,0,0)',radialaxis=dict(range=[0,100],tickfont=dict(size=9),gridcolor='rgba(159,176,181,.2)'),angularaxis=dict(tickfont=dict(size=10))),margin=dict(l=95,r=95,t=40,b=110),height=470,legend=dict(orientation='h',y=-.2))
        if len(fig.data)<len(rows):st.info('Some selected profiles lack a valid role metric; only complete profiles are included in the overlay. The table retains unavailable values explicitly.')
        st.plotly_chart(fig,width='stretch',key='comparison_radar')
    first,second=rows.iloc[0],rows.iloc[1]
    differences=[f'{METRICS[m]}: {first[m+"_p90"]-second[m+"_p90"]:+.3f} /90' for m in metrics if pd.notna(first[m+'_p90']) and pd.notna(second[m+'_p90'])]
    st.write(f'Signed difference, {first.player} minus {second.player}: '+'; '.join(differences))
    st.caption('Negative differences are valid directional comparisons. Higher event output does not establish superior ability, tactical fit or availability. A third selected player is included in the table and same-role radar.')
    export_button('Download comparison with caveats',table,'touchline-comparison.csv','compare_download')


def similar_profiles(board):
    kicker('Similar profiles / explainable statistical alternatives')
    row=select_player(board,key='similar_anchor');player_card(row);evidence(row)
    leagues=st.multiselect('Candidate leagues',list(LEAGUES),default=list(LEAGUES),format_func=LEAGUES.get)
    minutes=st.slider('Candidate minimum minutes',900,4000,900,100)
    st.caption('Same-role, same-season only. Role rates are exposure-shrunk toward their minutes-weighted mean, then standardized before cosine comparison. Invalid-feature records and zero vectors are excluded. Candidate filters apply after normalization; the anchor and all its other stints are excluded.')
    result=similar(board,row,leagues,minutes)
    if result.empty:st.info('No defined comparables for this selection. The anchor may lack a valid role metric, or the valid pool may be too small.');return
    st.dataframe(result[['player','team','comp','minutes','cosine_similarity','similarity_contributions']],hide_index=True,width='stretch')
    st.caption('Cosine ranges from −1 to +1: negative values indicate opposing standardized profiles, not negative counts or failure probabilities. Signed feature contributions explain the total. Shared low output can also align profiles. Resemblance is not equal talent or transfer suitability.')
    choice=st.selectbox('Inspect a comparable',range(len(result)),format_func=lambda i:result.iloc[i].player)
    candidate=result.iloc[choice];selected=board[(board.player_id.eq(candidate.player_id))&board.team_id.eq(candidate.team_id)&board.comp.eq(candidate.comp)&board.season.eq(candidate.season)].iloc[0]
    action_buttons(selected,'similar');export_button('Download these public comparables',result,'touchline-comparables.csv','similar_download')


def forecast_lab(data):
    kicker('Forecast lab / retrospective only')
    st.subheader('A historical estimate, not a signing recommendation')
    st.write('Retrospective estimate of next-season recorded NPG+xA per 90')
    st.warning('The 2025/26 period was seen during development. This is a retrospective research check, not proof of future forecasting performance.')
    st.write('Of 524 eligible players, only 391 have a usable next-season record. The other 133 are not assigned zero performance. Results describe players with recorded outcomes, not everyone who was considered.')
    vocabulary();pred=pd.DataFrame(data['predictions'])
    query=st.text_input('Search forecast players',key='forecast_search')
    pred=pred[pred.player.str.contains(query,case=False,regex=False)|pred.player_id.astype(str).eq(query)]
    if pred.empty:st.info('No forecast candidates match.');return
    idx=st.selectbox('Choose a forecast candidate',pred.index.tolist(),format_func=lambda i:f'{pred.loc[i,"player"]} | {pred.loc[i,"team_stints"]} | ID {pred.loc[i,"player_id"]}')
    row=pred.loc[idx]
    for label,value in [('Recorded current rate',row.current_rate),('Saved Ridge estimate',row.ridge),('Saved shrinkage comparison',row.shrinkage)]:st.metric(label,f'{value:.3f}')
    st.write(f'Historical error range: {row.ridge_low:.3f} to {row.ridge_high:.3f} per 90. This is not a guaranteed individual confidence range or a probability of participation.')
    if pd.notna(row.target_rate):st.write(f'Later recorded result: {row.target_rate:.3f} per 90. Displayed for retrospective comparison, never used as an input to this estimate.')
    else:st.info('Outcome not observed: no usable later result is available. The estimate assumes observation; it does not predict whether the player played or why a record is missing.')
    names=['Current recorded','Saved Ridge','Saved shrinkage'];values=[row.current_rate,row.ridge,row.shrinkage]
    if pd.notna(row.target_rate):names+=['Later observed'];values+=[row.target_rate]
    fig=go.Figure(go.Bar(x=values,y=names,orientation='h',marker_color=['#9fb0b5','#c8f743','#35eac4','#e3eeea'][:len(values)]))
    fig.add_vrect(x0=row.ridge_low,x1=row.ridge_high,fillcolor='#c8f743',opacity=.1,line_width=0,annotation_text='Saved historical range')
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis_title='NPG+xA per expanded 90',margin=dict(l=10,r=10,t=40,b=40),height=330)
    st.plotly_chart(fig,width='stretch',key='forecast_rates')
    st.caption('Nominal 90% ranges covered 90.53% of winger/attacking-midfield outcomes (264 players) and 85.83% of striker outcomes (127). 243 players occur in both calibration and test periods.')
    st.download_button('Download this historical estimate with caveats',public_csv(pd.DataFrame([row])),file_name='touchline-estimate.csv',mime='text/csv')
    with st.expander('How did the approaches compare?'):
        st.dataframe(pd.DataFrame(data['metrics']),hide_index=True,width='stretch')
        st.write('MAE is the average size of an error in rate units; lower is better. RMSE gives larger mistakes more weight. Spearman describes rank association, not recruitment accuracy. Average absolute error was 0.112 for Ridge versus 0.121 for the simple comparison. The difference is modest. Lower error on these recorded players does not prove recruitment value.')
    st.warning('Unknown historical training cutoff of upstream xG; selective observed outcomes and cross-season coverage; ranges are not guaranteed individual intervals. Estimates describe conditional observed output, not intrinsic talent, causal club fit or recruitment value.')


def shortlist_view(board):
    kicker('My shortlist / this browser session only')
    st.info('Temporary review workspace. Entries and notes disappear when this session ends. No accounts or database. Do not enter personal, confidential or sensitive information; notes are not deliberately persisted by this app.')
    row=select_player(board,key='shortlist_picker')
    if st.button('Add selected player',key='shortlist_add'):shortlist_add(st.session_state['shortlist'],row)
    table=shortlist_table(st.session_state['shortlist'],board)
    if table.empty:st.info('Your shortlist is empty. Add a player here, from rankings, a profile or similarity results.');return
    for _,r in table.iterrows():
        with st.expander(f'{r.player} · {r.team}',expanded=True):
            state=st.session_state['shortlist'][r.record_key]
            state['priority']=st.selectbox('Analyst review priority',['Standard','High','Low'],index=['Standard','High','Low'].index(state['priority']),key='priority_'+r.record_key)
            state['review_note']=st.text_area('Scouting question / video-review note',value=state['review_note'],max_chars=500,key='note_'+r.record_key)
            st.caption('Note is included in this session’s download.' if state['review_note'] else 'No note entered yet.')
            a,b=st.columns(2)
            a.button('Compare shortlisted player',key='shortcompare_'+r.record_key,on_click=queue_compare,args=(r.record_key,))
            if b.button('Remove player',key='remove_'+r.record_key):
                del st.session_state['shortlist'][r.record_key];st.session_state.pop('priority_'+r.record_key,None);st.session_state.pop('note_'+r.record_key,None);st.rerun()
    export_button('Download shortlist and notes',shortlist_table(st.session_state['shortlist'],board),'touchline-shortlist.csv','shortlist_export')
    if st.button('Clear shortlist'):
        for key in list(st.session_state):
            if key.startswith(('priority_','note_')):del st.session_state[key]
        st.session_state['shortlist']={};st.rerun()


def render(data,quality,content,default=None):
    board=prepare(content,json.dumps(quality,sort_keys=True))
    st.session_state.setdefault('shortlist',{})
    sidebar_brand()
    route=LEGACY.get(default,default) if default else 'main'
    if 'workspace_nav' not in st.session_state or (default and st.session_state.get('_entry_route')!=route):
        st.session_state['workspace_nav']=route if default else NAV[0]
    st.session_state['_entry_route']=route
    page=st.sidebar.radio('YOUR SCOUTING WORKSPACE',NAV,key='workspace_nav')
    hero(page,len(board),len(LEAGUES),len(data['predictions']),sum(p['target_rate'] is not None for p in data['predictions']))
    st.caption('Explore player performance, compare statistical profiles, and examine historical forecasting evidence.')
    st.sidebar.caption('Session-only shortlist and notes. Nothing is written to a visitor database. Data and estimates are historical; no live scouting decisions are made.')
    if page=='Scout Board':scout_board(board)
    elif page=='Player Intelligence':intelligence(board)
    elif page=='Compare Players':comparison(board)
    elif page=='Similar Profiles':similar_profiles(board)
    elif page=='Forecast Lab':forecast_lab(data)
    elif page=='My Shortlist':shortlist_view(board)
    elif page=='Player Stories':stories(pd.DataFrame(data['board']),pd.DataFrame(data['predictions']))
    else:
        methodology()
        st.caption("Independent research project. Not an official product of any football club, agency, or league.")
        st.warning('Derived-rate audit: 124 final-third-pass rates and 1,315 completed-pass rates are invalid from int16 arithmetic overflow, including positive corrupted values. They are unavailable in analytical views. All 347 CM/DM scores are excluded from rankings because their reference pool uses final-third-pass rates; 121 goalkeepers remain unscored. No forecasts or original artifacts were changed.')
        st.write('Age not verified · Nationality not verified. The public bundle contains neither verified birthdates nor nationality. They are not inferred from names, club or league. Future enrichment must be separately versioned, licensed and identity-matched.')
        st.caption('Negative signed differences, residuals and cosine similarity may be valid. Invalid count-like rates are not clamped. Metric-specific percentile pools and valid-feature similarity pools exclude unavailable values explicitly.')
        st.write(data['disclosure'])
    st.divider()
    st.caption('Data: [openplay (Noah Bair)](https://github.com/nlbair/openplay), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Filtered and aggregated; saved estimates are independent research. No live scouting or private player information.')
