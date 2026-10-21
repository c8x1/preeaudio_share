from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('scenario_revision.py')), run_name='__main__')
