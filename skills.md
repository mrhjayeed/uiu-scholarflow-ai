# skills.md — Agent Skills Definitions

> This document defines the discrete skills (capabilities) available in the UIU ScholarFlow AI agent system. Each skill maps to a specific agent and describes its inputs, outputs, and implementation approach.

---

## Skill Registry

### `syllabus.parse`

| Property      | Value                                              |
|---------------|----------------------------------------------------|
| **Agent**     | Agent 1 — Syllabus Parser                         |
| **Model**     | `gpt-4o-mini`                                      |
| **Type**      | Data Extraction                                    |

**Description:**
Converts unstructured academic text (syllabus PDFs, LMS announcements, emails, WhatsApp messages from course coordinators) into a normalized JSON structure with typed fields.

**Input:**
```
Any free-form text containing academic schedule information:
- Course codes and names
- Assignment titles and descriptions
- Due dates (in any format: "next Thursday", "June 14", "Week 6")
- Grade weightages (percentages, marks)
- Exam dates and coverage
```

**Output Schema:**
```json
{
  "course_name": "string",
  "course_code": "string",
  "deliverables": [
    {
      "type": "assignment|quiz|midterm|final|project|presentation",
      "title": "string",
      "deadline": "YYYY-MM-DD or descriptive string",
      "weight_percent": 10,
      "topics": ["string"]
    }
  ],
  "total_weeks": 14,
  "key_topics": ["string"]
}
```

**Capability Notes:**
- Handles relative dates ("next week", "in 3 days")
- Extracts implicit weightages ("worth 10 marks out of 100")
- Identifies topic coverage from descriptive text
- Normalizes inconsistent formatting (mixed cases, abbreviations)

---

### `student.profile`

| Property      | Value                                              |
|---------------|----------------------------------------------------|
| **Agent**     | Agent 2 — Student Profiler                        |
| **Model**     | `gpt-4o-mini`                                      |
| **Type**      | Analysis & Scoring                                 |

**Description:**
Cross-references structured course data with a student's self-reported weaknesses and schedule to generate a priority-scored topic matrix. This is the **memory encoding** step of the pipeline.

**Input:**
```
1. Structured syllabus JSON from Agent 1
2. Student free-text input:
   - Self-reported weak topics ("I struggle with SJF")
   - Self-reported strong topics ("I'm okay with processes")
   - Daily study availability ("3-4 hours on weekdays")
   - Contextual urgency ("midterm in 12 days")
```

**Output Schema:**
```json
{
  "student_profile": {
    "weak_areas": ["CPU Scheduling", "Deadlock Detection"],
    "strong_areas": ["Process Concepts", "File Systems"],
    "available_hours_per_day": 3.5
  },
  "priority_matrix": [
    {
      "topic": "CPU Scheduling",
      "urgency_score": 9,
      "difficulty_score": 8,
      "recommended_hours": 6,
      "rationale": "High exam weightage + midterm in 12 days + student weakness"
    }
  ]
}
```

**Scoring Algorithm:**
- **Urgency Score (1–10):** Calculated from deadline proximity × weightage percentage
- **Difficulty Score (1–10):** Derived from student self-report (weak = high, strong = low)
- **Recommended Hours:** Proportional allocation from total available study time

---

### `workflow.orchestrate`

| Property      | Value                                              |
|---------------|----------------------------------------------------|
| **Agent**     | Agent 3 — Study Strategist                        |
| **Model**     | `gpt-4o-mini`                                      |
| **Type**      | Planning & Orchestration                           |

**Description:**
The core orchestration skill. Takes all prior agent outputs and synthesizes a concrete, human-readable study plan with daily schedules, Power Hour sessions, and self-test checkpoints.

**Input:**
```
1. Structured syllabus JSON from Agent 1
2. Student profile + priority matrix JSON from Agent 2
```

**Output:**
```markdown
A full Markdown document containing:
- Executive summary (2-3 sentences)
- Day-by-day schedule until next major deadline
- Power Hour sessions for high-difficulty topics
- Daily checkpoints and self-test prompts
- Sprint Mantra (motivational closing)
```

**Planning Heuristics:**
- Topics with `urgency_score >= 8` AND `difficulty_score >= 7` get dedicated "Power Hour" blocks
- Strong areas get review-only sessions (30–45 min), not deep dives
- Weekends get allocated for high-cognitive tasks (problem sets, practice exams)
- Day before exam: review and rest only, no new material

---

### `plan.download`

| Property      | Value                                              |
|---------------|----------------------------------------------------|
| **Agent**     | UI Layer (Streamlit)                              |
| **Type**      | Output & Export                                    |

**Description:**
Exports the generated study plan as a downloadable Markdown file for offline use, sharing with study groups, or import into note-taking apps (Notion, Obsidian).

**Input:** Generated Markdown string from Agent 3
**Output:** `.md` file download in browser

---

## Skill Execution Flow

```
User Input
    │
    ▼
[syllabus.parse]  ─────────────────────────────────────────┐
    │ Structured JSON                                       │
    ▼                                                       │
[student.profile] ◄── User Profile Text                    │
    │ Priority Matrix JSON                                  │
    ▼                                                       │
[workflow.orchestrate] ◄──────────────────────────────────┘
    │ Markdown Study Plan
    ▼
[plan.download]
    │ .md File
    ▼
User
```

---

## Skill Design Principles

1. **Single Responsibility** — Each skill does exactly one thing well.
2. **Structured I/O** — JSON in, JSON out for machine-readable steps; Markdown only at the human-facing output layer.
3. **Temperature Discipline** — Factual extraction: low temp (0.1); analytical scoring: medium-low temp (0.2); creative planning: medium temp (0.7).
4. **Graceful Degradation** — If JSON parsing fails, raw text fallback prevents full pipeline failure.
5. **Context Accumulation** — Each downstream skill receives all prior context, not just the immediate predecessor's output.
