"""Verify archived L03 scores offline. No API calls, no edits to historical records.
Usage: python l03_helper.py --data-dir <internal L03 directory> [--output <new JSON file>]
"""
import argparse, csv, json, statistics
from pathlib import Path

def read_csv(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def verify(root):
    ref=read_csv(root/"approved_reference_scores.csv")
    scores=read_csv(root/"candidate_judge_scores.csv")
    refs={x["response_id"]:x for x in ref}
    if len(refs)!=len(ref) or len(ref)!=30: raise ValueError("Expected 30 unique reference records")
    result={}
    for provider in ("Gemini","GPT","Claude"):
        rows=[x for x in scores if x["judge_provider"]==provider]
        if len(rows)!=30 or {x["response_id"] for x in rows}!=set(refs): raise ValueError("Incomplete or duplicate candidate scores")
        diffs=[]; quality=[]
        for x in rows:
            r=refs[x["response_id"]]
            if x["status"]!="ok" or x["question_id"]!=r["question_id"]: raise ValueError("Invalid record")
            o,e,t=(int(x[k]) for k in ("option_score","evidence_score","total_score"))
            if o not in (0,1) or e not in (0,1) or e>o or t!=o+e or o!=int(r["human_option_score"]): raise ValueError("Invalid score")
            diffs.append(abs(t-int(r["human_total_score"])))
            for k in ("accuracy","groundedness","condition_unit"):
                a,b=int(x[k]),int(r["human_"+k])
                if not 1<=a<=5 or not 1<=b<=5: raise ValueError("Invalid G-Eval score")
                quality.append(abs(a-b))
        result[provider]={"n":len(rows),"mae_0_2":statistics.mean(diffs),"exact_match_rate":diffs.count(0)/len(diffs),"g_eval_mean_mae":statistics.mean(quality)}
    return {"reference_method":"LLM-assisted then human-approved; not independent human ratings","reference_distribution":{str(i):sum(int(r["human_total_score"])==i for r in ref) for i in (0,1,2)},"metrics":result,"status":"archived manual scores only; no live API verification"}

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--data-dir",type=Path,default=Path(__file__).resolve().parent); ap.add_argument("--output",type=Path); a=ap.parse_args()
    result=verify(a.data_dir); s=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output:
        with a.output.open("x",encoding="utf-8") as f: f.write(s)
    else: print(s,end="")
if __name__=="__main__":main()
