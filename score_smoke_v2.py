import json
import math
import argparse
import sys
import pandas as pd
from pathlib import Path

# ===== Setup Arguments =====
parser = argparse.ArgumentParser(description="Compute smoke metrics for a specific prediction file.")
parser.add_argument("--pred_jsonl", type=str, required=True, help="Path to the prediction JSONL file.")
parser.add_argument("--data_dir", type=str, default="data", help="Directory containing GT csv files.")
parser.add_argument("--out_dir", type=str, default="results/smoke/v8ak", help="Directory to save outputs.")
args = parser.parse_args()

DATA_DIR = Path(args.data_dir)
OUT_DIR = Path(args.out_dir)

SMOKE_CSV = DATA_DIR / "smoke_subset.csv"
LABELS_CSV = DATA_DIR / "labels_v0_1_smoke_clean.csv"
PRED_JSONL = Path(args.pred_jsonl)

# Check if files exist before proceeding
if not PRED_JSONL.exists():
    print(f"[Error] The prediction file {PRED_JSONL} does not exist.")
    sys.exit(1)
if not SMOKE_CSV.exists() or not LABELS_CSV.exists():
    print(f"[Error] GT data missing. Please ensure {SMOKE_CSV} and {LABELS_CSV} exist.")
    sys.exit(1)

OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Processing: {PRED_JSONL}")
print(f"Saving to:  {OUT_DIR}")

# ===== Functions =====

def read_jsonl(p: Path) -> pd.DataFrame:
    rows = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except:
                pass
    return pd.DataFrame(rows)

def pick_col(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def parse_actions(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return []
    if isinstance(x, list):
        return x
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return []
    try:
        return json.loads(s)
    except:
        return []

def top_action_type(actions):
    if not actions:
        return "none"
    if isinstance(actions, dict):
        actions = [actions]
    if not isinstance(actions, list) or len(actions) == 0:
        return "none"
    t = actions[0].get("type", "unknown")
    return str(t)

TOL_NUM = {"percent": 20, "temperature": 2, "temp": 2, "brightness": 20}

def param_within_tol(gt, pr):
    if gt is None or pr is None:
        return True
    if not isinstance(gt, dict) or not isinstance(pr, dict):
        return True
    for k, gv in gt.items():
        if k not in pr:
            return False
        pv = pr[k]
        if isinstance(gv, (int, float)) and isinstance(pv, (int, float)) and k in TOL_NUM:
            if abs(float(gv) - float(pv)) > TOL_NUM[k]:
                return False
        else:
            if str(gv) != str(pv):
                return False
    return True

def action_match(gt_actions, pr_actions):
    if not gt_actions:
        return (not pr_actions, True)
    if not pr_actions:
        return (False, False)
    gt0, pr0 = gt_actions[0], pr_actions[0]
    if str(gt0.get("type")) != str(pr0.get("type")):
        return (False, False)
    ok_param = param_within_tol(gt0.get("param", {}), pr0.get("param", {}))
    return (ok_param, ok_param)

# ===== Main Logic =====
smoke = pd.read_csv(SMOKE_CSV)
labels = pd.read_csv(LABELS_CSV)
pred = read_jsonl(PRED_JSONL)

gt_should = pick_col(labels, ["gt_should_act", "gt_should", "gt_act", "should_act"])
if gt_should is None:
    raise ValueError(f"gt_should_act column not found in labels: {list(labels.columns)}")

gt_action_col = pick_col(labels, ["gt_action_json", "gt_action", "gt_actions"])
if gt_action_col is None:
    raise ValueError(f"gt_action_json column not found in labels: {list(labels.columns)}")

pred_action_col = pick_col(pred, ["pred_action_json", "actions"])
if pred_action_col is None:
    raise ValueError(f"pred_action_json column not found in pred jsonl keys: {list(pred.columns)}")

df = smoke.merge(labels, on="clip_id", how="left").merge(pred, on="clip_id", how="left", suffixes=("_smoke", "_pred"))

scene_col = pick_col(df, ["scene_id", "scene_id_smoke", "scene_id_pred", "scene_id_x", "scene_id_y"])
if scene_col is None:
    raise ValueError(f"scene_id not found after merge. columns={list(df.columns)}")
df["scene_id_resolved"] = df[scene_col]

split_col = pick_col(df, ["split", "split_smoke", "split_pred"])
df["split_resolved"] = df[split_col] if split_col else "all"

df["gt_pos"] = df[gt_should].apply(lambda x: int(x) == 1)
df["gt_actions"] = df[gt_action_col].apply(parse_actions)
df["pred_actions"] = df[pred_action_col].apply(parse_actions)

df["gt_type"] = df["gt_actions"].apply(top_action_type)
df["pred_type"] = df["pred_actions"].apply(top_action_type)

match = df.apply(lambda r: action_match(r["gt_actions"], r["pred_actions"]), axis=1)
df["type_correct"] = df["gt_type"] == df["pred_type"]
df["param_correct"] = [m[1] for m in match]

# ===== Metrics =====
def compute_metrics(g: pd.DataFrame) -> dict:
    fa = ((~g["gt_pos"]) & (g["pred_type"] != "none")).mean() if len(g) else float("nan")
    miss = ((g["gt_pos"]) & (g["pred_type"] == "none")).mean() if len(g) else float("nan")
    type_acc = g["type_correct"].mean() if len(g) else float("nan")
    param_acc = g[g["gt_type"] != "none"]["param_correct"].mean() if (g["gt_type"] != "none").any() else float("nan")
    return {"n": int(len(g)), "false_activation": float(fa), "miss": float(miss), "type_acc": float(type_acc), "param_acc": float(param_acc)}

overall = compute_metrics(df)

by_split = []
for sp, g in df.groupby("split_resolved"):
    d = compute_metrics(g)
    d["split"] = sp
    by_split.append(d)
by_split_df = pd.DataFrame(by_split).sort_values("split")

by_split_df.to_csv(OUT_DIR / "smoke_metrics_by_split_v8ak.csv", index=False)

by_scene = []
for sid, g in df.groupby("scene_id_resolved"):
    d = compute_metrics(g)
    d["scene_id"] = sid
    by_scene.append(d)
by_scene_df = pd.DataFrame(by_scene).sort_values("false_activation", ascending=False)

by_scene_df.to_csv(OUT_DIR / "smoke_metrics_by_scene_v8ak.csv", index=False)

gt_dist = df["gt_type"].value_counts().rename_axis("gt_type").reset_index(name="count")
pred_dist = df["pred_type"].value_counts().rename_axis("pred_type").reset_index(name="count")
gt_dist.to_csv(OUT_DIR / "smoke_gt_type_dist_v8ak.csv", index=False)
pred_dist.to_csv(OUT_DIR / "smoke_pred_type_dist_v8ak.csv", index=False)

(OUT_DIR / "smoke_metrics_overall_v8ak.json").write_text(json.dumps(overall, indent=2, ensure_ascii=False), encoding="utf-8")

print("\n[SUCCESS] Saved Artifacts:")
print(f" - {OUT_DIR / 'smoke_metrics_overall_v8ak.json'}")
print(f" - {OUT_DIR / 'smoke_metrics_by_split_v8ak.csv'}")
print(f" - {OUT_DIR / 'smoke_metrics_by_scene_v8ak.csv'}")