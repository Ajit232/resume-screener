import re
import logging
logger = logging.getLogger(__name__)

EDUCATION_PATTERNS = {
    "phd": [r"\bph\.?d\b", r"\bdoctorate\b", r"\bdoctoral\b"],
    "master": [r"\bmaster.?s?\b", r"\bm\.s\.?\b", r"\bmba\b", r"\bpostgraduate\b"],
    "bachelor": [r"\bbachelor.?s?\b", r"\bb\.s\.?\b", r"\bb\.tech\b", r"\bdegree\b", r"\bundergraduate\b"],
    "diploma": [r"\bdiploma\b", r"\bcertificate\b"],
}

EDUCATION_TIER = {"phd": 4, "master": 3, "bachelor": 2, "diploma": 1, "": 0, "any": 0}

def extract_experience_requirement(text):
    patterns = [
        r"(\d+)\s*[-]\s*(\d+)\s*\+?\s*years?",
        r"(\d+)\s*\+\s*years?",
        r"at\s*least\s*(\d+)\s*years?",
        r"minimum\s*of\s*(\d+)\s*years?",
        r"(\d+)\s*years?\s*of\s*experience",
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0).strip()
    return ""

def extract_education_requirement(text):
    text_lower = text.lower()
    found_tier = ""
    found_level = 0
    for tier, patterns in EDUCATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                if EDUCATION_TIER[tier] > found_level:
                    found_level = EDUCATION_TIER[tier]
                    found_tier = tier
                break
    return found_tier

def extract_requirement_sentences(text):
    keywords = ["required", "must have", "should have", "experience with", "proficiency in", "knowledge of"]
    sentences = []
    lines = re.split(r"[\n\r]+", text)
    for line in lines:
        line = line.strip()
        line = re.sub(r"^[\u2022\*\-\+]\s*", "", line)
        if len(line) < 10:
            continue
        line_lower = line.lower()
        for kw in keywords:
            if kw in line_lower:
                sentences.append(line)
                break
    return sentences[:20]

def parse_jd(text):
    return {
        "experience_required": extract_experience_requirement(text),
        "education_required": extract_education_requirement(text),
        "requirement_sentences": extract_requirement_sentences(text),
    }

def extract_years_as_int(experience_str):
    if not experience_str:
        return 0
    numbers = re.findall(r"\d+", experience_str)
    if numbers:
        return int(numbers[0])
    return 0
