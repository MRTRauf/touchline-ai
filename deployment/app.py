"""Public read-only football guide; consumes only the curated JSON bundle."""
import hashlib
import json
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.models import role_percentiles,find_similar_players
from src.features import ROLE_WEIGHTS
from src.public_mode import bundle_path
from src.public_exports import public_csv
from src.public_theme import install_theme, sidebar_brand, hero, kicker, player_card, role_radar

st.set_page_config(page_title='Touchline AI — Football Player Intelligence',page_icon=':soccer:',layout='wide')
install_theme()
release_path=Path(__file__).parent/'public-release.json'
if release_path.exists():
    from urllib.parse import urlparse
    release=json.loads(release_path.read_text(encoding='utf-8'))
    site=release.get('portfolio_url')
    if release.get('portfolio_url_verified') is True and isinstance(site,str) and urlparse(site).scheme=='https' and urlparse(site).hostname=='mrtrauf.github.io':
        st.sidebar.link_button('Read the public methodology',site.rstrip('/')+'/#method')


@st.cache_data(show_spinner=False)
def parse_verified_content(content):
    return json.loads(content)


try:
    folder=bundle_path(ROOT)
    content=(folder/'public.json').read_bytes()
    if hashlib.sha256(content).hexdigest()!=(folder/'public.sha256').read_text().strip():raise ValueError('Bundle checksum mismatch')
    manifest_path=folder/'bundle_manifest.json'
    if folder.name=='cloud_bundle' or manifest_path.exists():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for name in ['public.json','public.sha256']:
            blob=(folder/name).read_bytes()
            if len(blob)!=manifest['files'][name]['bytes'] or hashlib.sha256(blob).hexdigest()!=manifest['files'][name]['sha256']:
                raise ValueError('Public manifest mismatch')
    data=parse_verified_content(content)  # Content-keyed cache, after every-render verification.
    if data['schema']!=1:raise ValueError('Unsupported bundle')
except Exception:
    st.error('The demonstration data is unavailable or inconsistent. Please contact the website owner; no replacement player data is generated.')
    st.stop()

from src.scouting_ui import render
try:
    quality=json.loads((ROOT/'deployment/quality_flags.json').read_bytes())
    if quality['bundle_sha256']!=hashlib.sha256(content).hexdigest():
        raise ValueError('Quality overlay belongs to a different release')
except Exception:
    st.error('The demonstration data is unavailable or inconsistent. The verified quality overlay is required; no replacement player data is generated.')
    st.stop()
render(data,quality,content,globals().get('PUBLIC_PAGE'))
