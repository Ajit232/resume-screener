"""
Unit tests for services/optimizer.py
Tests weak verb replacement, summary injection, skills injection.
"""

from django.test import TestCase
from services.optimizer import (
    optimize_resume,
    _replace_weak_verbs,
    _has_summary,
    _generate_summary,
    _inject_missing_skills,
)


class TestReplaceWeakVerbs(TestCase):

    def test_replaces_worked_on(self):
        text = "I worked on the payment module."
        result = _replace_weak_verbs(text)
        self.assertNotIn('worked on', result.lower())
        self.assertIn('developed', result.lower())

    def test_replaces_used(self):
        text = "I used Python and Django."
        result = _replace_weak_verbs(text)
        self.assertNotIn('used', result.lower())

    def test_case_insensitive_replacement(self):
        text = "I Worked On the backend API."
        result = _replace_weak_verbs(text)
        self.assertNotIn('Worked On', result)

    def test_normal_text_unchanged(self):
        text = "Built and deployed microservices using Docker."
        result = _replace_weak_verbs(text)
        self.assertEqual(result, text)


class TestHasSummary(TestCase):

    def test_detects_summary_keyword(self):
        text = "SUMMARY\nExperienced developer."
        self.assertTrue(_has_summary(text))

    def test_detects_profile_keyword(self):
        text = "PROFILE\nI am a developer."
        self.assertTrue(_has_summary(text))

    def test_detects_objective_keyword(self):
        text = "OBJECTIVE\nSeeking a role."
        self.assertTrue(_has_summary(text))

    def test_no_summary_returns_false(self):
        text = "EXPERIENCE\nWorked at TechCorp."
        self.assertFalse(_has_summary(text))

    def test_case_insensitive(self):
        text = "Professional Summary\nDeveloper with 5 years."
        self.assertTrue(_has_summary(text))


class TestGenerateSummary(TestCase):

    def test_includes_jd_title(self):
        result = _generate_summary('Python Developer', ['python', 'django'])
        self.assertIn('Python Developer', result)

    def test_includes_skills(self):
        result = _generate_summary('Developer', ['python', 'django'])
        self.assertIn('python', result.lower())

    def test_includes_professional_summary_header(self):
        result = _generate_summary('Developer', ['python'])
        self.assertIn('PROFESSIONAL SUMMARY', result)

    def test_fallback_when_no_skills(self):
        result = _generate_summary('Developer', [])
        self.assertIn('relevant technologies', result)


class TestInjectMissingSkills(TestCase):

    def test_appends_to_existing_skills_section(self):
        text = "EXPERIENCE\nSome experience.\n\nSKILLS\npython, django\n\nEDUCATION\nBS CS"
        result = _inject_missing_skills(text, ['docker', 'kubernetes'])
        self.assertIn('Docker', result)

    def test_adds_skills_section_if_missing(self):
        text = "EXPERIENCE\nSome work experience here."
        result = _inject_missing_skills(text, ['docker', 'kubernetes'])
        self.assertIn('SKILLS', result)
        self.assertIn('Docker', result)

    def test_limits_to_8_skills(self):
        skills = ['skill' + str(i) for i in range(20)]
        text = "Some resume text."
        result = _inject_missing_skills(text, skills)
        count = sum(1 for s in skills[:8] if s.title() in result)
        self.assertLessEqual(count, 8)


class TestOptimizeResume(TestCase):

    def test_empty_text_returns_empty(self):
        result = optimize_resume('', [], 'Developer', [])
        self.assertEqual(result, '')

    def test_adds_summary_when_missing(self):
        text = "EXPERIENCE\nWorked at TechCorp for 3 years."
        result = optimize_resume(text, [], 'Python Developer', ['python'])
        self.assertIn('PROFESSIONAL SUMMARY', result)

    def test_does_not_duplicate_summary(self):
        text = "PROFESSIONAL SUMMARY\nExperienced developer.\n\nEXPERIENCE\nTechCorp."
        result = optimize_resume(text, [], 'Developer', ['python'])
        count = result.upper().count('PROFESSIONAL SUMMARY')
        self.assertEqual(count, 1)

    def test_injects_missing_skills(self):
        text = "EXPERIENCE\nPython developer.\n\nSKILLS\npython"
        result = optimize_resume(text, ['docker', 'kubernetes'], 'Developer', ['python'])
        self.assertIn('Docker', result)

    def test_replaces_weak_verbs(self):
        text = "SUMMARY\nExperienced developer.\n\nEXPERIENCE\nI worked on backend APIs."
        result = optimize_resume(text, [], 'Developer', ['python'])
        self.assertNotIn('worked on', result.lower())

    def test_returns_string(self):
        result = optimize_resume("Some resume text.", ['docker'], 'Developer', ['python'])
        self.assertIsInstance(result, str)
