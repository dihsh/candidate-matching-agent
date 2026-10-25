"""Visual State Machine Diagram generator for LangGraph Candidate Matching Agent.
Outputs Mermaid definition and interactive HTML visualizer.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

MERMAID_GRAPH = """flowchart TD
    %% Styling and Definitions
    classDef startEnd fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC,font-weight:bold;
    classDef standardNode fill:#0F172A,stroke:#64748B,stroke-width:2px,color:#F1F5F9;
    classDef toolNode fill:#1E1B4B,stroke:#818CF8,stroke-width:2px,color:#E0E7FF;
    classDef decisionNode fill:#312E81,stroke:#C084FC,stroke-width:2px,color:#FAF5FF;
    classDef successNode fill:#064E3B,stroke:#34D399,stroke-width:2px,color:#ECFDF5;

    %% Workflow Nodes
    StartNode(["🚀 START"]):::startEnd
    ParseJD["📥 Node 1: Parse JD<br/><i>Validates & normalizes Job Description</i>"]:::standardNode
    ExtractReq["🎯 Node 2: Extract Requirements<br/><b>Tool:</b> extract_requirements()<br/><i>Must-Haves vs Nice-to-Haves, Exp Target</i>"]:::toolNode
    SearchResumes["🔍 Node 3: Search Resumes (Round 1)<br/><b>Tool:</b> RAG Search / TF-IDF Vector<br/><i>Screens Top 10 from 100 Resumes</i>"]:::toolNode
    RankCandidates["📊 Node 4: Rank Candidates (Round 2 & 3)<br/><i>Deep Analysis, Strengths/Gaps,<br/>Hire/No-Hire Verdicts & Suggestions</i>"]:::standardNode
    GenerateReport["📄 Node 5: Generate Report<br/><b>Tool:</b> save_screening_report()<br/><i>Saves full explainable Markdown dossier</i>"]:::standardNode
    HumanFeedback{"🤝 Node 6: Human Feedback Loop<br/><i>Human Review & Refinement Gate</i>"}:::decisionNode
    EndNode(["🏁 END (Shortlist Approved)"]):::successNode

    %% Additional On-Demand Tools
    subgraph OnDemandTools ["🛠️ Agent Auxiliary Tools"]
        CompareTool["⚖️ compare_candidates(ids)<br/><i>Head-to-head matrix & narrative</i>"]:::toolNode
        QuestionsTool["❓ generate_interview_questions(id)<br/><i>Tailored technical & behavioral questions</i>"]:::toolNode
        FileSysTool["📁 Filesystem Tools<br/><i>read_resume, list_resumes, save_report</i>"]:::toolNode
    end

    %% Workflow Edges
    StartNode --> ParseJD
    ParseJD --> ExtractReq
    ExtractReq --> SearchResumes
    SearchResumes --> RankCandidates
    RankCandidates --> GenerateReport
    GenerateReport --> HumanFeedback

    %% Iterative Refinement Feedback Loop
    HumanFeedback -- "Criteria Adjusted / Re-rank" --> ExtractReq
    HumanFeedback -- "Shortlist Approved / Finished" --> EndNode

    %% Auxiliary Connections
    HumanFeedback -.-> CompareTool
    HumanFeedback -.-> QuestionsTool
    RankCandidates -.-> FileSysTool
"""

def generate_diagram_files():
    mmd_path = os.path.join(DOCS_DIR, "state_machine.mmd")
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(MERMAID_GRAPH)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candidate Matching Agent - LangGraph State Machine Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #090D16;
            color: #E2E8F0;
            margin: 0;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .header {{
            text-align: center;
            max-width: 900px;
            margin-bottom: 25px;
        }}
        h1 {{
            color: #38BDF8;
            margin-bottom: 8px;
            font-size: 26px;
        }}
        p {{
            color: #94A3B8;
            font-size: 14px;
            line-height: 1.6;
        }}
        .diagram-container {{
            background: #0F172A;
            border: 1px solid #1E293B;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            max-width: 1000px;
            width: 100%;
        }}
        .badge-list {{
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .badge {{
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-rag {{ background: #1E1B4B; color: #818CF8; border: 1px solid #4338CA; }}
        .badge-rounds {{ background: #064E3B; color: #34D399; border: 1px solid #059669; }}
        .badge-loop {{ background: #312E81; color: #C084FC; border: 1px solid #7C3AED; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 LangGraph Agent State Machine Architecture</h1>
        <p>Visual representation of the candidate screening and iterative refinement pipeline. Flow follows: <code>START → Parse JD → Extract Requirements → Search Resumes → Rank Candidates → Generate Report → Human Feedback Loop → END</code>.</p>
        <div class="badge-list">
            <span class="badge badge-rounds">Multi-Round Screening (100 → 10 → Hire/No-Hire)</span>
            <span class="badge badge-rag">RAG Search & Filesystem Tools</span>
            <span class="badge badge-loop">Human Feedback & Iterative Refinement</span>
        </div>
    </div>
    <div class="diagram-container">
        <pre class="mermaid">
{MERMAID_GRAPH}
        </pre>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>
"""
    html_path = os.path.join(DOCS_DIR, "state_machine.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated diagram files in {DOCS_DIR}:")
    print(f" - Mermaid definition: {mmd_path}")
    print(f" - Interactive HTML visualizer: {html_path}")

if __name__ == "__main__":
    generate_diagram_files()
