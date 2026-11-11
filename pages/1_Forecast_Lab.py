from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1]/'deployment/app.py'),init_globals={'PUBLIC_PAGE':'Forecast Lab'})
