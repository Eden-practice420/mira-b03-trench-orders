"""Bayes-optimal one-step choice under uniform linear extensions and equal observation cost."""
import csv,itertools,json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def experiment(block):
    nodes=block["units"];assert 1<=len(nodes)<=8 and len(nodes)==len(set(nodes))
    perms=[p for p in itertools.permutations(nodes) if all(p.index(a)<p.index(b) for a,b in block["earlier"])]
    if not perms:raise ValueError("Contradictory input")
    universe=tuple(range(len(perms)))
    tests={tuple(pair):{i for i,p in enumerate(perms) if p.index(pair[0])<p.index(pair[1])} for pair in block["permitted"]}
    @lru_cache(None)
    def choose(candidates,mode):
        choices=[]
        for pair,yes_set in tests.items():
            ny=sum(i in yes_set for i in candidates);nn=len(candidates)-ny
            if not ny or not nn:continue
            # Conditional expected survivor count after one conclusive field check.
            choices.append((Fraction(ny*ny+nn*nn,ny+nn),pair))
        if not choices:return None
        return min(choices)[1] if mode=="split" else min(pair for _,pair in choices)
    out=[];summary={}
    for mode in ("field-id","split"):
        for hidden in universe:
            curr=universe
            for step in range(1,3):
                pair=choose(curr,mode)
                if pair:
                    answer=hidden in tests[pair]
                    nxt=tuple(i for i in curr if (i in tests[pair])==answer)
                else:
                    answer=None;nxt=curr
                assert hidden in nxt
                out.append([block["id"],mode,"".join(perms[hidden]),step,len(curr),"-".join(pair or []),answer,len(nxt)])
                curr=nxt
        current=[r for r in out if r[1]==mode]
        stats={}
        for step in (1,2):
            v=[r[-1] for r in current if r[3]==step]
            stats[str(step)]={"expected":round(sum(v)/len(v),3),"worst":max(v),"best":min(v)}
        summary[mode]={"first_probe":choose(universe,mode),"steps":stats}
    assert summary["split"]["steps"]["1"]["expected"]<=summary["field-id"]["steps"]["1"]["expected"]+1e-6
    # A failed observation returns no directional claim and keeps all candidates.
    return {"initial_orders":len(universe),"unobservable_first_probe_orders":len(universe),**summary},out

allrows=[];summary={}
for block in json.loads((ROOT/"survey_plans.json").read_text(encoding="utf-8")):
    data,rows=experiment(block);allrows.extend(rows);summary[block["id"]]=data
(ROOT/"results.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
with (ROOT/"all_hidden_orders.csv").open("w",encoding="utf-8",newline="") as fp:
    w=csv.writer(fp);w.writerow(["trench","policy","hidden_order","step","before","contact","answer","after"]);w.writerows(allrows)
print(json.dumps(summary))
