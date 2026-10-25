"""Additional Tools required for Candidate Matching Agent:
1. extract_requirements(jd: str) -> Parse must-have vs nice-to-have
2. compare_candidates(candidate_ids: list) -> Head-to-head comparison
3. generate_interview_questions(candidate_id: str) -> Create screening questions
"""

import re
import json
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from tools.filesystem_tools import read_resume
from tools.rag_tools import ResumeRAGIndex

@tool
def extract_requirements(jd: str) -> Dict[str, Any]:
    """Parses a job description to extract structured requirements:
    role title, minimum years of experience, must-have skills, nice-to-have skills,
    responsibilities, and domain focus.
    """
    lines = jd.strip().split("\n")
    
    # 1. Title Extraction
    title = "Software Engineer"
    title_match = re.search(r"(?:Job Title|Role|Position):\s*(.+)", jd, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    elif len(lines) > 0 and len(lines[0]) < 60:
        title = lines[0].replace("#", "").strip()

    # 2. Experience Extraction
    min_exp = 3.0
    exp_matches = re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:-\s*(\d+(?:\.\d+)?))?\s*years?", jd, re.IGNORECASE)
    if exp_matches:
        try:
            min_exp = float(exp_matches[0][0])
        except Exception:
            min_exp = 3.0

    # 3. Must-have vs Nice-to-have extraction
    must_have_section = ""
    nice_to_have_section = ""

    must_pattern = re.compile(r"Must[- ]Have(?:\s+(?:Requirements|Skills))?:?(.*?)(?=Nice[- ]to[- ]Have|Preferred|Bonus|Responsibilities|$)", re.IGNORECASE | re.DOTALL)
    nice_pattern = re.compile(r"Nice[- ]to[- ]Have(?:\s+(?:Requirements|Skills))?:?(.*?)(?=Responsibilities|About the Role|$)", re.IGNORECASE | re.DOTALL)

    m_must = must_pattern.search(jd)
    if m_must:
        must_have_section = m_must.group(1)

    m_nice = nice_pattern.search(jd)
    if m_nice:
        nice_to_have_section = m_nice.group(1)

    # Standard technical skill catalog for extraction
    skill_catalog = [
        "React", "TypeScript", "JavaScript", "Next.js", "Redux", "GraphQL", "Tailwind CSS",
        "Node.js", "Express", "Python", "FastAPI", "Django", "AWS", "Kubernetes", "Docker",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "CI/CD", "Jest", "Playwright",
        "Microservices", "REST", "Vue.js", "Angular", "Terraform", "LangChain", "PyTorch", "CSS3", "HTML5"
    ]

    must_haves = []
    nice_to_haves = []

    # If explicit sections exist, parse skills within them
    if must_have_section:
        for skill in skill_catalog:
            if re.search(rf"\b{re.escape(skill)}\b", must_have_section, re.IGNORECASE):
                if skill not in must_haves:
                    must_haves.append(skill)
    else:
        # Fallback keyword extraction from full text
        for skill in skill_catalog:
            if re.search(rf"\b{re.escape(skill)}\b", jd, re.IGNORECASE):
                must_haves.append(skill)

    if nice_to_have_section:
        for skill in skill_catalog:
            if re.search(rf"\b{re.escape(skill)}\b", nice_to_have_section, re.IGNORECASE):
                if skill not in must_haves and skill not in nice_to_haves:
                    nice_to_haves.append(skill)
    else:
        potential_nice = ["AWS", "Kubernetes", "Next.js", "GraphQL", "CI/CD", "Terraform"]
        for s in potential_nice:
            if s in must_haves and len(must_haves) > 4:
                must_haves.remove(s)
                nice_to_haves.append(s)

    # Ensure must-haves has reasonable values
    if not must_haves:
        must_haves = ["React", "JavaScript", "TypeScript"]

    return {
        "job_title": title,
        "min_years_experience": min_exp,
        "must_have_skills": must_haves,
        "nice_to_have_skills": nice_to_haves,
        "raw_parsed_summary": f"Targeting {title} with {min_exp}+ yrs exp. Must-haves: {', '.join(must_haves)}. Nice-to-haves: {', '.join(nice_to_haves) if nice_to_haves else 'None stated'}."
    }

@tool
def compare_candidates(candidate_ids: List[str]) -> Dict[str, Any]:
    """Generates a head-to-head comparison between specified candidates,
    evaluating their years of experience, skill depth, leadership, strengths,
    and relative trade-offs.
    """
    candidates_data = []
    for cid in candidate_ids:
        res = read_resume(cid)
        if "error" not in res and res.get("metadata"):
            candidates_data.append(res["metadata"])

    if len(candidates_data) < 2:
        return {
            "error": f"Need at least 2 valid candidates to compare. Found {len(candidates_data)}."
        }

    # Build comparison matrix
    comparison_table = []
    for c in candidates_data:
        comparison_table.append({
            "Candidate ID": c["id"],
            "Name": c["name"],
            "Current Role": c["title"],
            "Experience (Years)": c["years_experience"],
            "Key Skills": ", ".join(c.get("skills", [])[:6]),
            "Education": c.get("education", "").split(",")[0]
        })

    # Head-to-head analytical breakdown
    sorted_by_exp = sorted(candidates_data, key=lambda x: x["years_experience"], reverse=True)
    leader = sorted_by_exp[0]
    challengers = sorted_by_exp[1:]

    narrative = [
        f"### Head-to-Head Comparison: {' vs '.join([c['name'] for c in candidates_data])}",
        f"\n**1. Experience & Seniority:**",
        f"- **{leader['name']}** holds the greatest seniority with **{leader['years_experience']} years** ({leader['title']})."
    ]
    for ch in challengers:
        diff = round(leader['years_experience'] - ch['years_experience'], 1)
        narrative.append(f"- **{ch['name']}** has **{ch['years_experience']} years** ({diff} years difference).")

    narrative.append("\n**2. Technical Strengths & Architecture:**")
    for c in candidates_data:
        skills_set = set(c.get("skills", []))
        has_cloud = any(cloud in skills_set for cloud in ["AWS", "GCP", "Kubernetes", "Docker", "Terraform"])
        has_arch = any(arch in skills_set for arch in ["Next.js", "GraphQL", "Redux", "CI/CD", "Microservices"])
        narrative.append(
            f"- **{c['name']}**: Strong core in {', '.join(c.get('skills', [])[:4])}. "
            f"{'Demonstrates cloud/infrastructure mastery. ' if has_cloud else 'Primarily UI focused without extensive cloud depth. '}"
            f"{'Possesses architecture and scaling background.' if has_arch else ''}"
        )

    narrative.append("\n**3. Trade-off Verdict:**")
    c1, c2 = candidates_data[0], candidates_data[1]
    if c1["years_experience"] > c2["years_experience"]:
        narrative.append(
            f"- Choose **{c1['name']}** if seeking leadership, architectural ownership, and immediate senior impact.\n"
            f"- Choose **{c2['name']}** if seeking rapid component-level execution or if budget/band favors an agile mid-level engineer."
        )
    else:
        narrative.append(
            f"- Choose **{c2['name']}** for greater architectural maturity and senior leadership.\n"
            f"- Choose **{c1['name']}** for targeted tactical frontend implementation."
        )

    return {
        "candidate_ids": candidate_ids,
        "comparison_table": comparison_table,
        "narrative": "\n".join(narrative)
    }

@tool
def generate_interview_questions(candidate_id: str) -> Dict[str, Any]:
    """Generates tailored technical and behavioral screening interview questions
    for a candidate based on their specific resume background, projects, and potential skill gaps.
    """
    res = read_resume(candidate_id)
    if "error" in res or not res.get("metadata"):
        return {"error": f"Candidate {candidate_id} not found."}

    meta = res["metadata"]
    name = meta["name"]
    title = meta["title"]
    skills = meta.get("skills", [])
    exp = meta.get("years_experience", 0)

    # Dynamic question generation based on skills and experience
    questions = {
        "candidate_id": meta["id"],
        "name": name,
        "title": title,
        "experience": f"{exp} years",
        "technical_depth_questions": [],
        "system_design_questions": [],
        "gap_verification_questions": [],
        "behavioral_questions": []
    }

    # 1. Technical Depth
    if "React" in skills:
        questions["technical_depth_questions"].append(
            "How have you optimized React rendering performance in high-frequency update scenarios? Can you explain how you use React 18 concurrent features, useMemo/useCallback, or virtualization?"
        )
    if "TypeScript" in skills:
        questions["technical_depth_questions"].append(
            "How do you design type-safe component props and generic utilities for shared design libraries in TypeScript?"
        )
    else:
        questions["technical_depth_questions"].append(
            "Your background highlights JavaScript; how comfortable are you transitioning to strict TypeScript codebases, and how do you prevent runtime type errors?"
        )

    if "GraphQL" in skills or "REST APIs" in skills:
        questions["technical_depth_questions"].append(
            "Describe your strategy for client-side state caching and cache invalidation when working with GraphQL Apollo Client or React Query vs REST endpoints."
        )

    # 2. System Design & Scalability
    if exp >= 5.0 or "Next.js" in skills or "AWS" in skills:
        questions["system_design_questions"].append(
            "Walk us through how you would architect a globally distributed web application with Server-Side Rendering (SSR), edge caching, and automated blue-green deployments on AWS."
        )
    else:
        questions["system_design_questions"].append(
            "How do you approach modularizing a growing frontend codebase? What patterns do you follow to separate presentation components from business logic and state stores?"
        )

    # 3. Gap Verification / Borderline validation
    missing_elements = []
    if "AWS" not in skills and "Docker" not in skills:
        missing_elements.append("cloud deployment (AWS/Docker)")
    if "TypeScript" not in skills:
        missing_elements.append("TypeScript")
    if exp < 3.0:
        missing_elements.append("senior autonomy")

    if missing_elements:
        questions["gap_verification_questions"].append(
            f"Your profile shows less hands-on emphasis in {', '.join(missing_elements)}. How have you approached quickly ramping up on unfamiliar infrastructure or tooling in past roles?"
        )
    else:
        questions["gap_verification_questions"].append(
            "Given your extensive full-stack/cloud exposure, how do you balance low-level infrastructure work with keeping your frontend React craft up-to-date?"
        )

    # 4. Behavioral & Team Leadership
    if exp >= 5.0:
        questions["behavioral_questions"].append(
            "Tell us about a time you led a major architectural refactor or migration. How did you build consensus among dissenting engineers and avoid shipping delays?"
        )
    else:
        questions["behavioral_questions"].append(
            "Describe a complex bug in production that was difficult to isolate. How did you debug it, and what guardrails did you put in place to prevent regressions?"
        )

    formatted_md = f"""### Screening Interview Questions for {name} ({meta['id']} - {title})
**Years of Experience:** {exp} yrs | **Core Stack:** {', '.join(skills[:5])}

#### 🛠️ 1. Technical Deep-Dive
"""
    for idx, q in enumerate(questions["technical_depth_questions"], 1):
        formatted_md += f"{idx}. {q}\n"

    formatted_md += "\n#### 🏗️ 2. Architecture & System Design\n"
    for idx, q in enumerate(questions["system_design_questions"], 1):
        formatted_md += f"{idx}. {q}\n"

    formatted_md += "\n#### 🔍 3. Gap & Ramp-up Verification\n"
    for idx, q in enumerate(questions["gap_verification_questions"], 1):
        formatted_md += f"{idx}. {q}\n"

    formatted_md += "\n#### 🤝 4. Behavioral & Engineering Culture\n"
    for idx, q in enumerate(questions["behavioral_questions"], 1):
        formatted_md += f"{idx}. {q}\n"

    questions["formatted_markdown"] = formatted_md
    return questions
