import re
import logging
logger = logging.getLogger(__name__)

SKILL_WEIGHT      = 0.40
KEYWORD_WEIGHT    = 0.25
EXPERIENCE_WEIGHT = 0.20
EDUCATION_WEIGHT  = 0.15

EDUCATION_TIER = {"phd":4,"master":3,"bachelor":2,"diploma":1,"":0,"any":0}

def compute_skill_match(resume_skills, jd_skills):
    if not jd_skills:
        return {"score":0.0,"matched":[],"missing":[]}
    resume_set = {s.lower().strip() for s in resume_skills}
    jd_set     = {s.lower().strip() for s in jd_skills}
    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    score   = (len(matched) / len(jd_set)) * 100.0
    return {"score":round(score,2),"matched":matched,"missing":missing}

def compute_keyword_match(resume_text, jd_keywords):
    if not jd_keywords or not resume_text:
        return {"score":0.0,"matched":[],"missing":[]}
    resume_lower = resume_text.lower()
    matched, missing = [], []
    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            matched.append(kw)
        else:
            missing.append(kw)
    score = (len(matched) / len(jd_keywords)) * 100.0
    return {"score":round(score,2),"matched":matched,"missing":missing}

def compute_experience_score(resume_text, required_experience_str):
    if not required_experience_str:
        return 100.0
    req_numbers = re.findall(r"\d+", required_experience_str)
    if not req_numbers:
        return 100.0
    required_years = int(req_numbers[0])
    if required_years == 0:
        return 100.0
    candidate_years = _extract_years_from_resume(resume_text)
    if candidate_years == 0:
        return 40.0
    ratio = min(candidate_years / required_years, 1.0)
    return round(ratio * 100.0, 2)

def compute_education_score(resume_text, required_education):
    if not required_education or required_education in ("","any"):
        return 100.0
    required_tier  = EDUCATION_TIER.get(required_education.lower(), 0)
    candidate_tier = _extract_education_from_resume(resume_text)
    if candidate_tier >= required_tier:
        return 100.0
    elif candidate_tier == required_tier - 1:
        return 60.0
    elif candidate_tier == required_tier - 2:
        return 30.0
    return 0.0

def compute_final_score(skill_score, keyword_score, experience_score, education_score):
    final = (skill_score * SKILL_WEIGHT + keyword_score * KEYWORD_WEIGHT +
             experience_score * EXPERIENCE_WEIGHT + education_score * EDUCATION_WEIGHT)
    return round(min(final, 100.0), 2)

def run_full_scoring(resume_text, resume_skills, jd_text, jd_skills, jd_keywords, jd_experience_required, jd_education_required):
    skill_result   = compute_skill_match(resume_skills, jd_skills)
    keyword_result = compute_keyword_match(resume_text, jd_keywords)
    exp_score      = compute_experience_score(resume_text, jd_experience_required)
    edu_score      = compute_education_score(resume_text, jd_education_required)
    final          = compute_final_score(skill_result["score"], keyword_result["score"], exp_score, edu_score)
    return {
        "skill_match_score":    skill_result["score"],
        "keyword_match_score":  keyword_result["score"],
        "experience_score":     exp_score,
        "education_score":      edu_score,
        "final_score":          final,
        "matched_skills":       skill_result["matched"],
        "missing_skills":       skill_result["missing"],
        "matched_keywords":     keyword_result["matched"],
        "missing_keywords":     keyword_result["missing"],
    }

def _extract_years_from_resume(text):
    patterns = [r"(\d+)\s*\+?\s*years?\s*of\s*experience", r"(\d+)\s*\+?\s*years?\s*experience", r"(\d+)\s*\+\s*years?"]
    text_lower = text.lower()
    found_years = []
    for pattern in patterns:
        for m in re.findall(pattern, text_lower):
            try:
                found_years.append(int(m))
            except:
                pass
    return max(found_years) if found_years else 0

def _extract_education_from_resume(text):
    from services.parser import EDUCATION_PATTERNS, EDUCATION_TIER
    text_lower = text.lower()
    max_tier = 0
    for tier, patterns in EDUCATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                tier_val = EDUCATION_TIER.get(tier, 0)
                if tier_val > max_tier:
                    max_tier = tier_val
                break
    return max_tier
