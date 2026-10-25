# Autonomous Candidate Matching Agent (LangGraph)

An intelligent recruiting and candidate matching system built with **LangGraph**, featuring multi-round candidate screening, explainable ranking rationale, conversational natural language query processing, and iterative requirement refinement with human-in-the-loop feedback.

---

## 🏗️ Architecture & Graph Structure

The agent workflow is modeled as a state machine using LangGraph:

```
START ──► Parse JD ──► Extract Requirements ──► Search Resumes (Round 1) ──► Rank Candidates (Round 2 & 3) ──► Generate Report ──► Human Feedback Loop ──► END
                               ▲                                                                                                  │
                               └────────────────────── Criteria Adjusted / Re-Rank ───────────────────────────────────────────────┘
```

### 1. Agent State Design (`AgentState`)
- **Conversation History (`messages`)**: Retains multi-turn natural language dialogue.
- **Job Requirements Understanding (`requirements` & `previous_requirements`)**: Tracks target title, minimum experience threshold, must-have skills, nice-to-have bonus skills, and requirement deltas.
- **Multi-Round Candidate Shortlists**:
  - `round1_pool_size`: 100 candidate resumes in corpus.
  - `initial_candidates`: Top 10 broad semantic screen.
  - `shortlisted_candidates`: Top 10 with deep technical evaluation, strengths, gaps, scores.
  - `final_recommendations`: Classifications into `Strong Hire`, `Hire`, `Borderline` (with actionable improvement suggestions), and `No Hire`.
- **Explainability & Reasoning**: Stores ranking rationale, composite score breakdown, and ranking delta explanations when requirements are adjusted mid-conversation.

---

## 🛠️ Tools Available to the Agent

1. **File System Tools (`tools/filesystem_tools.py`)**:
   - `list_resumes(directory)`: Lists all resume profiles available in the corpus.
   - `read_resume(candidate_id)`: Loads structured metadata and markdown content.
   - `search_resumes_filesystem(keyword)`: Full-text scanner across files.
   - `save_screening_report(filename, content)`: Persists markdown match dossiers.
   - `read_job_description(name_or_path)`: Fetches target job descriptions.

2. **RAG Search Tool (`tools/rag_tools.py`)**:
   - `rag_search_tool(query, top_k=10, must_have_skills, min_years_experience)`:
     - Vector TF-IDF cosine similarity + skill token matching + experience penalty scoring.
     - Blazingly fast, reproducible, and operates with zero external API dependencies.

3. **Auxiliary Domain Tools (`tools/agent_tools.py`)**:
   - `extract_requirements(jd)`: Automatically extracts job title, experience requirements, must-haves, and nice-to-haves.
   - `compare_candidates(candidate_ids)`: Generates head-to-head comparison matrices, evaluates seniority, technical architecture, and provides actionable trade-off verdicts.
   - `generate_interview_questions(candidate_id)`: Produces 4-tier screening questions (Technical Deep-Dive, System Design & Architecture, Gap & Ramp-up Verification, and Behavioral/Leadership).

---

## 🎯 Advanced Capabilities

### Multi-Round Screening Funnel
- **Round 1 (Broad Screen)**: Evaluates 100 candidate resumes across varied engineering domains (Frontend, Full-Stack, Backend, Cloud/DevOps, AI/ML) and filters down to the Top 10.
- **Round 2 (Deep Technical Analysis)**: Evaluates architecture background, hands-on micro-frontends/cloud experience, strengths, and specific skill gaps.
- **Round 3 (Hire / No-Hire Recommendations)**:
  - `Strong Hire`: 85+ score, meets all must-haves, exceeds experience requirements.
  - `Hire`: 75-84 score, solid foundations, immediate contributor.
  - `Borderline`: 55-74 score, high potential with specific addressable gaps; **automatically generates tailored improvement suggestions**.
  - `No Hire`: Substantial experience or skill shortfalls.

### Iterative Refinement & Ranking Change Explanation
Recruiters can modify criteria mid-conversation (e.g. *"Adjust requirements: require 5+ years experience and AWS knowledge"*). The agent re-runs the pipeline and explains exact rank movements (e.g. *"Candidate X moved from #4 to #2 because of AWS experience and 5.9 years seniority"*).

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.10+ (Tested on Python 3.12 and 3.14)

### 1. Setup Environment
```bash
# Clone or navigate into project directory
cd candidate_matching_agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Interactive Streamlit Web UI
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to access:
- **Interactive Conversational Chat** with 1-click sample prompts
- **Multi-Round Screening Leaderboard & Funnel KPI metrics**
- **Side-by-Side Head-to-Head Candidate Comparator**
- **Interview Question Generator Studio**
- **Interactive LangGraph State Machine Architecture Diagram**

### 3. Run the Command-Line Interface (CLI)
```bash
python cli.py
```

### 4. Run the Automated 6-Flow Test Suite
```bash
python test_scenarios.py
```
Validates all assignment criteria:
1. `Flow 1`: Full multi-round screening pipeline (100 resumes -> Top 10 -> Hire/No-Hire)
2. `Flow 2`: Conversational natural language query (`"Find me candidates with React and 3+ years experience"`)
3. `Flow 3`: Candidate comparison (`"Compare the top 3 matches side by side"`)
4. `Flow 4`: Explainability query (`"Why did John rank higher than Jane?"`)
5. `Flow 5`: Iterative refinement and ranking delta explanation (`"Adjust requirements: require 5+ years experience and AWS"`)
6. `Flow 6`: Screening interview questions & borderline candidate improvement suggestions

---

## 📁 Project Structure

```
candidate_matching_agent/
├── data/
│   ├── resumes/            # 100 synthetic candidate resumes (.json & .md)
│   ├── sample_jds/         # Senior React Developer, Full Stack Cloud, ML/AI JDs
│   └── reports/            # Output screening reports generated by agent
├── tools/
│   ├── __init__.py
│   ├── filesystem_tools.py # Milestone 1 file system tools
│   ├── rag_tools.py        # Milestone 2 RAG search & indexing engine
│   └── agent_tools.py      # extract_requirements, compare_candidates, generate_interview_questions
├── agent_state.py          # LangGraph TypedDict state schema
├── matching_agent.py       # LangGraph agent workflow & conversational handlers
├── state_machine_diagram.py# State machine diagram exporter (Mermaid & HTML visualizer)
├── app.py                  # Full-featured Streamlit Web UI
├── cli.py                  # Terminal CLI interface
├── test_scenarios.py       # Comprehensive 6-flow test suite
├── docs/                   # Visual state machine diagram (.mmd & .html)
├── requirements.txt        # Python dependency manifest
└── README.md               # Documentation
```
