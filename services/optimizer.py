import re
import logging
logger = logging.getLogger(__name__)

WEAK_VERBS = {
    "worked on": "developed", "helped with": "contributed to",
    "was part of": "collaborated on", "did": "executed",
    "made": "built", "used": "implemented", "handled": "managed",
    "responsible for": "owned", "in charge of": "led",
}

def optimize_resume(resume_text, missing_skills, jd_title, matched_skills):
    if not resume_text:
        return resume_text
    optimized = _replace_weak_verbs(resume_text)
    if not _has_summary(optimized):
        summary = _generate_summary(jd_title, matched_skills)
        optimized = summary + "\n\n" + optimized
    if missing_skills:
        optimized = _inject_missing_skills(optimized, missing_skills)
    return optimized

def _replace_weak_verbs(text):
    for weak, strong in WEAK_VERBS.items():
        pattern = re.compile(re.escape(weak), re.IGNORECASE)
        text = pattern.sub(strong, text)
    return text

def _has_summary(text):
    for pattern in [r"\bsummary\b", r"\bprofile\b", r"\bobjective\b"]:
        if re.search(pattern, text.lower()):
            return True
    return False

def _generate_summary(jd_title, matched_skills):
    skills_str = ", ".join(matched_skills[:4]) if matched_skills else "relevant technologies"
    title = jd_title if jd_title else "the role"
    return (f"PROFESSIONAL SUMMARY\nResults-driven professional with hands-on experience in {skills_str}. "
            f"Seeking to leverage my technical skills in a {title} position. "
            f"Proven ability to deliver high-quality solutions in fast-paced environments.")

def _inject_missing_skills(text, missing_skills):
    skills_to_add = ", ".join(s.title() for s in missing_skills[:8])
    for pattern in [r"(skills\s*[:]?\s*)(.*?)(\n\n|\Z)", r"(technical skills\s*[:]?\s*)(.*?)(\n\n|\Z)"]:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            updated = match.group(2).strip() + ", " + skills_to_add
            text = text[:match.start(2)] + updated + text[match.end(2):]
            return text
    text += f"\n\nSKILLS\n{skills_to_add}"
    return text
