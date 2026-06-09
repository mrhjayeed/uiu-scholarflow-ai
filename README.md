# UIU ScholarFlow AI 🎓

> **A multi-agent academic workflow coordinator that transforms chaotic university syllabi into personalized, optimized study plans — powered by OpenAI GPT-4o-mini.**

Built for the **Codex Community Dhaka × UIU Hackathon** · June 2026

[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI%20GPT--4o--mini-412991?style=flat-square&logo=openai)](https://platform.openai.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)](https://python.org)

---

## 🎯 The Problem

UIU students face intense trimesters with sudden assignment piles, overlapping deadlines, and complex exam schedules scattered across LMS announcements, emails, and WhatsApp messages. The cognitive load of *planning* how to study often burns as much energy as the actual studying.

**ScholarFlow removes that cognitive load entirely.**

---

## 🤖 How It Works — Multi-Agent Architecture

ScholarFlow uses a **sequential 3-agent pipeline** where each agent has a single, scoped responsibility:

```
[Raw Syllabus Text] + [Student Profile]
         │
         ▼
┌─────────────────────┐
│  Agent 1            │  ← Syllabus Parser
│  Extracts: tasks,   │    Temperature: 0.1 (factual)
│  deadlines, weights │
└──────────┬──────────┘
           │ Structured JSON
           ▼
┌─────────────────────┐
│  Agent 2            │  ← Student Profiler
│  Scores: urgency,   │    Temperature: 0.2 (analytical)
│  difficulty, hours  │
└──────────┬──────────┘
           │ Priority Matrix JSON
           ▼
┌─────────────────────┐
│  Agent 3            │  ← Study Strategist (Orchestrator)
│  Generates: day-by- │    Temperature: 0.7 (creative)
│  day study plan     │
└─────────────────────┘
           │
           ▼
  📅 Personalized Study Plan (Markdown)
```

See [`AGENTS.md`](./AGENTS.md) for full agent architecture details.
See [`skills.md`](./skills.md) for skill definitions and I/O schemas.

---

## ✨ Key Features

- **🧠 3-Agent Pipeline** — Syllabus Parser → Student Profiler → Study Strategist
- **📊 Priority Matrix** — Topics scored by urgency (deadline × weight) and difficulty (student self-report)
- **⚡ Power Hour Sessions** — Deep work blocks auto-scheduled for weak, high-stakes topics
- **📅 Day-by-Day Plan** — Concrete daily schedule with checkpoints and self-test prompts
- **⬇️ Export to Markdown** — Download your plan for Notion, Obsidian, or offline use
- **🎨 Premium UI** — Dark glassmorphism interface with live agent status monitoring

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/uiu-scholarflow-ai.git
cd uiu-scholarflow-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 4a. Run the Web UI (Recommended)

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 4b. Run the CLI Version

```bash
python main.py
```

---

## 🏗️ Project Structure

```
uiu-scholarflow-ai/
├── main.py          # Core multi-agent pipeline (CLI)
├── app.py           # Streamlit web interface
├── AGENTS.md        # Agent architecture documentation
├── skills.md        # Agent skills & I/O schema definitions
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## 🔧 OpenAI Integration Details

| Component             | OpenAI Feature Used                        |
|-----------------------|--------------------------------------------|
| Syllabus Parser Agent | `chat.completions.create` · GPT-4o-mini · Structured JSON output · Temp 0.1 |
| Student Profiler Agent| `chat.completions.create` · GPT-4o-mini · Priority scoring · Temp 0.2 |
| Study Strategist Agent| `chat.completions.create` · GPT-4o-mini · Markdown generation · Temp 0.7 |
| Context Passing       | Explicit structured JSON chaining between agent calls |

**Why GPT-4o-mini?**
- Fast inference for a responsive UX during hackathon demos
- Cost-effective for iterative testing
- Excellent instruction-following for structured JSON extraction
- Strong enough for nuanced planning and motivational content

---

## 💡 Sample Input / Output

**Input (Syllabus):**
```
CSE 3111 — Operating Systems
Assignment 1: Process Scheduling — due June 14 (10%)
Midterm Exam: June 22 — Chapters 1–6 (30%)
```

**Input (Student Profile):**
```
I struggle with CPU Scheduling (SJF, Round Robin calculations).
I can study 4 hours/day. Midterm in 12 days.
```

**Output (Agent 3):**
```markdown
## 📋 Executive Summary
With 12 days until your midterm (30%), your #1 priority is CPU
Scheduling — your weakest area with the highest urgency score (9/10).

## 📅 Day-by-Day Sprint Plan

**Day 1 (Today) — Foundation Reset**
⏰ Power Hour (2h): CPU Scheduling — FCFS & SJF calculations
📖 Review (1h): Process & Thread fundamentals
✅ Checkpoint: Solve 5 FCFS Gantt chart problems from scratch
...
```

---

## 🏆 Impact

- **Who benefits:** UIU students (and any university student) overwhelmed by academic planning
- **Problem solved:** Converts chaotic, multi-source academic information into an actionable sprint plan in under 30 seconds
- **Scalability:** Works for any course, any university, any deadline structure

---

## 👨‍💻 Built By

Submitted to the **Codex Community Dhaka × UIU Hackathon** (June 2026)
Category: **Education & Learning / AI Agents**

---

## 📄 License

MIT License — free to use, modify, and distribute.
