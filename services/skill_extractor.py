import re
import logging
logger = logging.getLogger(__name__)

SKILLS_LIST = [
    "python","java","javascript","typescript","c++","c#","go","rust","kotlin","swift","ruby","php","scala","r","bash",
    "django","flask","fastapi","express","react","angular","vue","spring","spring boot","laravel","rails","node.js",
    "sql","mysql","postgresql","postgres","sqlite","mongodb","redis","cassandra","dynamodb","firebase","elasticsearch",
    "aws","azure","gcp","docker","kubernetes","terraform","ansible","jenkins","linux","unix",
    "machine learning","deep learning","nlp","natural language processing","computer vision",
    "tensorflow","pytorch","keras","scikit-learn","pandas","numpy","matplotlib","spark","hadoop","tableau","power bi",
    "rest","graphql","microservices","api","jwt","oauth",
    "git","github","gitlab","jira","agile","scrum","tdd","ci/cd","devops","selenium","pytest","postman",
    "communication","teamwork","leadership","problem solving","project management",
]

SKILLS_SET = {s.lower() for s in SKILLS_LIST}
_nlp = None
_matcher = None

def _get_nlp():
    global _nlp, _matcher
    if _nlp is None:
        try:
            import spacy
            from spacy.matcher import PhraseMatcher
            _nlp = spacy.load("en_core_web_sm")
            _matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
            patterns = [_nlp.make_doc(skill) for skill in SKILLS_LIST]
            _matcher.add("SKILLS", patterns)
        except Exception as e:
            logger.error(f"spaCy load error: {e}")
            _nlp = None
            _matcher = None
    return _nlp, _matcher

def extract_skills(text):
    if not text:
        return []
    nlp, matcher = _get_nlp()
    if nlp is None or matcher is None:
        return _fallback_skill_extract(text)
    try:
        doc = nlp(text[:100000])
        matches = matcher(doc)
        found = set()
        for match_id, start, end in matches:
            found.add(doc[start:end].text.lower())
        return sorted(found)
    except Exception as e:
        logger.error(f"Skill extraction error: {e}")
        return _fallback_skill_extract(text)

def extract_keywords(text, top_n=30):
    if not text:
        return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        sentences = re.split(r"[.\n]", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        if len(sentences) < 2:
            return _frequency_keywords(text, top_n)
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words="english", ngram_range=(1,2), min_df=1)
        vectorizer.fit_transform(sentences)
        return sorted(vectorizer.get_feature_names_out().tolist())
    except Exception as e:
        logger.error(f"Keyword extraction error: {e}")
        return _frequency_keywords(text, top_n)

def _fallback_skill_extract(text):
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_LIST:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(found)

def _frequency_keywords(text, top_n):
    from collections import Counter
    STOPWORDS = {"the","and","for","with","this","that","are","you","will","have","from","our","not","but","was","all","can","been","has","its","their","also"}
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    counter = Counter(filtered)
    return [word for word, _ in counter.most_common(top_n)]

def normalize_skills(skills):
    return {s.lower().strip() for s in skills if s and s.strip()}