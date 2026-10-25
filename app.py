"""Streamlit Web Application for LangGraph Candidate Matching Agent.
Provides an interactive conversational UI, multi-round screening visualizer,
side-by-side candidate comparison, interview question generator, and state machine graph.
"""

import streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components

from matching_agent import MatchingAgent
from tools.filesystem_tools import read_job_description, list_resumes
from tools.agent_tools import compare_candidates, generate_interview_questions

st.set_page_config(
    page_title="Candidate Matching Agent | LangGraph",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-hire { background-color: #DCFCE7; color: #166534; }
    .badge-strong { background-color: #BBF7D0; color: #14532D; font-weight: 700; }
    .badge-borderline { background-color: #FEF9C3; color: #854D0E; }
    .badge-nohire { background-color: #FEE2E2; color: #991B1B; }
    .card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "agent" not in st.session_state:
    st.session_state.agent = MatchingAgent()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hello! I am your **LangGraph Candidate Matching Agent**.\n\nI have screened **100 candidate resumes** against the current job requirements and identified the top matches. You can ask me natural language questions, compare candidates, ask why one candidate ranked higher than another, or adjust criteria mid-conversation!"}
    ]

agent: MatchingAgent = st.session_state.agent
state = agent.state
reqs = state.get("requirements", {})

# ==========================================
# Sidebar: Configuration & State Inspector
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.title("Recruitment Control")
    
    st.subheader("📋 Job Description")
    jd_options = {
        "Senior React Developer": "senior_react_developer",
        "Full Stack Cloud Engineer": "fullstack_cloud_engineer",
        "AI / ML Engineer": "ml_ai_engineer"
    }
    selected_jd_label = st.selectbox("Select Preset JD:", list(jd_options.keys()))
    
    if st.button("🔄 Reload & Re-Screen Candidates"):
        raw_jd = read_job_description(jd_options[selected_jd_label])
        st.session_state.agent = MatchingAgent(default_jd=raw_jd)
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"🔄 Reloaded and re-screened candidate pool for **{selected_jd_label}**."}
        ]
        st.rerun()

    st.divider()
    st.subheader("🔍 Active Agent State")
    st.write(f"**Target Role:** {reqs.get('job_title', 'Software Engineer')}")
    st.write(f"**Min Experience:** {reqs.get('min_years_experience', 3.0)}+ years")
    
    with st.expander("Must-Have Skills", expanded=True):
        for s in reqs.get("must_have_skills", []):
            st.markdown(f"- `{s}`")
            
    with st.expander("Nice-to-Have Skills", expanded=False):
        for s in reqs.get("nice_to_have_skills", []):
            st.markdown(f"- `{s}`")

    st.caption("Agent powered by **LangGraph** & **RAG Retrieval**")

# ==========================================
# Main Header
# ==========================================
st.markdown('<div class="main-header">🤖 Autonomous Candidate Matching Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Round Screening (100 → 10 → Hire/No-Hire) | Explainable Match Reasoning | Iterative Refinement</div>', unsafe_allow_html=True)

# Funnel KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Round 1: Initial Corpus", "100 Resumes", "RAG Indexed")
with col2:
    st.metric("Round 2: Shortlist Pool", f"{len(state.get('shortlisted_candidates', []))} Candidates", "Deep Analysis")
with col3:
    strong_hires = sum(1 for c in state.get('shortlisted_candidates', []) if "Hire" in c.get('recommendation', '') and "No" not in c.get('recommendation', ''))
    st.metric("Round 3: Hire Recommendations", f"{strong_hires} Candidates", "Recommended")
with col4:
    top_score = state.get('shortlisted_candidates', [{}])[0].get('composite_score', 0) if state.get('shortlisted_candidates') else 0
    st.metric("Top Candidate Score", f"{top_score} / 100", state.get('shortlisted_candidates', [{}])[0].get('name', 'N/A'))

# ==========================================
# Application Tabs
# ==========================================
tab_chat, tab_leaderboard, tab_compare, tab_questions, tab_graph = st.tabs([
    "💬 Conversational Agent",
    "📊 Multi-Round Leaderboard",
    "⚖️ Side-by-Side Comparator",
    "❓ Interview Screening Studio",
    "🔄 State Machine Architecture"
])

# ------------------------------------------
# TAB 1: Conversational Agent
# ------------------------------------------
with tab_chat:
    st.subheader("Natural Language Interaction & Feedback Loop")
    
    # Suggested Prompts
    st.write("**💡 Quick Queries (Click to Run):**")
    p_cols = st.columns(5)
    sample_queries = [
        "Find me candidates with React and 3+ years experience",
        "Compare the top 3 matches side by side",
        "Why did John rank higher than Jane?",
        "Adjust requirements: require 5+ years experience and AWS knowledge",
        "Generate interview questions for John Doe"
    ]
    
    clicked_prompt = None
    for idx, (p_col, q_text) in enumerate(zip(p_cols, sample_queries)):
        with p_col:
            if st.button(f"Prompt {idx+1}", help=q_text, use_container_width=True):
                clicked_prompt = q_text

    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Box
    user_input = st.chat_input("Ask a question, adjust requirements, or query candidate comparisons...")
    
    active_query = clicked_prompt or user_input
    if active_query:
        # Append User Message
        st.session_state.chat_history.append({"role": "user", "content": active_query})
        with st.chat_message("user"):
            st.markdown(active_query)

        # Agent Execution
        with st.chat_message("assistant"):
            with st.spinner("Agent is reasoning and querying candidate state..."):
                agent_reply = agent.handle_natural_query(active_query)
                st.markdown(agent_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": agent_reply})
        st.rerun()

# ------------------------------------------
# TAB 2: Multi-Round Leaderboard & Explainability
# ------------------------------------------
with tab_leaderboard:
    st.subheader("🏆 Multi-Round Candidate Screening Leaderboard")
    candidates = state.get("shortlisted_candidates", [])
    
    if candidates:
        table_rows = []
        for c in candidates:
            table_rows.append({
                "Rank": f"#{c['rank']}",
                "ID": c["candidate_id"],
                "Candidate Name": c["name"],
                "Current Title": c["title"],
                "Years Exp": c["years_experience"],
                "Match Score": c["composite_score"],
                "Verdict": c["recommendation"],
                "Confidence": f"{int(c['confidence_score']*100)}%"
            })
        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("🔍 Deep Explainability Profiles (Strengths, Gaps & Suggestions)")
        
        for c in candidates:
            rec = c["recommendation"]
            color_badge = "🟢" if "Hire" in rec and "No" not in rec else ("🟡" if rec == "Borderline" else "🔴")
            
            with st.expander(f"{color_badge} Rank #{c['rank']}: **{c['name']}** ({c['candidate_id']}) — Score: `{c['composite_score']}/100` — *{rec}*", expanded=(c['rank'] <= 2)):
                c_col1, c_col2 = st.columns([1, 1])
                with c_col1:
                    st.write(f"**Current Role:** {c['title']}")
                    st.write(f"**Experience:** {c['years_experience']} years")
                    st.write(f"**Recommendation Justification:** {c['justification']}")
                    st.write(f"**Skills:** {', '.join(c.get('skills', []))}")
                with c_col2:
                    st.markdown("**✅ Key Strengths:**")
                    for s in c.get("strengths", []):
                        st.markdown(f"- {s}")
                    st.markdown("**⚠️ Identified Gaps:**")
                    for g in c.get("gaps", []):
                        st.markdown(f"- {g}")
                    if c.get("improvement_suggestions"):
                        st.markdown("**💡 Borderline Improvement Suggestions:**")
                        for imp in c["improvement_suggestions"]:
                            st.markdown(f"- *{imp}*")
    else:
        st.info("No candidates evaluated yet. Load a job description from the sidebar.")

# ------------------------------------------
# TAB 3: Side-by-Side Candidate Comparator
# ------------------------------------------
with tab_compare:
    st.subheader("⚖️ Head-to-Head Candidate Comparator")
    candidates = state.get("shortlisted_candidates", [])
    candidate_map = {f"{c['name']} ({c['candidate_id']})": c['candidate_id'] for c in candidates}
    
    if len(candidate_map) >= 2:
        selected_cand_keys = st.multiselect(
            "Select Candidates to Compare:",
            options=list(candidate_map.keys()),
            default=list(candidate_map.keys())[:2]
        )
        
        if st.button("Run Head-to-Head Comparison"):
            selected_ids = [candidate_map[k] for k in selected_cand_keys]
            if len(selected_ids) >= 2:
                res = compare_candidates.invoke({"candidate_ids": selected_ids})
                st.markdown(res.get("narrative", "Unable to compare."))
                
                if res.get("comparison_table"):
                    st.table(pd.DataFrame(res["comparison_table"]))
            else:
                st.warning("Please select at least 2 candidates to compare.")
    else:
        st.info("Insufficient candidates available for comparison.")

# ------------------------------------------
# TAB 4: Interview Screening Studio
# ------------------------------------------
with tab_questions:
    st.subheader("❓ Tailored Interview Screening Question Studio")
    candidates = state.get("shortlisted_candidates", [])
    candidate_map = {f"#{c['rank']} {c['name']} ({c['candidate_id']}) - {c['title']}": c['candidate_id'] for c in candidates}
    
    if candidate_map:
        selected_for_q = st.selectbox("Select Candidate for Interview Preparation:", list(candidate_map.keys()))
        if st.button("Generate Interview Screening Dossier"):
            cid = candidate_map[selected_for_q]
            res = generate_interview_questions.invoke({"candidate_id": cid})
            st.markdown(res.get("formatted_markdown", "Failed to generate questions."))
    else:
        st.info("No shortlisted candidates available.")

# ------------------------------------------
# TAB 5: LangGraph State Machine Architecture
# ------------------------------------------
with tab_graph:
    st.subheader("🔄 LangGraph State Machine Diagram")
    st.markdown("""
    This workflow is implemented using **LangGraph** with explicit state transitions, conditional edges for human feedback,
    and multi-round candidate screening logic:
    """)
    
    mermaid_code = """
flowchart TD
    StartNode(["🚀 START"]):::startEnd
    ParseJD["📥 Node 1: Parse JD"]:::nodeStyle
    ExtractReq["🎯 Node 2: Extract Requirements<br/><b>Tool:</b> extract_requirements()"]:::toolStyle
    SearchResumes["🔍 Node 3: Search Resumes (Round 1)<br/><b>Tool:</b> RAG Search Tool (100 resumes)"]:::toolStyle
    RankCandidates["📊 Node 4: Rank Candidates (Round 2 & 3)<br/><i>Deep Evaluation & Hire/No-Hire Verdicts</i>"]:::nodeStyle
    GenerateReport["📄 Node 5: Generate Report<br/><b>Tool:</b> save_screening_report()"]:::nodeStyle
    HumanFeedback{"🤝 Node 6: Human Feedback Loop<br/><i>Human Refinement Gate</i>"}:::decisionStyle
    EndNode(["🏁 END"]):::startEnd

    StartNode --> ParseJD
    ParseJD --> ExtractReq
    ExtractReq --> SearchResumes
    SearchResumes --> RankCandidates
    RankCandidates --> GenerateReport
    GenerateReport --> HumanFeedback

    HumanFeedback -- "Criteria Adjusted / Re-rank" --> ExtractReq
    HumanFeedback -- "Shortlist Approved" --> EndNode

    classDef startEnd fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-weight:bold;
    classDef nodeStyle fill:#0F172A,stroke:#64748B,stroke-width:2px,color:#F1F5F9;
    classDef toolStyle fill:#1E1B4B,stroke:#818CF8,stroke-width:2px,color:#E0E7FF;
    classDef decisionStyle fill:#312E81,stroke:#C084FC,stroke-width:2px,color:#FAF5FF;
    """
    
    components.html(f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <div style="background-color: #0F172A; padding: 20px; border-radius: 10px;">
        <pre class="mermaid" style="text-align: center;">
{mermaid_code}
        </pre>
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
    """, height=500)
    
    st.markdown("""
    ### Key Architectural Highlights:
    1. **Agent State Persistence**: Tracks conversation history, parsed must-haves vs nice-to-haves, candidate shortlists, reasoning, and ranking delta explanations.
    2. **Multi-Round Screening Funnel**:
       - *Round 1 (Initial Screen)*: 100 candidate resumes filtered down to Top 10 using hybrid TF-IDF + BM25/Semantic cosine similarity and must-have constraints.
       - *Round 2 (Deep Analysis)*: Technical depth assessment, architectural background, and strengths & gaps breakdown.
       - *Round 3 (Final Decision)*: `Strong Hire`, `Hire`, `Borderline` (with actionable improvement suggestions), or `No Hire` recommendation.
    3. **Iterative Refinement Loop**: Conditional edge in LangGraph returns control to `extract_requirements` when users update criteria, providing explicit explanations for ranking changes.
    """)
