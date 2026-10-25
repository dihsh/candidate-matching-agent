"""Milestone 2: RAG Search Tool for Resume Corpus Retrieval.
Provides semantic and keyword-augmented retrieval over indexed resume profiles.
Computes hybrid similarity scores, extracts relevant chunks, and supports structured filtering.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUMES_JSON = os.path.join(BASE_DIR, "data", "resumes", "all_resumes.json")

class ResumeRAGIndex:
    """In-memory Vector/TF-IDF RAG search index over the candidate resume corpus."""
    _instance = None

    def __init__(self):
        self.candidates: List[Dict[str, Any]] = []
        self.documents: List[str] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.load_and_index()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_and_index(self):
        if not os.path.exists(RESUMES_JSON):
            return
        with open(RESUMES_JSON, "r", encoding="utf-8") as f:
            self.candidates = json.load(f)

        self.documents = []
        for cand in self.candidates:
            # Build an enriched document chunk
            skills_str = " ".join(cand.get("skills", []))
            highlights = []
            for exp in cand.get("experience", []):
                highlights.extend(exp.get("highlights", []))
            highlights_str = " ".join(highlights)
            projects_str = " ".join(cand.get("projects", []))
            doc = f"{cand['title']} {cand['summary']} Skills: {skills_str} Experience: {highlights_str} Projects: {projects_str}"
            self.documents.append(doc)

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=2500
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def search(
        self,
        query: str,
        top_k: int = 10,
        must_have_skills: Optional[List[str]] = None,
        min_years_experience: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Executes a hybrid RAG retrieval: semantic TF-IDF cosine similarity + hard criteria scoring."""
        if not self.vectorizer or self.tfidf_matrix is None or len(self.candidates) == 0:
            return []

        query_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        max_sim = float(sim_scores.max()) if sim_scores.max() > 0 else 1.0

        results = []
        must_haves = [s.lower().strip() for s in (must_have_skills or [])]

        for idx, cand in enumerate(self.candidates):
            raw_sim = float(sim_scores[idx])
            norm_sim = min(1.0, raw_sim / max_sim) if max_sim > 0 else raw_sim
            cand_skills_lower = [s.lower() for s in cand.get("skills", [])]
            cand_exp = float(cand.get("years_experience", 0))

            # Experience alignment score
            exp_penalty = 0.0
            if min_years_experience is not None:
                if cand_exp < min_years_experience:
                    exp_penalty = (min_years_experience - cand_exp) * 0.15

            # Skill matching ratio
            matched_must_haves = []
            missing_must_haves = []
            doc_lower = self.documents[idx].lower()

            def candidate_satisfies_skill(req: str) -> bool:
                r = req.lower()
                # Direct check
                if any(r in s or s in r for s in cand_skills_lower) or r in doc_lower:
                    return True
                # Semantic supersets
                if r == "javascript" and ("typescript" in cand_skills_lower or "typescript" in doc_lower):
                    return True
                if r == "react" and ("next.js" in cand_skills_lower or "next.js" in doc_lower):
                    return True
                if r == "css3" and any("css" in s or "tailwind" in s or "bootstrap" in s for s in cand_skills_lower):
                    return True
                return False

            if must_haves:
                for mh in must_haves:
                    if candidate_satisfies_skill(mh):
                        matched_must_haves.append(mh)
                    else:
                        missing_must_haves.append(mh)
                skill_match_ratio = len(matched_must_haves) / len(must_haves)
            else:
                skill_match_ratio = 1.0

            # Composite hybrid score (scaled to 100)
            base_score = (norm_sim * 40.0) + (skill_match_ratio * 45.0) + min(15.0, cand_exp * 2.0)
            final_score = max(5.0, min(99.0, base_score - (exp_penalty * 20.0)))

            results.append({
                "candidate_id": cand["id"],
                "name": cand["name"],
                "title": cand["title"],
                "years_experience": cand_exp,
                "skills": cand.get("skills", []),
                "similarity_score": round(raw_sim, 4),
                "composite_score": round(final_score, 1),
                "matched_must_haves": matched_must_haves,
                "missing_must_haves": missing_must_haves,
                "summary": cand.get("summary", ""),
                "education": cand.get("education", "")
            })

        # Rank by composite score descending
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        return results[:top_k]

def rag_search_tool(
    query: str,
    top_k: int = 10,
    must_have_skills: Optional[List[str]] = None,
    min_years_experience: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Standalone entry point for agent tool calls."""
    index = ResumeRAGIndex.get_instance()
    return index.search(
        query=query,
        top_k=top_k,
        must_have_skills=must_have_skills,
        min_years_experience=min_years_experience
    )
