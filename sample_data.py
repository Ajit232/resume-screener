"""
Run this script to insert sample data into the database.

Usage:
    python manage.py shell < sample_data.py

Or copy-paste into the Django shell:
    python manage.py shell
"""

from django.contrib.auth.models import User
from jobs.models import JobDescription
from resumes.models import Resume
from analysis.models import AnalysisResult

print("Creating sample data...")

# -------------------------------------------------------------------
# 1. Create demo user (skip if already exists)
# -------------------------------------------------------------------
user, created = User.objects.get_or_create(
    username='demo',
    defaults={
        'email': 'demo@resumeai.com',
        'first_name': 'Demo',
        'last_name': 'User',
    }
)
if created:
    user.set_password('Demo@1234')
    user.save()
    print(f"Created user: demo / Demo@1234")
else:
    print(f"User 'demo' already exists — skipping.")

# -------------------------------------------------------------------
# 2. Sample Job Descriptions
# -------------------------------------------------------------------

jd1_text = """
We are looking for a Senior Python Developer to join our backend team.

Requirements:
- 3-5 years of experience with Python
- Strong knowledge of Django or Flask web frameworks
- Experience with PostgreSQL and Redis
- Proficiency in REST API design and development
- Experience with Docker and Kubernetes
- Familiarity with AWS or GCP cloud platforms
- Knowledge of Git version control
- Experience with CI/CD pipelines
- Strong problem solving and communication skills
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Design and implement scalable backend services
- Write clean, maintainable, and well-tested code
- Collaborate with frontend and DevOps teams
- Participate in code reviews and architecture discussions
- Optimise application performance and reliability
"""

jd2_text = """
Data Scientist - Machine Learning Engineer

We are hiring a Data Scientist with strong machine learning skills.

Requirements:
- 2+ years of experience in data science or machine learning
- Proficiency in Python with pandas, numpy, scikit-learn
- Experience with TensorFlow or PyTorch
- Knowledge of NLP and computer vision techniques
- Strong understanding of statistics and probability
- Experience with SQL and data warehousing
- Familiarity with Spark and big data tools
- Ability to communicate complex findings clearly
- Master's degree in Computer Science, Statistics, or related field

Nice to have:
- Experience with MLOps and model deployment
- Knowledge of Tableau or Power BI for data visualization
- Experience with cloud platforms AWS or Azure
"""

jd3_text = """
Full Stack JavaScript Developer

Join our product team as a Full Stack Developer.

Requirements:
- 3+ years of experience in full stack development
- Strong proficiency in JavaScript and TypeScript
- Experience with React or Angular frontend frameworks
- Backend experience with Node.js or Express
- Knowledge of SQL and MongoDB databases
- Experience with REST and GraphQL APIs
- Familiarity with Docker and CI/CD
- Experience with Git and GitHub
- Strong teamwork and communication skills
- Bachelor's degree preferred
"""

jds = [
    ('Senior Python Developer', 'TechCorp Ltd', jd1_text),
    ('Data Scientist', 'DataInsights Inc', jd2_text),
    ('Full Stack Developer', 'WebSolutions Co', jd3_text),
]

created_jds = []
for title, company, text in jds:
    if not JobDescription.objects.filter(user=user, title=title).exists():
        from services.skill_extractor import extract_skills, extract_keywords
        from services.parser import parse_jd

        parsed = parse_jd(text)
        skills = extract_skills(text)
        keywords = extract_keywords(text, top_n=25)

        jd = JobDescription.objects.create(
            user=user,
            title=title,
            company=company,
            raw_text=text.strip(),
            parsed_skills=skills,
            parsed_keywords=keywords,
            experience_required=parsed['experience_required'],
            education_required=parsed['education_required'],
        )
        created_jds.append(jd)
        print(f"Created JD: {title} ({len(skills)} skills extracted)")
    else:
        jd = JobDescription.objects.get(user=user, title=title)
        created_jds.append(jd)
        print(f"JD '{title}' already exists — skipping.")

# -------------------------------------------------------------------
# 3. Sample Resumes
# -------------------------------------------------------------------

resume1_text = """
John Smith
john.smith@email.com | linkedin.com/in/johnsmith | github.com/johnsmith

PROFESSIONAL SUMMARY
Results-driven Python developer with 4 years of experience building scalable
web applications using Django and Flask. Strong background in PostgreSQL,
Docker, and REST API development. Passionate about clean code and best practices.

SKILLS
Python, Django, Flask, FastAPI, PostgreSQL, Redis, Docker, Kubernetes,
AWS, Git, GitHub, REST API, CI/CD, Jenkins, Linux, Agile, Scrum

EXPERIENCE

Senior Python Developer — TechStartup Inc (2022 - Present)
- Built and maintained Django REST APIs serving 50,000+ daily users
- Implemented Redis caching reducing response times by 60%
- Deployed microservices using Docker and Kubernetes on AWS
- Led a team of 3 developers on a critical payment processing module
- Wrote comprehensive unit tests achieving 90% code coverage

Python Developer — WebAgency Ltd (2020 - 2022)
- Developed Flask applications for client projects
- Designed PostgreSQL database schemas for e-commerce platforms
- Integrated third-party REST APIs including Stripe and Twilio
- Set up CI/CD pipelines using Jenkins and GitHub Actions

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2020

CERTIFICATIONS
- AWS Certified Developer Associate
- Docker Certified Associate
"""

resume2_text = """
Sarah Johnson
sarah.j@email.com | linkedin.com/in/sarahjohnson

SUMMARY
Data scientist with 3 years of experience in machine learning and NLP.
Skilled in Python, TensorFlow, and scikit-learn. Experienced in building
end-to-end ML pipelines and deploying models to production.

SKILLS
Python, pandas, numpy, scikit-learn, TensorFlow, PyTorch, NLP,
machine learning, deep learning, SQL, PostgreSQL, Spark, Tableau,
Git, Docker, AWS, statistics, data analysis

EXPERIENCE

Data Scientist — Analytics Corp (2022 - Present)
- Built NLP models for sentiment analysis with 92% accuracy
- Developed machine learning pipelines processing 1M+ records daily
- Created Tableau dashboards for business intelligence reporting
- Collaborated with engineering teams to deploy models on AWS

Junior Data Analyst — DataFirm (2021 - 2022)
- Analysed large datasets using pandas and numpy
- Built predictive models using scikit-learn
- Wrote SQL queries for data extraction and transformation

EDUCATION
Master of Science in Data Science
State University, 2021

Bachelor of Science in Mathematics
State University, 2019
"""

resumes_data = [
    ('John Smith - Python Developer', resume1_text),
    ('Sarah Johnson - Data Scientist', resume2_text),
]

created_resumes = []
for title, text in resumes_data:
    if not Resume.objects.filter(user=user, title=title).exists():
        resume = Resume.objects.create(
            user=user,
            title=title,
            raw_text=text.strip(),
            version=1,
        )
        created_resumes.append(resume)
        print(f"Created resume: {title} ({resume.word_count()} words)")
    else:
        resume = Resume.objects.get(user=user, title=title)
        created_resumes.append(resume)
        print(f"Resume '{title}' already exists — skipping.")

# -------------------------------------------------------------------
# 4. Sample Analysis Results
# -------------------------------------------------------------------

if created_jds and created_resumes:
    from services.skill_extractor import extract_skills, extract_keywords
    from services.scorer import run_full_scoring
    from services.recommender import generate_suggestions

    pairs = [
        (created_resumes[0], created_jds[0]),  # Python dev vs Python JD
        (created_resumes[1], created_jds[1]),  # Data scientist vs DS JD
        (created_resumes[0], created_jds[2]),  # Python dev vs JS JD (mismatch)
    ]

    for resume, jd in pairs:
        if AnalysisResult.objects.filter(user=user, resume=resume, job_description=jd).exists():
            print(f"Analysis {resume.title} vs {jd.title} already exists — skipping.")
            continue

        resume_skills = extract_skills(resume.raw_text)

        scores = run_full_scoring(
            resume_text=resume.raw_text,
            resume_skills=resume_skills,
            jd_text=jd.raw_text,
            jd_skills=jd.parsed_skills,
            jd_keywords=jd.parsed_keywords,
            jd_experience_required=jd.experience_required,
            jd_education_required=jd.education_required,
        )

        suggestions = generate_suggestions(
            missing_skills=scores['missing_skills'],
            missing_keywords=scores['missing_keywords'],
            skill_score=scores['skill_match_score'],
            keyword_score=scores['keyword_match_score'],
            experience_score=scores['experience_score'],
            education_score=scores['education_score'],
            final_score=scores['final_score'],
            jd_title=jd.title,
        )

        result = AnalysisResult.objects.create(
            user=user,
            resume=resume,
            job_description=jd,
            skill_match_score=scores['skill_match_score'],
            keyword_match_score=scores['keyword_match_score'],
            experience_score=scores['experience_score'],
            education_score=scores['education_score'],
            final_score=scores['final_score'],
            matched_skills=scores['matched_skills'],
            missing_skills=scores['missing_skills'],
            matched_keywords=scores['matched_keywords'],
            missing_keywords=scores['missing_keywords'],
            suggestions=suggestions,
        )
        print(f"Created analysis: {resume.title} vs {jd.title} — Score: {result.final_score:.1f}% ({result.get_label()})")

print("\nSample data created successfully!")
print("Login with: username=demo  password=Demo@1234")
