"""
UIU ScholarFlow AI — Multi-Agent Academic Workflow Coordinator
==============================================================
A sequential multi-agent system that parses university syllabi and
orchestrates personalized, optimized study plans for UIU students.

Agents:
  1. Syllabus Parser Agent  — Extracts tasks, deadlines, weightages
  2. Student Profiler Agent — Identifies weak areas & learning style
  3. Study Strategist Agent — Orchestrates final day-by-day study plan
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file if present (works locally and in Streamlit)
load_dotenv()

MODEL = "gpt-4o-mini"


def _get_client() -> OpenAI:
    """Lazily create the OpenAI client so imports never fail."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file or export it as an environment variable."
        )
    return OpenAI(api_key=api_key)

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1 — Syllabus Parser Agent
# Skill: Data Extraction & Normalization
# ─────────────────────────────────────────────────────────────────────────────
def agent_syllabus_parser(raw_syllabus: str) -> dict:
    """
    Extracts structured academic data from raw syllabus text.
    Returns a clean JSON object with assignments, exams, and deadlines.
    """
    print("\n🤖 [Agent 1 — Syllabus Parser] Extracting structured data...")

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the Syllabus Parser Agent. Your ONLY job is to extract "
                    "structured academic data from unstructured text. Parse the input and "
                    "return a valid JSON object with the following schema:\n\n"
                    "{\n"
                    '  "course_name": "string",\n'
                    '  "course_code": "string",\n'
                    '  "deliverables": [\n'
                    '    {\n'
                    '      "type": "assignment|quiz|midterm|final|project|presentation",\n'
                    '      "title": "string",\n'
                    '      "deadline": "YYYY-MM-DD or descriptive string",\n'
                    '      "weight_percent": number,\n'
                    '      "topics": ["string"]\n'
                    '    }\n'
                    '  ],\n'
                    '  "total_weeks": number,\n'
                    '  "key_topics": ["string"]\n'
                    "}\n\n"
                    "Return ONLY the JSON, no markdown fences, no explanation."
                ),
            },
            {"role": "user", "content": raw_syllabus},
        ],
        temperature=0.1,
    )

    raw_json = response.choices[0].message.content.strip()
    # Strip markdown fences if model added them anyway
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError:
        parsed = {"raw": raw_json}

    print(f"  ✅ Extracted {len(parsed.get('deliverables', []))} deliverables.")
    return parsed


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2 — Student Profiler Agent
# Skill: Weakness Analysis & Priority Scoring
# ─────────────────────────────────────────────────────────────────────────────
def agent_student_profiler(parsed_data: dict, student_input: str) -> dict:
    """
    Analyzes student weaknesses against extracted syllabus data.
    Produces a priority-scored topic matrix.
    """
    print("\n🤖 [Agent 2 — Student Profiler] Analyzing gaps & priorities...")

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the Student Profiler Agent. Given structured syllabus data "
                    "and the student's self-reported weaknesses and schedule, produce a "
                    "priority-scored study matrix as JSON:\n\n"
                    "{\n"
                    '  "student_profile": {\n'
                    '    "weak_areas": ["string"],\n'
                    '    "strong_areas": ["string"],\n'
                    '    "available_hours_per_day": number\n'
                    "  },\n"
                    '  "priority_matrix": [\n'
                    '    {\n'
                    '      "topic": "string",\n'
                    '      "urgency_score": 1-10,\n'
                    '      "difficulty_score": 1-10,\n'
                    '      "recommended_hours": number,\n'
                    '      "rationale": "string"\n'
                    '    }\n'
                    '  ]\n'
                    "}\n\n"
                    "Return ONLY the JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Syllabus Data:\n{json.dumps(parsed_data, indent=2)}\n\n"
                    f"Student Input:\n{student_input}"
                ),
            },
        ],
        temperature=0.2,
    )

    raw_json = response.choices[0].message.content.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
    try:
        profile = json.loads(raw_json)
    except json.JSONDecodeError:
        profile = {"raw": raw_json}

    topics = profile.get("priority_matrix", [])
    print(f"  ✅ Profiled {len(topics)} topics with urgency scores.")
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3 — Study Strategist Agent (Orchestrator)
# Skill: Workflow Orchestration & Sprint Planning
# ─────────────────────────────────────────────────────────────────────────────
def agent_study_strategist(parsed_data: dict, student_profile: dict) -> str:
    """
    Orchestrates all previous agent outputs into a concrete,
    day-by-day personalized study plan with sprint goals.
    """
    print("\n🤖 [Agent 3 — Study Strategist] Orchestrating study workflow...")

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the Study Strategist Agent — the final orchestrator of the "
                    "UIU ScholarFlow system. You receive structured syllabus data and a "
                    "student priority matrix. Your job is to synthesize everything into "
                    "a concrete, motivating, day-by-day study sprint plan in Markdown.\n\n"
                    "Requirements:\n"
                    "- Start with a quick executive summary (2-3 sentences)\n"
                    "- Create a day-by-day schedule covering up to the nearest major deadline\n"
                    "- Use emojis for visual clarity\n"
                    "- Include 'Power Hour' deep work sessions for weak areas\n"
                    "- Add daily checkpoints and self-test prompts\n"
                    "- End with a motivational 'Sprint Mantra' section\n"
                    "- Keep it realistic and achievable\n"
                    "Format as clean, readable Markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Syllabus Data:\n{json.dumps(parsed_data, indent=2)}\n\n"
                    f"Student Profile & Priority Matrix:\n{json.dumps(student_profile, indent=2)}"
                ),
            },
        ],
        temperature=0.7,
    )

    plan = response.choices[0].message.content.strip()
    print("  ✅ Study workflow orchestrated successfully.")
    return plan


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATION PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
def run_scholar_flow(raw_syllabus: str, student_input: str) -> dict:
    """
    Main pipeline: runs all 3 agents in sequence, passing context forward.
    Returns a dict with all intermediate and final outputs.
    """
    print("\n" + "=" * 60)
    print("  🎓 UIU ScholarFlow AI — Starting Agent Pipeline")
    print("=" * 60)

    # Agent 1 → parse syllabus
    parsed_data = agent_syllabus_parser(raw_syllabus)

    # Agent 2 → profile student (receives Agent 1 output)
    student_profile = agent_student_profiler(parsed_data, student_input)

    # Agent 3 → orchestrate final plan (receives both Agent 1 & 2 outputs)
    study_plan = agent_study_strategist(parsed_data, student_profile)

    print("\n" + "=" * 60)
    print("  ✨ Pipeline Complete! Your ScholarFlow plan is ready.")
    print("=" * 60)

    return {
        "parsed_syllabus": parsed_data,
        "student_profile": student_profile,
        "study_plan": study_plan,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEMO / CLI ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_syllabus = """
    Course: CSE 3111 — Operating Systems
    Instructor: Dr. Tanvir Ahmed
    UIU Spring 2026

    Deliverables:
    - Assignment 1: Process Scheduling — due June 14, 2026 (10%)
    - Assignment 2: Memory Management — due June 21, 2026 (10%)
    - Quiz 1: June 12, 2026, Chapters 1–3 (5%)
    - Quiz 2: June 19, 2026, Chapters 4–6 (5%)
    - Midterm Exam: June 22, 2026 — Chapters 1–6 (30%)
    - Final Project: Implement a simple shell — due July 10, 2026 (15%)
    - Final Exam: July 20, 2026 — all chapters (25%)

    Key Topics:
    1. Process and Threads
    2. CPU Scheduling (FCFS, SJF, Round Robin, Priority)
    3. Synchronization (Mutex, Semaphores, Deadlock)
    4. Memory Management (Paging, Segmentation, Virtual Memory)
    5. File Systems
    6. I/O Systems
    """

    sample_student_input = """
    I struggle badly with CPU Scheduling algorithms, especially calculating
    turnaround time and waiting time for SJF and Round Robin. Deadlock detection
    is also confusing. I am okay with Process concepts and File Systems.
    I can study about 3–4 hours per day on weekdays and 5–6 hours on weekends.
    My midterm is in 12 days.
    """

    result = run_scholar_flow(sample_syllabus, sample_student_input)

    print("\n\n╔══════════════════════════════════════════════════╗")
    print("║         YOUR SCHOLARFLOW STUDY PLAN             ║")
    print("╚══════════════════════════════════════════════════╝\n")
    print(result["study_plan"])
