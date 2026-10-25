"""Dataset generator: creates 100 realistic candidate resumes and sample Job Descriptions."""

import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_DIR = os.path.join(BASE_DIR, "data", "resumes")
JD_DIR = os.path.join(BASE_DIR, "data", "sample_jds")

os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(JD_DIR, exist_ok=True)

# Specific key candidates for exact scenario reproduction
KEY_CANDIDATES = [
    {
        "id": "CAND-001",
        "name": "John Doe",
        "title": "Senior Frontend Engineer",
        "years_experience": 6.5,
        "location": "San Francisco, CA (Remote)",
        "skills": ["React", "TypeScript", "Next.js", "Redux", "GraphQL", "Tailwind CSS", "Jest", "CI/CD", "AWS", "Performance Optimization"],
        "education": "B.S. in Computer Science, University of California, Berkeley",
        "summary": "Accomplished Senior Frontend Engineer with 6.5 years of experience architecting large-scale React micro-frontends, high-throughput web apps, and design systems. Led a team of 5 engineers, cut page load times by 42%, and maintained 95%+ test coverage.",
        "experience": [
            {
                "company": "ScalePulse Tech",
                "role": "Lead Frontend Engineer",
                "duration": "2022 - Present",
                "highlights": [
                    "Engineered enterprise SaaS dashboard using React 18, TypeScript, and Next.js handling 1.2M daily active users.",
                    "Architected server-side rendering (SSR) and Edge caching strategy reducing Time to Interactive by 42%.",
                    "Mentored 5 junior/mid frontend engineers and drove modern React patterns and automated Jest/Playwright testing."
                ]
            },
            {
                "company": "Veloce Systems",
                "role": "Senior Frontend Developer",
                "duration": "2019 - 2022",
                "highlights": [
                    "Migrated monolithic frontend into modular React micro-frontends with Redux Toolkit and GraphQL Apollo Client.",
                    "Integrated AWS CloudFront CDN and automated GitHub Actions CI/CD pipelines."
                ]
            }
        ],
        "projects": [
            "React Design System Component Library adopted across 8 engineering squads.",
            "Open-source React performance profiler with 1.4k GitHub stars."
        ]
    },
    {
        "id": "CAND-002",
        "name": "Jane Smith",
        "title": "Frontend UI Developer",
        "years_experience": 3.5,
        "location": "Austin, TX (Hybrid)",
        "skills": ["React", "JavaScript (ES6+)", "HTML5", "CSS3/SASS", "Bootstrap", "REST APIs", "Git", "Webpack"],
        "education": "B.A. in Digital Media & Web Design, University of Texas at Austin",
        "summary": "Creative and diligent Frontend UI Developer with 3.5 years of experience building responsive, accessible web interfaces using React and modern CSS. Proven ability to translate Figma mockups into pixel-perfect components.",
        "experience": [
            {
                "company": "PixelCraft Studios",
                "role": "Frontend Developer",
                "duration": "2022 - Present",
                "highlights": [
                    "Developed responsive client portals using React and CSS Modules for mid-sized enterprise clients.",
                    "Collaborated closely with UX designers to implement WCAG 2.1 AA accessible UI elements.",
                    "Consumed RESTful endpoints and managed state using React Hooks and Context API."
                ]
            },
            {
                "company": "Hyperlink Digital",
                "role": "Junior Web Developer",
                "duration": "2020 - 2022",
                "highlights": [
                    "Built marketing landing pages and interactive forms using HTML5, SASS, and vanilla JavaScript.",
                    "Assisted in refactoring legacy jQuery widgets into reusable React components."
                ]
            }
        ],
        "projects": [
            "E-commerce product catalog with dynamic filtering and shopping cart in React.",
            "Personal UI component playground."
        ]
    },
    {
        "id": "CAND-003",
        "name": "Alex Rivera",
        "title": "Senior Full Stack Engineer",
        "years_experience": 5.0,
        "location": "New York, NY (Remote)",
        "skills": ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "AWS (S3, Lambda, ECS)", "Docker", "REST APIs", "Redis"],
        "education": "B.S. in Software Engineering, Rochester Institute of Technology",
        "summary": "Versatile Full Stack Engineer with 5 years building scalable web applications. Strong expertise in React frontend coupled with robust Node.js and AWS cloud infrastructure.",
        "experience": [
            {
                "company": "CloudForge Labs",
                "role": "Senior Full Stack Developer",
                "duration": "2021 - Present",
                "highlights": [
                    "Built real-time collaboration canvas using React, WebSockets, and Node.js microservices deployed on AWS ECS.",
                    "Designed relational database schemas in PostgreSQL with Redis caching layer, handling 5k req/sec.",
                    "Implemented end-to-end OAuth2 and JWT authentication flows."
                ]
            }
        ],
        "projects": [
            "Full-stack telemetry monitoring tool with React dashboard and Go/Node.js telemetry collector."
        ]
    },
    {
        "id": "CAND-004",
        "name": "Priya Sharma",
        "title": "Principal Cloud & Frontend Architect",
        "years_experience": 8.0,
        "location": "Seattle, WA (Remote)",
        "skills": ["React", "TypeScript", "AWS", "Kubernetes", "GraphQL", "Next.js", "Terraform", "System Architecture", "Kafka"],
        "education": "M.S. in Computer Science, University of Washington",
        "summary": "Seasoned Lead Cloud & Frontend Architect with 8 years architecting mission-critical cloud-native web systems. Deep mastery of AWS cloud governance, React microfrontends, and distributed resilience.",
        "experience": [
            {
                "company": "Apex Cloud Systems",
                "role": "Principal Solutions Engineer",
                "duration": "2020 - Present",
                "highlights": [
                    "Architected globally distributed cloud platform on AWS utilizing CloudFront, API Gateway, and React micro-frontends.",
                    "Reduced infrastructure costs by 35% through containerization and AWS Graviton migrations.",
                    "Formulated enterprise engineering standards and mentored 20+ software engineers across 4 squads."
                ]
            }
        ],
        "projects": [
            "Multi-tenant AWS infrastructure blueprint with automated Terraform provisioning and Next.js frontend."
        ]
    },
    {
        "id": "CAND-005",
        "name": "Marcus Vance",
        "title": "Junior Frontend Developer (Borderline Candidate)",
        "years_experience": 2.2,
        "location": "Denver, CO",
        "skills": ["React", "JavaScript", "HTML5", "CSS3", "Tailwind CSS", "Git"],
        "education": "Certificate in Full Stack Web Development, Flatiron School",
        "summary": "Enthusiastic junior frontend developer with 2.2 years of professional experience building web pages with React. Fast learner eager to bridge experience gaps in TypeScript and cloud systems.",
        "experience": [
            {
                "company": "MileHigh Digital",
                "role": "Junior Frontend Developer",
                "duration": "2023 - Present",
                "highlights": [
                    "Built 15+ marketing landing pages in React and Tailwind CSS.",
                    "Assisted in fixing bug tickets in React customer support dashboard."
                ]
            }
        ],
        "projects": [
            "Weather tracking progressive web app in React."
        ]
    }
]

FIRST_NAMES = [
    "Aaron", "Abigail", "Adam", "Aisha", "Alan", "Albert", "Alice", "Amanda", "Amber", "Amy",
    "Andrew", "Angela", "Anita", "Anthony", "Arjun", "Ashley", "Austin", "Barbara", "Benjamin", "Brandon",
    "Brian", "Brittany", "Carlos", "Catherine", "Charles", "Chloe", "Christopher", "Daniel", "David", "Derek",
    "Elena", "Emily", "Eric", "Ethan", "Fatima", "Gabriel", "Grace", "Hannah", "Hassan", "Heather",
    "Isaac", "Jack", "Jacob", "Jason", "Jeffrey", "Jennifer", "Jessica", "Jonathan", "Jordan", "Joseph",
    "Joshua", "Justin", "Karen", "Katherine", "Keith", "Kenneth", "Kevin", "Kimberly", "Kyle", "Laura",
    "Lauren", "Liam", "Logan", "Lucas", "Madeline", "Manuel", "Maria", "Matthew", "Megan", "Melissa",
    "Michael", "Michelle", "Nathan", "Nicholas", "Nicole", "Noah", "Olivia", "Patrick", "Paul", "Rachel",
    "Raymond", "Rebecca", "Richard", "Robert", "Ryan", "Samantha", "Samuel", "Sarah", "Sean", "Sophia",
    "Stephanie", "Steven", "Taylor", "Thomas", "Timothy", "Tyler", "Victoria", "William", "Zachary", "Zoe"
]

LAST_NAMES = [
    "Anderson", "Bailey", "Baker", "Barnes", "Bell", "Bennett", "Brooks", "Brown", "Campbell", "Carter",
    "Chen", "Clark", "Collins", "Cooper", "Cox", "Davis", "Diaz", "Edwards", "Evans", "Fisher",
    "Flores", "Foster", "Garcia", "Gomez", "Gonzalez", "Gray", "Green", "Gutierrez", "Hall", "Harris",
    "Hernandez", "Hill", "Howard", "Hughes", "Jackson", "James", "Jenkins", "Johnson", "Jones", "Kelly",
    "Kim", "King", "Lee", "Lewis", "Long", "Lopez", "Martin", "Martinez", "Miller", "Mitchell",
    "Moore", "Morales", "Morgan", "Morris", "Murphy", "Myers", "Nelson", "Nguyen", "Ortiz", "Parker",
    "Patel", "Perez", "Perry", "Peterson", "Phillips", "Price", "Ramirez", "Reed", "Reyes", "Richardson",
    "Rivera", "Roberts", "Robinson", "Rodriguez", "Rogers", "Ross", "Russell", "Sanchez", "Sanders", "Scott",
    "Smith", "Stewart", "Sullivan", "Taylor", "Thomas", "Thompson", "Torres", "Turner", "Walker", "Ward",
    "Washington", "Watson", "White", "Williams", "Wilson", "Wood", "Wright", "Young", "Zhang", "Zimmerman"
]

ROLES_CONFIG = [
    {
        "domain": "Frontend",
        "titles": ["Frontend Engineer", "Senior Frontend Engineer", "Staff UI Architect", "Web Applications Engineer"],
        "core_skills": [["React", "TypeScript", "Next.js", "Redux", "Tailwind CSS"], ["React", "JavaScript", "HTML5", "CSS3", "REST APIs"], ["Vue.js", "JavaScript", "Nuxt", "Vuex", "CSS3"], ["Angular", "TypeScript", "RxJS", "SCSS", "Jest"]],
        "cloud_skills": ["AWS", "Vercel", "Docker", "Firebase", "Netlify"],
        "base_exp_range": (2.0, 9.0)
    },
    {
        "domain": "Full Stack",
        "titles": ["Full Stack Engineer", "Senior Full Stack Developer", "Software Engineer - Web Systems"],
        "core_skills": [["React", "Node.js", "TypeScript", "PostgreSQL", "Docker"], ["React", "Python", "FastAPI", "MongoDB", "AWS"], ["Angular", "Java", "Spring Boot", "MySQL", "Docker"], ["Vue.js", "Django", "PostgreSQL", "Redis", "GCP"]],
        "cloud_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Redis"],
        "base_exp_range": (3.0, 10.0)
    },
    {
        "domain": "Backend",
        "titles": ["Backend Engineer", "Senior Distributed Systems Engineer", "API Platform Engineer"],
        "core_skills": [["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka"], ["Go", "gRPC", "Docker", "Kubernetes", "PostgreSQL"], ["Java", "Spring Boot", "Microservices", "Kafka", "AWS"], ["Node.js", "Express", "TypeScript", "MongoDB", "RabbitMQ"]],
        "cloud_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Prometheus"],
        "base_exp_range": (2.5, 11.0)
    },
    {
        "domain": "DevOps/Cloud",
        "titles": ["DevOps Engineer", "Site Reliability Engineer (SRE)", "Cloud Infrastructure Engineer"],
        "core_skills": [["AWS", "Terraform", "Kubernetes", "Docker", "CI/CD", "Python"], ["GCP", "Kubernetes", "Helm", "Ansible", "Bash", "Prometheus"], ["Azure", "Terraform", "GitHub Actions", "Docker", "PowerShell"]],
        "cloud_skills": ["AWS", "Linux", "Terraform", "Kubernetes", "Monitoring"],
        "base_exp_range": (3.0, 12.0)
    },
    {
        "domain": "Data/AI",
        "titles": ["Machine Learning Engineer", "Data Engineer", "AI Applications Developer"],
        "core_skills": [["Python", "PyTorch", "LangChain", "Vector DBs", "FastAPI", "Docker"], ["Python", "Spark", "SQL", "Airflow", "Snowflake", "AWS"], ["Python", "Scikit-Learn", "Pandas", "NLP", "MLflow"]],
        "cloud_skills": ["AWS S3", "SageMaker", "Docker", "Snowflake", "Databricks"],
        "base_exp_range": (2.0, 8.5)
    }
]

UNIVERSITIES = [
    "Stanford University", "MIT", "Carnegie Mellon University", "UC Berkeley", "Georgia Tech",
    "University of Texas at Austin", "University of Illinois Urbana-Champaign", "University of Michigan",
    "Cornell University", "Purdue University", "University of Washington", "New York University"
]

COMPANIES = [
    "Nexora Tech", "Acrobyte Data", "Vertex Cloud Solutions", "Optima Health Tech", "Finova Digital",
    "Kinetic Systems", "BlueHarbor Software", "StrataCore Inc.", "InnoVibe Labs", "CipherWave Networks",
    "OmniPlatform Systems", "PulsePoint Media", "Zenith Financial Technologies", "Skyline Analytics"
]

def generate_100_resumes():
    all_candidates = []
    
    # Add explicit key candidates first (5 candidates)
    all_candidates.extend(KEY_CANDIDATES)
    
    random.seed(42)  # Deterministic generation
    
    for idx in range(6, 101):
        cand_id = f"CAND-{idx:03d}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        # Pick a domain with slight frontend bias to ensure competitive React candidate pool
        domain_weights = [0.35, 0.25, 0.15, 0.15, 0.10]
        cfg = random.choices(ROLES_CONFIG, weights=domain_weights, k=1)[0]
        
        title = random.choice(cfg["titles"])
        exp = round(random.uniform(cfg["base_exp_range"][0], cfg["base_exp_range"][1]), 1)
        
        # Core skill set
        chosen_core = list(random.choice(cfg["core_skills"]))
        # Additional cloud / extra skill
        extra = random.sample(cfg["cloud_skills"], k=random.randint(1, 2))
        skills = list(dict.fromkeys(chosen_core + extra))
        
        # Random location
        loc = random.choice(["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Boston, MA", "Chicago, IL", "Remote - US", "Denver, CO"])
        edu = f"{random.choice(['B.S.', 'M.S.'])} in {random.choice(['Computer Science', 'Software Engineering', 'Information Technology', 'Data Science'])}, {random.choice(UNIVERSITIES)}"
        
        comp1 = random.choice(COMPANIES)
        comp2 = random.choice([c for c in COMPANIES if c != comp1])
        
        summary = (
            f"Results-oriented {title} with {exp} years of industry experience specializing in {', '.join(skills[:3])}. "
            f"Proven track record delivering reliable software systems and collaborating in Agile teams."
        )
        
        experience = [
            {
                "company": comp1,
                "role": title,
                "duration": "2022 - Present",
                "highlights": [
                    f"Designed and maintained enterprise web features utilizing {skills[0]} and {skills[1]}.",
                    f"Collaborated with cross-functional product and engineering teams to enhance performance and UX.",
                    f"Automated unit testing and CI/CD pipelines to ensure code stability and release frequency."
                ]
            },
            {
                "company": comp2,
                "role": f"Associate {title}",
                "duration": "2019 - 2022" if exp > 4 else "2021 - 2022",
                "highlights": [
                    f"Contributed to core product development with {skills[min(2, len(skills)-1)]}.",
                    "Wrote unit tests and resolved critical customer defect tickets."
                ]
            }
        ]
        
        projects = [
            f"Built scalable {skills[0]} architecture reducing end-to-end latency by {random.randint(15, 45)}%.",
            f"Engineered microservices toolset integrating {skills[1]} with cloud monitoring."
        ]
        
        cand = {
            "id": cand_id,
            "name": name,
            "title": title,
            "years_experience": exp,
            "location": loc,
            "skills": skills,
            "education": edu,
            "summary": summary,
            "experience": experience,
            "projects": projects
        }
        all_candidates.append(cand)
        
    # Write JSON and Markdown resumes
    with open(os.path.join(RESUME_DIR, "all_resumes.json"), "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, indent=2)
        
    for cand in all_candidates:
        file_path = os.path.join(RESUME_DIR, f"{cand['id']}.md")
        content = f"""# {cand['name']}
**Candidate ID:** {cand['id']}
**Current Title:** {cand['title']}
**Experience:** {cand['years_experience']} years
**Location:** {cand['location']}
**Education:** {cand['education']}

## Skills
{', '.join(cand['skills'])}

## Professional Summary
{cand['summary']}

## Work Experience
"""
        for exp in cand['experience']:
            content += f"\n### {exp['role']} - {exp['company']} ({exp['duration']})\n"
            for hl in exp['highlights']:
                content += f"- {hl}\n"
                
        content += "\n## Key Projects\n"
        for p in cand['projects']:
            content += f"- {p}\n"
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Generated {len(all_candidates)} resumes in {RESUME_DIR}")
    return all_candidates

def generate_sample_jds():
    jds = {
        "senior_react_developer": {
            "id": "JD-001",
            "title": "Senior React Developer",
            "department": "Frontend Engineering",
            "raw_text": """Job Title: Senior React Developer
Location: Remote (US)
Experience Required: 3+ years (Senior: 5+ years preferred)

About the Role:
We are looking for a Senior React Developer to join our core product team. You will be responsible for architecting and building high-performance, user-friendly frontend web applications, leading frontend modernization efforts, and mentoring other engineers.

Must-Have Requirements:
- At least 3+ years of professional software development experience with strong focus on React.
- Deep expertise in React (v17/18), modern JavaScript/TypeScript, and state management (Redux, Zustand, or Context API).
- Experience building responsive, accessible, and high-performance web user interfaces.
- Familiarity with modern frontend tooling, automated testing (Jest, React Testing Library), and REST / GraphQL APIs.
- Strong team collaboration, communication, and code review practices.

Nice-to-Have Requirements:
- 5+ years of software engineering experience.
- Experience with Next.js, Server-Side Rendering (SSR), or static site generation.
- Hands-on cloud experience with AWS (S3, CloudFront, Lambda) and CI/CD pipelines.
- Experience with micro-frontends and design system component libraries.
- Proven track record mentoring junior and mid-level developers."""
        },
        "fullstack_cloud_engineer": {
            "id": "JD-002",
            "title": "Full Stack Cloud Engineer",
            "department": "Platform Engineering",
            "raw_text": """Job Title: Full Stack Cloud Engineer
Location: Remote or Hybrid
Experience Required: 4+ years

Must-Have Requirements:
- 4+ years full stack development experience with React and Node.js or Python.
- Proven experience with AWS cloud infrastructure (ECS, Lambda, S3, RDS).
- Strong database skills with PostgreSQL or MySQL and Docker containerization.
- Experience building and consuming RESTful and GraphQL APIs.

Nice-to-Have Requirements:
- Experience with Kubernetes and Terraform infrastructure-as-code.
- Knowledge of Redis caching and message queues (Kafka or RabbitMQ).
- Microservices architectural design patterns."""
        },
        "ml_ai_engineer": {
            "id": "JD-003",
            "title": "AI / Machine Learning Engineer",
            "department": "AI Innovation",
            "raw_text": """Job Title: AI / Machine Learning Engineer
Experience Required: 3+ years

Must-Have Requirements:
- 3+ years Python experience in machine learning or AI application development.
- Hands-on experience with PyTorch, Scikit-Learn, or Hugging Face Transformers.
- Experience with LLM orchestration (LangChain, LangGraph, or LlamaIndex) and Vector DBs.
- Strong understanding of REST APIs, FastAPI, and Docker.

Nice-to-Have Requirements:
- Experience deploying ML models to AWS SageMaker or Kubernetes.
- Experience with agentic workflows and multi-step reasoning systems."""
        }
    }
    
    for key, data in jds.items():
        with open(os.path.join(JD_DIR, f"{key}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        with open(os.path.join(JD_DIR, f"{key}.txt"), "w", encoding="utf-8") as f:
            f.write(data["raw_text"])
            
    print(f"Generated {len(jds)} sample JDs in {JD_DIR}")

if __name__ == "__main__":
    generate_100_resumes()
    generate_sample_jds()
