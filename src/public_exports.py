"""CSV downloads contain only public data with portable attribution and caveats."""
import pandas as pd


def public_csv(frame):
    out=frame.drop(columns=['age_last_recorded','is_youth_candidate'],errors='ignore').copy()
    out['source']='openplay (Noah Bair)'
    out['source_url']='https://github.com/nlbair/openplay'
    out['license']='CC BY 4.0'
    out['disclosure']='Retrospective descriptive/conditional research; exposed 2025/26; selective missing outcomes; upstream xG timing unknown; historical age eligibility unverified; not potential, value, availability or recruitment advice.'
    for col in out.select_dtypes(include=['object','string','category']):
        out[col]=out[col].astype('string').map(lambda x:"'"+x if pd.notna(x) and x.lstrip().startswith(('=','+','-','@')) else x)
    return out.to_csv(index=False).encode('utf-8-sig')
