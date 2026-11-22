import json
from pathlib import Path
from analyze import inspect
ROOT=Path(__file__).resolve().parent
block=json.loads((ROOT/"trenches.json").read_text(encoding="utf-8"))[-1]
out=[]
for i,edge in enumerate(block["earlier"]):
    altered=dict(block,earlier=block["earlier"][:i]+block["earlier"][i+1:])
    result=inspect(altered)
    out.append({"omitted":edge,"status":result["status"],"orders":result["extensions"]})
assert sum(r["orders"]>0 for r in out)==3
(ROOT/"stress.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
