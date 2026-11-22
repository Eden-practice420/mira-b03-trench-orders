"""Use an independent factorial enumeration oracle for the supplied small trenches."""
import itertools
import json
from pathlib import Path
from analyze import inspect

ROOT=Path(__file__).resolve().parent
result={}
for block in json.loads((ROOT/"trenches.json").read_text(encoding="utf-8")):
    rows=block["earlier"]
    orders=[perm for perm in itertools.permutations(block["units"]) if all(perm.index(a)<perm.index(b) for a,b,_ in rows)]
    result[block["trench"]]=obs=inspect(block)
    assert obs["extensions"] == len(orders)
    if orders:
        comparable=sum(1 for a,b in itertools.combinations(block["units"],2) if len({p.index(a)<p.index(b) for p in orders})==1)
        assert obs["all_comparable"]==comparable
    else:
        path=obs["conflicts"][0]["cycle"]
        assert path[0]==path[-1] and all(any(u==a and v==b for u,v,_ in rows) for a,b in zip(path,path[1:]))
(ROOT/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
