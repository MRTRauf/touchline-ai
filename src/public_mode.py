"""Owner-controlled public mode; visitor inputs never select filesystem paths."""
import os
from pathlib import Path


def bundle_path(root):
    root=Path(root).resolve()
    default='deployment/cloud_bundle' if (root/'deployment/cloud_bundle').exists() or (root/'deployment/public-release.json').exists() else 'deployment/bundle'
    relative=Path(os.environ.get('TOUCHLINE_BUNDLE_DIR',default))
    path=(root/relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(root):
        raise ValueError('Public bundle must be a relative directory inside the deployment checkout')
    return path


def public_mode(root):
    mode=os.environ.get('TOUCHLINE_MODE','auto')
    if mode not in {'public','research','auto'}:raise ValueError('Invalid owner deployment mode')
    return mode=='public' or (mode=='auto' and ((Path(root)/'deployment/public-release.json').exists() or (bundle_path(root)/'public.json').exists()))
