"""Milestone 1: File System Tools for Candidate Matching Agent.
Provides core file system operations to read, list, search, and persist resume records and screening reports.
"""

import os
import glob
import json
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUMES_DIR = os.path.join(BASE_DIR, "data", "resumes")
JDS_DIR = os.path.join(BASE_DIR, "data", "sample_jds")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

def list_resumes(directory: Optional[str] = None) -> List[str]:
    """Lists all available resume files in the resume directory."""
    target_dir = directory or RESUMES_DIR
    if not os.path.exists(target_dir):
        return []
    files = [os.path.basename(f) for f in glob.glob(os.path.join(target_dir, "CAND-*.md"))]
    return sorted(files)

def read_resume(candidate_id: str) -> Dict[str, Any]:
    """Reads a candidate resume by candidate ID (e.g. 'CAND-001' or 'CAND-001.md').
    Returns structured data and full markdown text.
    """
    clean_id = candidate_id.replace(".md", "").replace(".json", "").upper()
    md_path = os.path.join(RESUMES_DIR, f"{clean_id}.md")
    json_path = os.path.join(RESUMES_DIR, "all_resumes.json")
    
    candidate_meta = None
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                all_cands = json.load(f)
                for c in all_cands:
                    if c["id"].upper() == clean_id:
                        candidate_meta = c
                        break
        except Exception:
            pass
            
    raw_markdown = ""
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            raw_markdown = f.read()
            
    if not raw_markdown and not candidate_meta:
        return {"error": f"Candidate {clean_id} not found."}
        
    return {
        "candidate_id": clean_id,
        "metadata": candidate_meta or {},
        "raw_text": raw_markdown
    }

def search_resumes_filesystem(keyword: str) -> List[Dict[str, str]]:
    """Performs a direct file-system keyword search across all resume markdown files."""
    results = []
    keyword_lower = keyword.lower()
    for file_path in glob.glob(os.path.join(RESUMES_DIR, "CAND-*.md")):
        cand_id = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if keyword_lower in content.lower():
                # Extract first matching line snippet
                matching_lines = [line.strip() for line in content.split("\n") if keyword_lower in line.lower()]
                snippet = matching_lines[0] if matching_lines else ""
                results.append({
                    "candidate_id": cand_id,
                    "file": os.path.basename(file_path),
                    "snippet": snippet[:150]
                })
    return results

def save_screening_report(report_name: str, content: str) -> str:
    """Saves a candidate match or screening report to the file system."""
    if not report_name.endswith(".md"):
        report_name += ".md"
    file_path = os.path.join(REPORTS_DIR, report_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def read_job_description(name_or_path: str) -> str:
    """Reads a job description from sample JDs or direct path."""
    if os.path.exists(name_or_path):
        with open(name_or_path, "r", encoding="utf-8") as f:
            return f.read()
            
    candidate_path = os.path.join(JDS_DIR, f"{name_or_path}.txt")
    if os.path.exists(candidate_path):
        with open(candidate_path, "r", encoding="utf-8") as f:
            return f.read()
            
    candidate_json = os.path.join(JDS_DIR, f"{name_or_path}.json")
    if os.path.exists(candidate_json):
        with open(candidate_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("raw_text", "")
            
    return ""
