"""
Unit tests for services/skill_extractor.py
Tests skill extraction, keyword extraction, and normalization.
"""

from django.test import TestCase
from services.skill_extractor import (
    extract_skills,
    extract_keywords,
    normalize_skills,
    _fallback_skill_extract,
)


class TestExtractSkills(TestCase):

    def test_extracts_python(self):
        text = "We need a Python developer with Django experience."
        result = extract_skills(text)
        self.assertIn('python', result)

    def test_extracts_multiple_skills(self):
        text = "Skills required: Python, Django, PostgreSQL, Docker, AWS"
        result = extract_skills(text)
        self.assertIn('python', result)
        self.assertIn('django', result)
        self.assertIn('postgresql', result)

    def test_returns_list(self):
        result = extract_skills("Python developer")
        self.assertIsInstance(result, list)

    def test_empty_text_returns_empty(self):
        result = extract_skills("")
        self.assertEqual(result, [])

    def test_none_returns_empty(self):
        result = extract_skills(None)
        self.assertEqual(result, [])

    def test_no_skills_in_text(self):
        text = "We are looking for a passionate team player."
        result = extract_skills(text)
        self.assertIsInstance(result, list)

    def test_results_are_lowercase(self):
        text = "Proficiency in PYTHON and DJANGO required."
        result = extract_skills(text)
        for skill in result:
            self.assertEqual(skill, skill.lower())

    def test_results_are_sorted(self):
        text = "Python, Django, AWS, Docker, PostgreSQL"
        result = extract_skills(text)
        self.assertEqual(result, sorted(result))

    def test_no_duplicates(self):
        text = "Python Python Python Django Django"
        result = extract_skills(text)
        self.assertEqual(len(result), len(set(result)))

    def test_machine_learning_phrase(self):
        text = "Experience with machine learning and deep learning required."
        result = extract_skills(text)
        self.assertIn('machine learning', result)


class TestFallbackSkillExtract(TestCase):

    def test_finds_python(self):
        text = "Strong Python programming skills required."
        result = _fallback_skill_extract(text)
        self.assertIn('python', result)

    def test_finds_docker(self):
        text = "Experience with Docker and Kubernetes."
        result = _fallback_skill_extract(text)
        self.assertIn('docker', result)

    def test_empty_text(self):
        result = _fallback_skill_extract("")
        self.assertEqual(result, [])


class TestExtractKeywords(TestCase):

    def test_returns_list(self):
        text = "Python developer with Django and PostgreSQL experience."
        result = extract_keywords(text)
        self.assertIsInstance(result, list)

    def test_empty_text_returns_empty(self):
        result = extract_keywords("")
        self.assertEqual(result, [])

    def test_respects_top_n(self):
        text = " ".join(["word" + str(i) for i in range(100)])
        result = extract_keywords(text, top_n=10)
        self.assertLessEqual(len(result), 10)

    def test_no_stopwords(self):
        text = (
            "The candidate should have strong experience with "
            "Python and Django framework for building web applications."
        )
        result = extract_keywords(text)
        stopwords = {'the', 'and', 'for', 'with'}
        for kw in result:
            self.assertNotIn(kw.lower(), stopwords)


class TestNormalizeSkills(TestCase):

    def test_lowercases_skills(self):
        skills = ['Python', 'DJANGO', 'PostgreSQL']
        result = normalize_skills(skills)
        self.assertIn('python', result)
        self.assertIn('django', result)
        self.assertIn('postgresql', result)

    def test_strips_whitespace(self):
        skills = ['  python  ', 'django ']
        result = normalize_skills(skills)
        self.assertIn('python', result)
        self.assertIn('django', result)

    def test_removes_empty_strings(self):
        skills = ['python', '', '  ', 'django']
        result = normalize_skills(skills)
        self.assertNotIn('', result)

    def test_returns_set(self):
        result = normalize_skills(['python', 'django'])
        self.assertIsInstance(result, set)

    def test_deduplicates(self):
        skills = ['python', 'Python', 'PYTHON']
        result = normalize_skills(skills)
        self.assertEqual(len(result), 1)
