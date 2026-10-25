"""Test Scenarios: 5+ Conversation Flows for Candidate Matching Agent.
Validates all requirements from Part A, Part B, and Part C:
1. Flow 1: Full Multi-Round Screening Pipeline (100 resumes -> Top 10 -> Hire/No-Hire)
2. Flow 2: Conversational Search ("Find me candidates with React and 3+ years experience")
3. Flow 3: Head-to-Head Comparison ("Compare the top 3 matches side by side")
4. Flow 4: Explainability Deep-Dive ("Why did John rank higher than Jane?")
5. Flow 5: Iterative Refinement & Ranking Delta Explanation ("Adjust requirements: require 5+ years experience and AWS")
6. Flow 6: Screening Interview Questions & Borderline Improvement Suggestions
"""

import sys
import os
import json

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from matching_agent import MatchingAgent
from tools.filesystem_tools import read_job_description

def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80 + "\n")

def test_flow_1_full_pipeline(agent: MatchingAgent):
    print_banner("Flow 1: Full Multi-Round Screening Pipeline (Part A & Part C)")
    state = agent.state
    
    print(f"Current Step: {state.get('current_step')}")
    print(f"Role: {state.get('requirements', {}).get('job_title')}")
    print(f"Must-Have Skills: {state.get('requirements', {}).get('must_have_skills')}")
    print(f"Nice-to-Have Skills: {state.get('requirements', {}).get('nice_to_have_skills')}")
    print(f"Round 1 Initial Candidate Pool Screened: {state.get('round1_pool_size', 100)} candidates")
    print(f"Round 1 Screened Down To: {len(state.get('initial_candidates', []))} candidates")
    
    shortlisted = state.get("shortlisted_candidates", [])
    print(f"\nRound 2 & 3 Shortlisted Leaderboard ({len(shortlisted)} candidates):")
    for c in shortlisted[:5]:
        print(f"  #{c['rank']} {c['name']} ({c['candidate_id']}) - Score: {c['composite_score']}/100 | {c['recommendation']} (Conf: {int(c['confidence_score']*100)}%)")
        print(f"     Strengths: {c['strengths'][0] if c['strengths'] else 'None'}")
        print(f"     Gaps: {c['gaps'][0] if c['gaps'] else 'None'}")

    assert len(shortlisted) >= 5, "Pipeline should produce at least 5 top candidates"
    assert state.get("report_markdown"), "Report markdown should be generated"
    print("\n[PASSED] Flow 1 verified successfully!")

def test_flow_2_conversational_search(agent: MatchingAgent):
    print_banner("Flow 2: Conversational Natural Language Query (Part B)")
    query = "Find me candidates with React and 3+ years experience"
    print(f"User Query: \"{query}\"\n")
    response = agent.handle_natural_query(query)
    print("Agent Response:")
    print(response)
    
    assert "Search Results for" in response, "Response should confirm search query"
    assert "years experience" in response, "Response should mention experience filtering"
    print("\n[PASSED] Flow 2 verified successfully!")

def test_flow_3_candidate_comparison(agent: MatchingAgent):
    print_banner("Flow 3: Head-to-Head Comparison Query (Part B & Part A Tools)")
    query = "Compare the top 3 matches side by side"
    print(f"User Query: \"{query}\"\n")
    response = agent.handle_natural_query(query)
    print("Agent Response:")
    print(response)
    
    assert "Head-to-Head Comparison" in response, "Response should contain comparison headline"
    assert "Experience & Seniority" in response, "Response should evaluate relative seniority"
    assert "Trade-off Verdict" in response, "Response should provide trade-off verdict"
    print("\n[PASSED] Flow 3 verified successfully!")

def test_flow_4_explainability(agent: MatchingAgent):
    print_banner("Flow 4: Explainability Query - 'Why did John rank higher than Jane?' (Part B & Part C)")
    query = "Why did John rank higher than Jane?"
    print(f"User Query: \"{query}\"\n")
    response = agent.handle_natural_query(query)
    print("Agent Response:")
    print(response)
    
    assert "John Doe" in response, "Response should reference John Doe"
    assert "Jane Smith" in response, "Response should reference Jane Smith"
    assert "Composite Match Scores" in response or "Seniority" in response, "Response should explain scoring differential"
    print("\n[PASSED] Flow 4 verified successfully!")

def test_flow_5_iterative_refinement(agent: MatchingAgent):
    print_banner("Flow 5: Iterative Refinement & Ranking Changes Explanation (Part B)")
    # Capture current #1 candidate ID
    prev_top = agent.state["shortlisted_candidates"][0]["name"]
    print(f"Baseline #1 Candidate: {prev_top}")
    
    refinement_query = "Adjust requirements: require 5+ years experience and AWS knowledge"
    print(f"\nUser Refinement Feedback: \"{refinement_query}\"\n")
    response = agent.handle_natural_query(refinement_query)
    print("Agent Response:")
    print(response)
    
    new_reqs = agent.state["requirements"]
    print(f"\nUpdated Min Experience: {new_reqs['min_years_experience']} years")
    print(f"Updated Must-Haves: {new_reqs['must_have_skills']}")
    
    assert new_reqs["min_years_experience"] == 5.0, "Experience criteria should update to 5.0"
    assert "AWS" in new_reqs["must_have_skills"], "AWS should now be a must-have skill"
    print("\n[PASSED] Flow 5 verified successfully!")

def test_flow_6_interview_questions_and_borderline(agent: MatchingAgent):
    print_banner("Flow 6: Screening Questions & Borderline Improvement Suggestions (Part A & Part C)")
    query = "Generate interview questions for John Doe"
    print(f"User Query: \"{query}\"\n")
    response = agent.handle_natural_query(query)
    print("Agent Response:")
    print(response)
    
    assert "Screening Interview Questions for John Doe" in response, "Should generate questions for John"
    assert "Technical Deep-Dive" in response, "Should have technical questions"
    assert "Architecture & System Design" in response, "Should have architecture questions"
    
    # Verify borderline improvement suggestions in state
    borderline_cands = [c for c in agent.state["shortlisted_candidates"] if c["recommendation"] == "Borderline"]
    if borderline_cands:
        b_cand = borderline_cands[0]
        print(f"\nBorderline Candidate Improvement Suggestions for {b_cand['name']} ({b_cand['candidate_id']}):")
        for sug in b_cand.get("improvement_suggestions", []):
            print(f"  💡 {sug}")
        assert len(b_cand.get("improvement_suggestions", [])) > 0, "Borderline candidate should have suggestions"
        
    print("\n[PASSED] Flow 6 verified successfully!")

def run_all_tests():
    print("================================================================================")
    print("       STARTING AUTOMATED VERIFICATION: ALL 6 CONVERSATION FLOWS                ")
    print("================================================================================")
    
    agent = MatchingAgent()
    
    test_flow_1_full_pipeline(agent)
    test_flow_2_conversational_search(agent)
    test_flow_3_candidate_comparison(agent)
    test_flow_4_explainability(agent)
    test_flow_5_iterative_refinement(agent)
    test_flow_6_interview_questions_and_borderline(agent)
    
    print("\n" + "=" * 80)
    print("  🎉 ALL 6 TEST CONVERSATION FLOWS PASSED WITH 100% SUCCESS!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_all_tests()
