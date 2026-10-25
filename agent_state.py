"""Agent State Design for Candidate Matching Agent.
Tracks conversation history, job requirements understanding, multi-round candidate shortlists,
reasoning, and iterative refinement feedback.
"""

from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
import operator

class CandidateEvaluation(TypedDict, total=False):
    candidate_id: str
    name: str
    title: str
    years_experience: float
    skills: List[str]
    similarity_score: float
    composite_score: float
    rank: int
    strengths: List[str]
    gaps: List[str]
    recommendation: str  # "Strong Hire", "Hire", "Borderline", "No Hire"
    confidence_score: float
    improvement_suggestions: List[str]
    justification: str

class JobRequirements(TypedDict, total=False):
    job_title: str
    min_years_experience: float
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    domain: Optional[str]
    raw_parsed_summary: str

class AgentState(TypedDict, total=False):
    # 1. Track conversation history
    messages: List[Dict[str, str]]
    user_query: Optional[str]
    
    # 2. Maintain job requirements understanding
    job_description: str
    requirements: JobRequirements
    previous_requirements: Optional[JobRequirements]
    
    # 3. Store candidate shortlist and multi-round screening
    round1_pool_size: int                       # 100 resumes
    initial_candidates: List[Dict[str, Any]]     # Round 1: Top 10 filtered from 100
    shortlisted_candidates: List[CandidateEvaluation] # Round 2: Deep technical analysis of Top 10
    final_recommendations: List[CandidateEvaluation]  # Round 3: Hire / Borderline / No-Hire verdicts
    
    # 4. Explainability & Reasoning
    ranking_reasoning: str
    ranking_changes: List[Dict[str, Any]]
    report_markdown: str
    
    # 5. Ad-hoc tool outputs
    comparison_result: Optional[Dict[str, Any]]
    interview_questions: Optional[Dict[str, Any]]
    
    # 6. Workflow tracking
    current_step: str
    human_feedback: Optional[str]
    human_approved: bool
