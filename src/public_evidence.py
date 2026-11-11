"""Preserved public case narratives and scientific disclosures."""
import streamlit as st
from src.public_theme import kicker

def vocabulary():
    st.caption("Per 90 means per 90 minutes of recorded playing time, including stoppage time. NPG = goals excluding penalties. xA = estimated chance quality created for teammates, not actual assists.")

def stories(board, pred):
    kicker('Case studies / player intelligence')
    olise=board[board.player_id.eq(371281)&board.team_id.eq(37)].iloc[0]
    dembele=pred[pred.player_id.eq(299513)].iloc[0]
    st.subheader('1. Michael Olise: a creative-profile video question')
    st.write(f'Bayern, 2024/25, attacking midfield/wing: {int(olise.minutes):,} recorded minutes; descriptive screen {olise.screening_score:.2f}/100. He recorded {olise.xa_p90:.3f} xA and {olise.key_passes_p90:.3f} key passes per 90.')
    st.write('The saved comparison method identifies Rayan Cherki, Maghnes Akliouche and Xavi Simons as close statistical profiles. Watch receiving zones, pressure and chance creation before judging whether the roles really match. Team possession and league strength are unadjusted. No age, value or availability conclusion follows.')
    st.subheader('2. Ousmane Dembele: an estimate checked against a later record')
    st.write(f'PSG, 2024/25: {int(dembele.minutes):,} recorded minutes. The saved model estimate was {dembele.ridge:.3f} NPG+xA per 90; simple comparison {dembele.shrinkage:.3f}; later observed 2025/26 rate {dembele.target_rate:.3f}. Historical error range {dembele.ridge_low:.3f}-{dembele.ridge_high:.3f}.')
    st.write('A close result for one player is not general proof. Across 391 observed outcomes, model average error was 0.112 versus 0.121 for shrinkage. Ask how role, team and exposure changed; do not invent injuries, contracts or transfer explanations. This exposed-period research cannot automate decisions.')

def methodology():
    kicker('Methodology / limitations and attribution')
    st.subheader('What the website can and cannot tell you')
    st.write('Use it to explore recorded performance, form a video-review queue and question statistical comparisons. Do not use it to infer potential, value, availability, medical circumstances, agency relationships or causal club fit.')
    vocabulary()
    st.write('Five European leagues; descriptive screen: 2024/25. Research inputs span 2018/19-2025/26. Known source gaps and flagged matches exist. Transfers combine covered stints for the research study; leagues outside coverage are unknown.')
    st.warning('Scientific limits: previously exposed test period; unknown historical training cutoff of the upstream xG model; selective missing outcomes; unreliable historical ages; varied role coverage and repeated players. None has been resolved by publishing a website.')
    st.write('This website reads saved records and estimates. It does not train models, request uploads, write to the research database or make live predictions.')

