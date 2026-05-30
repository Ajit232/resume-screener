import logging
logger = logging.getLogger(__name__)

def generate_suggestions(missing_skills, missing_keywords, skill_score, keyword_score, experience_score, education_score, final_score, jd_title=""):
    suggestions = []
    if missing_skills:
        skills_str = ", ".join(missing_skills[:5])
        suggestions.append(f"Add these missing skills to your resume: {skills_str}. If you have experience with them make sure they are explicitly mentioned.")
    if skill_score < 40:
        suggestions.append("Your skill match is low. Review the job description carefully and add all relevant technical skills you possess.")
    elif skill_score < 70:
        suggestions.append("Consider adding more skills to your resume. Focus on the specific tools and technologies mentioned in the job description.")
    if missing_keywords:
        kw_str = ", ".join(missing_keywords[:5])
        suggestions.append(f"Include these keywords from the job description in your resume: {kw_str}.")
    if keyword_score < 50:
        suggestions.append("Your resume is missing many keywords from the job description. Mirror the language used in the job posting.")
    if experience_score < 60:
        suggestions.append("Highlight your years of experience more clearly. Use phrases like X years of experience in... at the start of your summary.")
    if education_score < 60:
        suggestions.append("The job requires a higher level of education than detected in your resume. Make sure your education section is clearly listed.")
    if final_score < 40:
        suggestions.append(f"Your overall match is low. Consider tailoring your resume specifically for this {jd_title} role.")
    suggestions.append("Use strong action verbs such as built, designed, implemented, led, and optimised when describing your work experience.")
    suggestions.append("Quantify your achievements where possible for example Reduced API response time by 40% or Managed a team of 5 engineers.")
    return suggestions
