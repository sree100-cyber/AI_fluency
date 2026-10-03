"""One command: python run_all.py  -> regenerates everything in results/."""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
(HERE / "results").mkdir(exist_ok=True)
for gb in (10, 16):
    r = subprocess.run([sys.executable, str(HERE / "vram_estimate.py"), "--available", str(gb)],
                       capture_output=True, text=True, check=True)
    (HERE / "results" / f"estimator_output_{gb}GB.txt").write_text(r.stdout)
    print(f"saved results/estimator_output_{gb}GB.txt")
for script in ("scenario_estimates.py", "context_quant_study.py", "check_reality.py"):
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, str(HERE / script)], check=False)
