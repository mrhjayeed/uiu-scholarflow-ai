# AGENTS.md — UIU ScholarFlow AI

## Overview

UIU ScholarFlow AI uses a **sequential multi-agent pipeline** where each agent has a distinct, scoped responsibility. Agent outputs are passed as structured context to the next agent, enabling progressive refinement from raw unstructured input to a personalized, actionable study plan.

```
┌─────────────────────────────────────────────────────────────┐
│                  ScholarFlow Agent Pipeline                  │
│                                                              │
│  [Raw Syllabus Text]                                         │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────┐                                        │
│  │  Agent 1        │  Syllabus Parser                       │
│  │  Skill: Extract │──► Structured JSON (deliverables,      │
│  └─────────────────┘    deadlines, weights, topics)         │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────┐  + [Student Profile Input]             │
│  │  Agent 2        │                                        │
│  │  Skill: Profile │──► Priority Matrix JSON                │
│  └─────────────────┘    (urgency, difficulty, hours)        │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────┐                                        │
│  │  Agent 3        │  Study Strategist (Orchestrator)       │
│  │  Skill: Plan    │──► Day-by-day Markdown Study Plan      │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Definitions

### Agent 1 — Syllabus Parser Agent

| Property      | Value                                      |
|---------------|--------------------------------------------|
| **Role**      | Data Extraction & Normalization            |
| **Model**     | `gpt-4o-mini`                              |
| **Temp**      | `0.1` (deterministic, factual extraction)  |
| **Input**     | Unstructured text (syllabus, LMS posts, emails, PDFs) |
| **Output**    | Structured JSON: deliverables, deadlines, weights, topics |

**System Prompt Focus:**
Instructs the agent to extract ONLY structured academic metadata. Returns strict JSON with no markdown fences or explanatory text. Validates against a defined schema before passing to Agent 2.

**Design Decision:**
Temperature set to `0.1` to minimize hallucination on factual data like dates and percentages. The agent is constrained to a fixed JSON schema to ensure reliable downstream parsing by Agent 2.

---

### Agent 2 — Student Profiler Agent

| Property      | Value                                             |
|---------------|---------------------------------------------------|
| **Role**      | Weakness Analysis & Priority Scoring              |
| **Model**     | `gpt-4o-mini`                                     |
| **Temp**      | `0.2` (near-deterministic, logic-based scoring)   |
| **Input**     | Agent 1 JSON output + student self-reported text  |
| **Output**    | Priority matrix JSON with urgency & difficulty scores |

**System Prompt Focus:**
Receives the structured academic data from Agent 1 and cross-references it with the student's stated weaknesses and availability. Generates a `priority_matrix` — a scored list of topics ranked by urgency (deadline proximity × weightage) and difficulty (student self-report).

**Design Decision:**
This agent acts as the **memory layer** — it encodes student-specific context that would otherwise be lost. By scoring topics 1–10 on both urgency and difficulty, it allows Agent 3 to make data-driven scheduling decisions rather than generic suggestions.

---

### Agent 3 — Study Strategist Agent (Orchestrator)

| Property      | Value                                               |
|---------------|-----------------------------------------------------|
| **Role**      | Workflow Orchestration & Sprint Planning            |
| **Model**     | `gpt-4o-mini`                                       |
| **Temp**      | `0.7` (creative, motivating output)                 |
| **Input**     | Agent 1 JSON + Agent 2 priority matrix JSON         |
| **Output**    | Day-by-day Markdown study plan with sprint goals    |

**System Prompt Focus:**
The final orchestrator synthesizes ALL upstream context into a human-readable, motivating study plan. It is given creative latitude (higher temperature) to produce varied, engaging output while remaining grounded in the factual data from Agents 1 and 2.

**Design Decision:**
This agent operates as the "planner" in a Plan-Execute pattern. Rather than generating a generic schedule, it consults the priority matrix to allocate more time to high-urgency, high-difficulty topics and less to strong areas. It includes "Power Hour" deep work sessions specifically for weak areas flagged by Agent 2.

---

## Context Passing Strategy

Context is passed **explicitly and structurally** between agents:

```python
# Agent 1 output → Agent 2 input
parsed_data = agent_syllabus_parser(raw_syllabus)

# Agent 2 receives BOTH raw student input AND Agent 1 output
student_profile = agent_student_profiler(parsed_data, student_input)

# Agent 3 receives BOTH Agent 1 AND Agent 2 outputs
study_plan = agent_study_strategist(parsed_data, student_profile)
```

This ensures no context is lost between steps and each agent can reason about the full picture of prior work.

---

## Error Handling & Resilience

- JSON parsing includes fallback handling: if a model returns malformed JSON (e.g., with markdown fences), the pipeline strips fences before parsing.
- Each agent validates its output before passing downstream.
- The Streamlit UI catches pipeline exceptions and reports them with clear error messages.

---

## Future Agent Extensions (Roadmap)

| Agent          | Role                                               |
|----------------|----------------------------------------------------|
| Quiz Agent     | Generates self-test questions from topic summaries |
| Progress Agent | Tracks daily completion and adjusts future days    |
| Alert Agent    | Sends deadline reminders via email/WhatsApp        |
| Peer Agent     | Matches students with study partners on same course|
