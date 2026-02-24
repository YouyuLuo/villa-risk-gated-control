# ViLLA Decision Chain Analysis: How to Prevent a "Catastrophic" False Activation?

This script is based on real evaluation data from `sample_record.json`. It demonstrates how ViLLA ensures system reliability through the **Risk-Gated** mechanism when facing deceptive scenarios.

## Scene Reconstruction (Scene: BR01)
* **Input Video**: Bedroom scene (`BR01`).
* **Ground Truth**: The user is lying on the bed covered with a blanket using a phone (`phone_scrolling`).
* **Available Devices**: Curtain (`curtain`), desk lamp (`desk_lamp`).

## Phase 1: VLM Proposal
In this phase, the VLM acts as an "observer" and "proposer". It tends to easily overreact.
* **Observation**: "A person is lying on a bed with a blanket, using a phone."
* **Rationale**: The VLM infers that using a phone while lying in bed is bad for the eyes, determining the lighting is too dim (`too_dark: true`) and poses a hazard (`hazard: true`).
* **Dangerous Candidates**: The VLM strongly recommends turning on the desk lamp (`desk_lamp` brightness 50) with a high confidence score of **0.8**.

> **⚠️ Pain Point**: If an end-to-end Direct Execution approach is used, the desk lamp would suddenly turn on, severely disturbing the user who is trying to sleep or resting. This is exactly why the Direct mode has a high false activation rate of 64.87%.

## Phase 2: Risk-Gated Verification
This is the core line of defense for ViLLA. The system does not blindly follow the VLM.
* The system extracts the current physical sensor states and predefined room policies (`policy_signals`).
* Through rigorous Neuro-Symbolic logical comparison, it finds that the current physical environment does not meet the hard metrics for `too_dark`, and scrolling on a phone is insufficient to trigger the `hazard` emergency protocol.
* **Gating Result**: Triggers `gate_reason: "reject_all"`, completely vetoing the VLM's proposal.

## Phase 3: Final Execution
* **Pred Action**: `[{"type": "none", "param": {}}]`
* **Result**: The system remains silent. It successfully intercepts a False Activation, with the entire decision chain taking only 5.62 seconds.

**Summary**: By decoupling "proposal" and "authorization," ViLLA introduces a deterministic safety lower bound while retaining the generalization capabilities of large models.
