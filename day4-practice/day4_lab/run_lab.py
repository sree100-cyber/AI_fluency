"""One-command workflow for the Day 4 lab:  python run_lab.py [--available GB]

1. Runs the estimator for 8 GB and for your own figure -> outputs/vram_output_*.txt
2. Runs the Ollama reality check                        -> outputs/estimate_vs_reality.md
3. Prints where to paste each result.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--available", type=float, default=None, help="your real RAM/VRAM in GB")
args = parser.parse_args()

sizes = [8.0] + ([args.available] if args.available and args.available != 8.0 else [])
for gb in sizes:
    result = subprocess.run([sys.executable, str(HERE / "vram_estimate.py"), "--available", str(gb)],
                            capture_output=True, text=True, check=True)
    (OUT / f"vram_output_{gb:g}GB.txt").write_text(result.stdout)
    print(f"saved outputs/vram_output_{gb:g}GB.txt")

subprocess.run([sys.executable, str(HERE / "check_reality.py")], check=False)
print("\nDone. Paste outputs/ into report/02_observation_sheet.md and record the date of Part D.")
