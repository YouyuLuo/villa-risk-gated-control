# ViLLA: Risk-Gated Control for Proactive Smart Home VLM Agents

![Status](https://img.shields.io/badge/Status-Evaluation_Artifacts-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Focus](https://img.shields.io/badge/Focus-VLM_Agent%20%7C%20Smart_Home-orange)

This repository contains **evaluation** and **demo** artifacts for **ViLLA**, a proactive smart-home agent.  
ViLLA employs a rigorous **Propose → Verify (risk-gated) → Execute** pipeline to reduce unsafe or incorrect actuations in open-ended physical environments.

> **Note**  
> This repo focuses on reproducible evaluation and auditable decision traces. To protect intellectual property pending publication, full datasets and raw videos are **not** included. Only sanitized, lightweight artifacts are provided for demonstration.

---

## ✨ Key Results (Smoke Stress-Test, n=908)

Direct execution by VLMs can lead to severe false activations in a real home. ViLLA introduces a risk-gated verification mechanism to enforce deterministic constraints and scene policies.

Evaluated using `score_smoke_v2.py`, we report three operating points:

| Setting | False Activation ↓ | Miss ↓ | Type Acc ↑ | Param Acc ↑ |
|---|---:|---:|---:|---:|
| **Direct (v8direct)** | 64.87% | 0.22% | 22.25% | 1.95% |
| **Risk-gated Balanced (v8ak)** | 0.44% | 31.61% | 67.95% | 4.89% |
| **Risk-gated Strict (v8al)** | **0.00%** | 32.49% | 67.51% | 2.28% |

**Highlight:** Risk-gating reduces false activations by **~147×** (Direct → v8ak), trading a manageable increase in "miss" rate (conservatism) for critical operational safety.

---

## 🧭 Contents

- [Quickstart](#-quickstart)
- [Demo Walkthrough](#-demo-walkthrough)
- [Repository Structure](#-repository-structure)
- [Reproducibility Notes](#-reproducibility-notes)
- [License](#-license)
- [Citation](#-citation)

---

## 🛠 Quickstart

### 1) Installation

Clone the repository and install minimal dependencies:

```bash
git clone https://github.com/<your-username>/villa-risk-gated-control.git
cd villa-risk-gated-control
pip install -r requirements.txt
```

### 2) Run Smoke Evaluation

Run the evaluation script against your prediction file (e.g., `pred_smoke.jsonl`):

```bash
bash scripts/run_eval_smoke.sh /path/to/pred_smoke.jsonl
```

The evaluator processes hard negatives and generates artifacts (the output directory is printed by the script):

- `smoke_metrics_overall_*.json`
- `smoke_metrics_by_split_*.csv`
- `smoke_metrics_by_scene_*.csv`

---

## 🎬 Demo Walkthrough

We provide a concise breakdown of ViLLA's decision-making process:

- `demo/demo_script.md`
- `demo/sample_record.json`

**Pipeline overview:** `Video → Proposal JSON → Risk-Gate Reason → Action (Execute / No-op)`

1. **Input**  
   Streams the input video clip (or clip ID) and captures the VLM’s initial proposal (`proposer_json`).

2. **Proposal**  
   The VLM identifies observations/triggers and generates candidate actions with confidence signals (e.g., `should_act`, `none_conf`).

3. **Risk-Gated Verification**  
   The core of ViLLA. The verifier checks proposals against **scene policies** and deterministic constraints.  
   *Proposing ≠ Authorizing.* We log `gate_reason`, `veto_reason`, and strict policy signals for auditability.

4. **Decision**  
   The final `pred_action_json` outputs either a validated real action **or** safely defaults to:
   ```json
   [{"type":"none"}]
   ```

---

## 📁 Repository Structure

```text
villa-risk-gated-control/
├── demo/                   # Demo scripts and sample decision traces
├── docs/                   # Documentation including the evaluation protocol
├── results/                # Generated metrics and evaluation outputs
├── scripts/                # Bash scripts for running evaluations
├── requirements.txt        # Minimal environment dependencies
└── README.md
```

---

## 🔁 Reproducibility Notes

- This repo is designed to be **audit-friendly**: decision traces are logged with explicit gate/veto reasons.
- Full datasets and raw videos are intentionally omitted; evaluation runs on provided/sanitized artifacts.
- Recommended: run in a clean Python 3.9+ environment (e.g., `venv` or `conda`) for stable dependency resolution.

---

## 📜 License

Choose a license and add it as `LICENSE` (e.g., MIT, Apache-2.0).  
If you are preparing for publication, you may want to postpone license selection until the paper is public.

---

## 📎 Citation

If you use this repository in academic work, please cite the accompanying paper:

```bibtex
@article{villa2026,
  title   = {ViLLA: Risk-Gated Control for Proactive Smart Home VLM Agents},
  author  = {Anonymous},
  year    = {2026},
  note    = {Under review}
}
```
