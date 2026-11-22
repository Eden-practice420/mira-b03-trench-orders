"""Run the scientific programs in a temporary workspace and print the measured evidence."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(directory, script, *args):
    print("RUN  " + " ".join([script, *args]), flush=True)
    completed = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", script, *args],
        cwd=directory, check=True, capture_output=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return completed.stdout

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def main():
    with tempfile.TemporaryDirectory(prefix="mira-replay-") as scratch:
        work = Path(scratch) / "附件"
        shutil.copytree(ROOT / "附件", work)
        review = work / "复核实验"
        base = json.loads(run(work, "analyze.py", "trenches.json"))
        print("南北双沟 | 合法顺序", base["南北双沟"]["extensions"])
        cycle = base["抄录冲突"]["conflicts"][0]
        print("抄录冲突 | " + " > ".join(cycle["cycle"]))
        print("矛盾记录 | " + " / ".join(item[0] for item in cycle["field_records"]))
        res = json.loads(run(review, "survey.py"))["two-trenches"]
        print("可行历史 |", res["initial_orders"])
        for name in ("field-id", "split"):
            step = res[name]["steps"]["2"]
            print(f"{name} | 两次后均值 {step['expected']} | 最坏 {step['worst']}")
        print("无法观测 | 保留", res["unobservable_first_probe_orders"], "种")


if __name__ == "__main__":
    main()
