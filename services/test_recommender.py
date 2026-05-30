"""
Unit tests for services/recommender.py
Tests suggestion generation logic.
"""

from django.test import TestCase
from services.recommender import generate_suggestions


class TestGenerateSuggestions(TestCase):

    def _run(self, **kwargs):
        defaults = {
            'missing_skills': [],
            'missing_keywords': [],
            'skill_score': 70.0,
            'keyword_score': 70.0,
            'experience_score': 70.0,
            'education_score': 70.0,
            'final_score': 70.0,
            'jd_title': 'Python Developer',
        }
        defaults.update(kwargs)
        return generate_suggestions(**defaults)

    def test_returns_list(self):
        result = self._run()
        self.assertIsInstance(result, list)

    def test_missing_skills_generates_suggestion(self):
        result = self._run(missing_skills=['docker', 'kubernetes'])
        combined = ' '.join(result).lower()
        self.assertIn('docker', combined)

    def test_missing_keywords_generates_suggestion(self):
        result = self._run(missing_keywords=['agile', 'scrum'])
        combined = ' '.join(result).lower()
        self.assertIn('agile', combined)

    def test_low_skill_score_generates_warning(self):
        result = self._run(skill_score=30.0)
        combined = ' '.join(result).lower()
        self.assertIn('skill', combined)

    def test_low_final_score_generates_tailor_suggestion(self):
        result = self._run(final_score=35.0)
        combined = ' '.join(result).lower()
        self.assertTrue(
            'low' in combined or 'tailor' in combined or 'match' in combined
        )

    def test_always_includes_action_verb_suggestion(self):
        result = self._run()
        combined = ' '.join(result).lower()
        self.assertIn('action', combined)

    def test_always_includes_quantify_suggestion(self):
        result = self._run()
        combined = ' '.join(result).lower()
        self.assertIn('quantif', combined)

    def test_no_missing_skills_no_skill_suggestion(self):
        result = self._run(missing_skills=[], skill_score=90.0)
        combined = ' '.join(result).lower()
        self.assertNotIn('add these missing skills', combined)

    def test_low_experience_score_suggestion(self):
        result = self._run(experience_score=40.0)
        combined = ' '.join(result).lower()
        self.assertIn('experience', combined)

    def test_low_education_score_suggestion(self):
        result = self._run(education_score=30.0)
        combined = ' '.join(result).lower()
        self.assertIn('education', combined)
