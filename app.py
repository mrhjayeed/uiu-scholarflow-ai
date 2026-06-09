"""
UIU ScholarFlow AI — Streamlit Web Interface
============================================
A premium, interactive web UI for the multi-agent academic coordinator.
Run with: streamlit run app.py
"""

import os
import json
import time
import streamlit as st
from main import agent_syllabus_parser, agent_student_profiler, agent_study_strategist

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UIU ScholarFlow AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1321 50%, #0a1628 100%);
    color: #e2e8f0;
}

/* Hero Header */
.hero-header {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.15) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
    text-align: center;
}

.hero-header h1 {
    background: linear-gradient(135deg, #818cf8, #c084fc, #fb7185);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}

.hero-header p {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

/* Agent Cards */
.agent-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.agent-card.active {
    border-color: rgba(99,102,241,0.7);
    box-shadow: 0 0 20px rgba(99,102,241,0.2);
}

.agent-card.done {
    border-color: rgba(52,211,153,0.5);
    box-shadow: 0 0 15px rgba(52,211,153,0.1);
}

.agent-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Plan output */
.plan-container {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 0 40px rgba(52,211,153,0.05);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(10, 14, 26, 0.95) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 25px rgba(99,102,241,0.45) !important;
}

/* Textareas */
.stTextArea textarea {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Metric cards */
.metric-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
}

.metric-number {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.metric-label {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.25rem;
}

/* Progress bar */
.progress-bar {
    background: rgba(99,102,241,0.15);
    border-radius: 999px;
    height: 6px;
    margin-top: 0.5rem;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    transition: width 0.5s ease;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─── Hero Header ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-header">
    <h1>🎓 UIU ScholarFlow AI</h1>
    <p>Multi-Agent Academic Workflow Coordinator · Powered by OpenAI GPT-4o-mini</p>
</div>
""",
    unsafe_allow_html=True,
)

# ─── Sidebar — Agent Monitor ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Agent Pipeline Monitor")
    st.markdown("---")

    agent_status = st.session_state.get("agent_status", {1: "idle", 2: "idle", 3: "idle"})

    status_icons = {"idle": "⬜", "running": "🔄", "done": "✅", "error": "❌"}
    status_colors = {
        "idle": "#475569",
        "running": "#f59e0b",
        "done": "#34d399",
        "error": "#f87171",
    }

    agents_info = [
        (1, "Syllabus Parser", "Data Extraction & Normalization"),
        (2, "Student Profiler", "Gap Analysis & Priority Scoring"),
        (3, "Study Strategist", "Workflow Orchestration"),
    ]

    for agent_id, name, skill in agents_info:
        status = agent_status.get(agent_id, "idle")
        icon = status_icons[status]
        color = status_colors[status]
        st.markdown(
            f"""
            <div style="background: rgba(15,23,42,0.6); border: 1px solid {color}33;
                        border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">
                    <span style="font-size:1.1rem">{icon}</span>
                    <strong style="color:#e2e8f0; font-size:0.9rem">Agent {agent_id}: {name}</strong>
                </div>
                <div style="color:#64748b; font-size:0.78rem">{skill}</div>
                <div style="color:{color}; font-size:0.78rem; font-weight:600; margin-top:0.4rem; text-transform:uppercase; letter-spacing:0.5px">
                    {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### ⚙️ Model Config")
    st.markdown(
        """
        <div style="background:rgba(15,23,42,0.6); border-radius:10px; padding:0.9rem;">
            <div style="color:#818cf8; font-weight:600; font-size:0.85rem">Model</div>
            <div style="color:#e2e8f0; font-family:'JetBrains Mono'; font-size:0.85rem">gpt-4o-mini</div>
            <div style="color:#818cf8; font-weight:600; font-size:0.85rem; margin-top:0.6rem">Architecture</div>
            <div style="color:#e2e8f0; font-size:0.85rem">Sequential Multi-Agent</div>
            <div style="color:#818cf8; font-weight:600; font-size:0.85rem; margin-top:0.6rem">Context Passing</div>
            <div style="color:#34d399; font-size:0.85rem">✓ Chained (A1 → A2 → A3)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Main Input Area ─────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### 📋 Course Syllabus / Assignment Details")
    st.markdown(
        '<span style="color:#64748b; font-size:0.875rem">Paste your course outline, assignment details, exam schedule — anything from your LMS or syllabus PDF.</span>',
        unsafe_allow_html=True,
    )
    syllabus_input = st.text_area(
        label="Syllabus Input",
        label_visibility="collapsed",
        height=280,
        placeholder="""Example:
Course: CSE 3111 — Operating Systems
Instructor: Dr. Tanvir Ahmed

Deliverables:
- Assignment 1: Process Scheduling — due June 14 (10%)
- Assignment 2: Memory Management — due June 21 (10%)
- Quiz 1: June 12, Chapters 1–3 (5%)
- Midterm Exam: June 22 — all Chapters 1–6 (30%)
- Final Project: Implement a simple shell — July 10 (15%)
- Final Exam: July 20 (25%)

Key Topics: Processes, CPU Scheduling, Synchronization,
Memory Management, File Systems, I/O Systems""",
        value=st.session_state.get("demo_syllabus", ""),
    )

with col2:
    st.markdown("#### 🧑‍🎓 Your Profile & Weak Areas")
    st.markdown(
        '<span style="color:#64748b; font-size:0.875rem">Describe your weak topics, how many hours you can study per day, and your nearest exam date.</span>',
        unsafe_allow_html=True,
    )
    student_input = st.text_area(
        label="Student Profile Input",
        label_visibility="collapsed",
        height=280,
        placeholder="""Example:
I struggle with CPU Scheduling algorithms — calculating
turnaround time and waiting time for SJF and Round Robin
is really confusing. Deadlock detection is also hard.

I'm okay with Process concepts and File Systems basics.

I can study 3–4 hours on weekdays, 5–6 hours on weekends.
My midterm is in 12 days. I really need to pass this one.""",
        value=st.session_state.get("demo_student", ""),
    )

# ─── Quick Fill Demo Button ───────────────────────────────────────────────────
col_fill, col_run, col_clear = st.columns([1, 1, 1])

DEMO_SYLLABUS = """Course: CSE 3111 — Operating Systems
Instructor: Dr. Tanvir Ahmed | UIU Spring 2026

Deliverables:
- Assignment 1: Process Scheduling — due June 14, 2026 (10%)
- Assignment 2: Memory Management — due June 21, 2026 (10%)
- Quiz 1: June 12, 2026, Chapters 1–3 (5%)
- Quiz 2: June 19, 2026, Chapters 4–6 (5%)
- Midterm Exam: June 22, 2026 — Chapters 1–6 (30%)
- Final Project: Implement a simple shell — due July 10, 2026 (15%)
- Final Exam: July 20, 2026 — all chapters (25%)

Key Topics: Processes and Threads, CPU Scheduling (FCFS, SJF, Round Robin, Priority),
Synchronization (Mutex, Semaphores, Deadlock), Memory Management (Paging, Segmentation,
Virtual Memory), File Systems, I/O Systems"""

DEMO_STUDENT = """I struggle badly with CPU Scheduling algorithms, especially calculating
turnaround time and waiting time for SJF and Round Robin. Deadlock detection
and avoidance (Banker's Algorithm) is also confusing. I am okay with Process
concepts and File Systems.

I can study about 3–4 hours per day on weekdays and 5–6 hours on weekends.
My midterm is in 12 days. This is worth 30% so I really need to focus."""

with col_fill:
    if st.button("⚡ Load Demo Data", use_container_width=True, key="btn_demo"):
        st.session_state["demo_syllabus"] = DEMO_SYLLABUS
        st.session_state["demo_student"] = DEMO_STUDENT
        st.rerun()

with col_run:
    run_btn = st.button("🚀 Generate My ScholarFlow Plan", use_container_width=True, type="primary", key="btn_run")

with col_clear:
    if st.button("🗑️ Clear", use_container_width=True, key="btn_clear"):
        for key in ["demo_syllabus", "demo_student", "result", "agent_status"]:
            st.session_state.pop(key, None)
        st.rerun()

# ─── Pipeline Execution ───────────────────────────────────────────────────────
if run_btn:
    syllabus_val = syllabus_input or st.session_state.get("demo_syllabus", "")
    student_val = student_input or st.session_state.get("demo_student", "")

    if not syllabus_val.strip() or not student_val.strip():
        st.error("⚠️ Please fill in both the syllabus and your profile before running.")
    else:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            st.error("⚠️ `OPENAI_API_KEY` environment variable not set. Please set it and restart.")
        else:
            st.session_state["agent_status"] = {1: "idle", 2: "idle", 3: "idle"}

            st.markdown("---")
            st.markdown("### 🔄 Agent Pipeline Running...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Agent 1
                st.session_state["agent_status"] = {1: "running", 2: "idle", 3: "idle"}
                status_text.markdown(
                    "🤖 **Agent 1 — Syllabus Parser:** Extracting structured data..."
                )
                progress_bar.progress(10)
                parsed_data = agent_syllabus_parser(syllabus_val)
                progress_bar.progress(33)
                st.session_state["agent_status"] = {1: "done", 2: "idle", 3: "idle"}

                # Agent 2
                st.session_state["agent_status"] = {1: "done", 2: "running", 3: "idle"}
                status_text.markdown(
                    "🤖 **Agent 2 — Student Profiler:** Analyzing gaps and priorities..."
                )
                progress_bar.progress(40)
                student_profile = agent_student_profiler(parsed_data, student_val)
                progress_bar.progress(66)
                st.session_state["agent_status"] = {1: "done", 2: "done", 3: "idle"}

                # Agent 3
                st.session_state["agent_status"] = {1: "done", 2: "done", 3: "running"}
                status_text.markdown(
                    "🤖 **Agent 3 — Study Strategist:** Orchestrating your personalized plan..."
                )
                progress_bar.progress(75)
                study_plan = agent_study_strategist(parsed_data, student_profile)
                progress_bar.progress(100)
                st.session_state["agent_status"] = {1: "done", 2: "done", 3: "done"}

                status_text.markdown("✅ **Pipeline complete! Your ScholarFlow plan is ready.**")

                st.session_state["result"] = {
                    "parsed_syllabus": parsed_data,
                    "student_profile": student_profile,
                    "study_plan": study_plan,
                }

            except Exception as e:
                st.error(f"❌ Pipeline error: {e}")
                st.session_state["agent_status"] = {1: "error", 2: "error", 3: "error"}

            st.rerun()

# ─── Results Display ──────────────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]

    st.markdown("---")
    st.markdown(
        '<h2 style="background:linear-gradient(135deg,#34d399,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700">✨ Your ScholarFlow Study Plan</h2>',
        unsafe_allow_html=True,
    )

    # Metrics row
    parsed = result.get("parsed_syllabus", {})
    profile = result.get("student_profile", {})
    deliverables = parsed.get("deliverables", [])
    weak_areas = profile.get("student_profile", {}).get("weak_areas", [])
    priority_matrix = profile.get("priority_matrix", [])
    hours = profile.get("student_profile", {}).get("available_hours_per_day", "—")

    m1, m2, m3, m4 = st.columns(4)
    for col, num, label in [
        (m1, len(deliverables), "Deliverables Found"),
        (m2, len(weak_areas), "Weak Areas Flagged"),
        (m3, len(priority_matrix), "Topics Prioritized"),
        (m4, f"{hours}h", "Study Hours/Day"),
    ]:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">{num}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Study plan
    tab1, tab2, tab3 = st.tabs(
        ["📅 Study Plan", "📊 Priority Matrix", "🗂️ Parsed Syllabus"]
    )

    with tab1:
        st.markdown(
            '<div class="plan-container">',
            unsafe_allow_html=True,
        )
        st.markdown(result["study_plan"])
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        if priority_matrix:
            import pandas as pd

            df = pd.DataFrame(priority_matrix)
            st.dataframe(
                df,
                width="stretch",
                column_config={
                    "topic": "📚 Topic",
                    "urgency_score": st.column_config.ProgressColumn(
                        "🔥 Urgency", min_value=0, max_value=10
                    ),
                    "difficulty_score": st.column_config.ProgressColumn(
                        "💪 Difficulty", min_value=0, max_value=10
                    ),
                    "recommended_hours": st.column_config.NumberColumn(
                        "⏱️ Hours", format="%g h"
                    ),
                    "rationale": "💡 Rationale",
                },
                hide_index=True,
            )
        else:
            st.json(profile)

    with tab3:
        st.json(parsed)

    # Download plan
    st.download_button(
        label="⬇️ Download Study Plan (Markdown)",
        data=result["study_plan"],
        file_name="scholarflow_plan.md",
        mime="text/markdown",
    )

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center; color:#334155; font-size:0.8rem; margin-top:3rem; padding-top:1.5rem; border-top:1px solid rgba(99,102,241,0.1)">
    UIU ScholarFlow AI · Built for Codex Community Dhaka Hackathon · Powered by OpenAI GPT-4o-mini
</div>
""",
    unsafe_allow_html=True,
)
