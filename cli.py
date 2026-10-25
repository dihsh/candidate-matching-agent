"""Interactive CLI Interface for LangGraph Candidate Matching Agent."""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from matching_agent import MatchingAgent
from tools.filesystem_tools import read_job_description

def print_help():
    print("""
======================================================================
  🤖 Candidate Matching Agent - Interactive CLI Commands & Queries
======================================================================
  Type any natural language prompt, or try one of these examples:
  1. "Find me candidates with React and 3+ years experience"
  2. "Compare the top 3 matches side by side"
  3. "Why did John rank higher than Jane?"
  4. "Adjust requirements: require 5+ years experience and AWS knowledge"
  5. "Generate interview questions for John Doe"
  6. "status"  - View current state, requirements, and top candidates
  7. "report"  - View the generated markdown screening report
  8. "help"    - Show this help menu
  9. "exit"    - Exit the program
======================================================================
""")

def main():
    print("\n" + "=" * 70)
    print("  🚀 Initializing LangGraph Candidate Matching Agent...")
    print("=" * 70)

    agent = MatchingAgent()
    reqs = agent.state.get("requirements", {})
    print(f"\n[Ready] Loaded Job Description: {reqs.get('job_title', 'Role')}")
    print(f"Screened 100 candidate resumes into Top {len(agent.state.get('shortlisted_candidates', []))} shortlist.\n")
    print_help()

    while True:
        try:
            user_input = input("\n[Recruiter / Hiring Manager] > ").strip()
            if not user_input:
                continue

            cmd_lower = user_input.lower()
            if cmd_lower in ["exit", "quit", "q"]:
                print("Exiting Candidate Matching Agent. Goodbye!")
                break
            elif cmd_lower in ["help", "h"]:
                print_help()
                continue
            elif cmd_lower == "status":
                s_reqs = agent.state.get("requirements", {})
                shortlisted = agent.state.get("shortlisted_candidates", [])
                print("\n--- Current Agent State ---")
                print(f"Target Role: {s_reqs.get('job_title')}")
                print(f"Experience Required: {s_reqs.get('min_years_experience')}+ yrs")
                print(f"Must-Have Skills: {', '.join(s_reqs.get('must_have_skills', []))}")
                print(f"Top 5 Candidates:")
                for c in shortlisted[:5]:
                    print(f"  #{c['rank']} {c['name']} ({c['candidate_id']}) - Score: {c['composite_score']} | {c['recommendation']}")
                continue
            elif cmd_lower == "report":
                report = agent.state.get("report_markdown", "No report available.")
                print("\n" + report)
                continue

            # Process natural language query
            response = agent.handle_natural_query(user_input)
            print("\n[Matching Agent]:\n")
            print(response)

        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    main()
