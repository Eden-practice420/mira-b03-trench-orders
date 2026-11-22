"""Exhaustively count linear extensions of a small stratigraphic partial order."""
import argparse
import json
from collections import deque
from functools import lru_cache
from pathlib import Path

def witness(edges, start, goal, skip=None):
    todo = deque([(start,[start])])
    seen = {start}
    while todo:
        curr,path = todo.popleft()
        for tail,head in sorted(edges):
            if tail != curr or (tail,head) == skip:
                continue
            if head == goal:
                return path+[goal]
            if head not in seen:
                seen.add(head)
                todo.append((head,path+[head]))
    return None

def inspect(block):
    units = list(block["units"])
    if not 1 <= len(units) <= 16:
        raise ValueError("Exact enumeration supports 1 to 16 units")
    labels = {}
    for a,b,record in block["earlier"]:
        if a not in units or b not in units or not record.strip():
            raise ValueError("Unknown unit or empty field record")
        labels.setdefault((a,b),[]).append(record)
    conflicts = []
    for a,b in labels:
        path = [a] if a == b else witness(labels,b,a)
        if path:
            loop = [a] + path
            conflicts.append({"cycle":loop,"field_records":[labels[(u,v)] for u,v in zip(loop,loop[1:])]})
            break
    if conflicts:
        return dict(status="review-records",extensions=0,conflicts=conflicts)
    implied = []
    undecided = []
    for i,a in enumerate(units):
        for b in units[i+1:]:
            path = witness(labels,a,b) or witness(labels,b,a)
            if not path:
                undecided.append([a,b])
            elif len(path) > 2:
                implied.append(path)
    reduced = [[a,b] for a,b in labels if not witness(labels,a,b,skip=(a,b))]
    indexes = {u:1<<i for i,u in enumerate(units)}
    pred = {u:sum(indexes[a] for a,b in labels if b==u) for u in units}
    @lru_cache(None)
    def count(mask):
        if mask == (1<<len(units))-1:
            return 1
        return sum(count(mask | bit) for u,bit in indexes.items() if not (mask & bit) and (mask & pred[u]) == pred[u])
    return dict(status="partial-order",extensions=count(0),direct_pairs=len(labels),all_comparable=len(labels)+len(implied),
                minimal_edges=reduced,implied_witnesses=implied,incomparable=undecided)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("json",type=Path)
    blocks=json.loads(parser.parse_args().json.read_text(encoding="utf-8-sig"))
    if len({b["trench"] for b in blocks}) != len(blocks):
        raise ValueError("Duplicate trench ID")
    print(json.dumps({b["trench"]:inspect(b) for b in blocks},ensure_ascii=False,indent=2))
