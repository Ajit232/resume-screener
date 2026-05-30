"""
Unit tests for services/scorer.py
Tests all scoring components and the final weighted score.
"""

from django.test import TestCase
from services.scorer import (
    compute_skill_match,
    compute_keyword_match,
    compute_experience_score,
    compute_education_score,
    compute_final_score,
    run_full_scoring,
    SKILL_WEIGHT,
    KEYWORD_WEIGHT,
    EXPERIENCE_WEIGHT,
    EDUCATION_WEIGHT,
)


class TestWeights(TestCase):

    def test_weights_sum_to_one(self):
        total = SKILL_WEIGHT + KEYWORD_WEIGHT + EXPERIENCE_WEIGHT + EDUCATION_WEIGHT
        self.assertAlmostEqual(total, 1.0, places=5)


class TestComputeSkillMatch(TestCase):

    def test_perfect_match(self):
        result = compute_skill_match(
            ['python', 'django', 'postgresql'],
            ['python', 'django', 'postgresql']
        )
        self.assertEqual(result['score'], 100.0)
        self.assertEqual(len(result['missing']), 0)
        self.assertEqual(len(result['matched']), 3)

    def test_no_match(self):
        result = compute_skill_match(
            ['java', 'spring'],
            ['python', 'django', 'postgresql']
        )
        self.assertEqual(result['score'], 0.0)
        self.assertEqual(len(result['missing']), 3)
        self.assertEqual(len(result['matched']), 0)

    def test_partial_match(self):
        result = compute_skill_match(
            ['python', 'java'],
            ['python', 'django', 'postgresql']
        )
        self.assertAlmostEqual(result['score'], 33.33, places=1)
        self.assertIn('python', result['matched'])
        self.assertIn('django', result['missing'])

    def test_empty_jd_skills(self):
        result = compute_skill_match(['python'], [])
        self.assertEqual(result['score'], 0.0)

    def test_empty_resume_skills(self):
        result = compute_skill_match([], ['python', 'django'])
        self.assertEqual(result['score'], 0.0)
        self.assertEqual(len(result['missing']), 2)

    def test_case_insensitive(self):
        result = compute_skill_match(['Python', 'DJANGO'], ['python', 'django'])
        self.assertEqual(result['score'], 100.0)

    def test_score_between_0_and_100(self):
        result = compute_skill_match(['python'], ['python', 'django'])
        self.assertGreaterEqual(result['score'], 0.0)
        self.assertLessEqual(result['score'], 100.0)


class TestComputeKeywordMatch(TestCase):

    def test_all_keywords_present(self):
        resume = "I have python django postgresql experience."
        keywords = ['python', 'django', 'postgresql']
        result = compute_keyword_match(resume, keywords)
        self.assertEqual(result['score'], 100.0)

    def test_no_keywords_present(self):
        resume = "I have java spring boot experience."
        keywords = ['python', 'django']
        result = compute_keyword_match(resume, keywords)
        self.assertEqual(result['score'], 0.0)

    def test_partial_match(self):
        resume = "I know python but not django."
        keywords = ['python', 'django', 'postgresql']
        result = compute_keyword_match(resume, keywords)
        self.assertGreater(result['score'], 0.0)
        self.assertLess(result['score'], 100.0)

    def test_empty_keywords(self):
        result = compute_keyword_match("some text", [])
        self.assertEqual(result['score'], 0.0)

    def test_empty_resume(self):
        result = compute_keyword_match("", ['python'])
        self.assertEqual(result['score'], 0.0)

    def test_whole_word_matching(self):
        # 'py' should not match 'python'
        resume = "I work with py and django."
        keywords = ['python']
        result = compute_keyword_match(resume, keywords)
        self.assertEqual(result['score'], 0.0)


class TestComputeExperienceScore(TestCase):

    def test_exact_match(self):
        resume = "I have 5 years of experience in Python."
        score = compute_experience_score(resume, '5 years')
        self.assertEqual(score, 100.0)

    def test_exceeds_requirement(self):
        resume = "I have 8 years of experience."
        score = compute_experience_score(resume, '5 years')
        self.assertEqual(score, 100.0)

    def test_below_requirement(self):
        resume = "I have 2 years of experience."
        score = compute_experience_score(resume, '5 years')
        self.assertLess(score, 100.0)
        self.assertGreater(score, 0.0)

    def test_no_requirement_gives_full_score(self):
        resume = "I have 3 years of experience."
        score = compute_experience_score(resume, '')
        self.assertEqual(score, 100.0)

    def test_no_years_in_resume(self):
        resume = "I am an experienced developer."
        score = compute_experience_score(resume, '3 years')
        self.assertEqual(score, 40.0)

    def test_score_between_0_and_100(self):
        resume = "3 years of experience."
        score = compute_experience_score(resume, '5 years')
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)


class TestComputeEducationScore(TestCase):

    def test_exact_match(self):
        resume = "Bachelor of Science in Computer Science."
        score = compute_education_score(resume, 'bachelor')
        self.assertEqual(score, 100.0)

    def test_exceeds_requirement(self):
        resume = "PhD in Computer Science."
        score = compute_education_score(resume, 'bachelor')
        self.assertEqual(score, 100.0)

    def test_one_tier_below(self):
        resume = "Diploma in Information Technology."
        score = compute_education_score(resume, 'bachelor')
        self.assertEqual(score, 60.0)

    def test_no_requirement_gives_full_score(self):
        resume = "Some resume text."
        score = compute_education_score(resume, '')
        self.assertEqual(score, 100.0)

    def test_any_requirement_gives_full_score(self):
        resume = "Some resume text."
        score = compute_education_score(resume, 'any')
        self.assertEqual(score, 100.0)

    def test_phd_required_bachelor_present(self):
        resume = "Bachelor of Science in Computer Science."
        score = compute_education_score(resume, 'phd')
        self.assertLess(score, 100.0)


class TestComputeFinalScore(TestCase):

    def test_all_perfect_gives_100(self):
        score = compute_final_score(100.0, 100.0, 100.0, 100.0)
        self.assertEqual(score, 100.0)

    def test_all_zero_gives_zero(self):
        score = compute_final_score(0.0, 0.0, 0.0, 0.0)
        self.assertEqual(score, 0.0)

    def test_weighted_calculation(self):
        # skill=100, keyword=0, exp=0, edu=0
        # expected = 100*0.40 + 0*0.25 + 0*0.20 + 0*0.15 = 40.0
        score = compute_final_score(100.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(score, 40.0, places=1)

    def test_score_never_exceeds_100(self):
        score = compute_final_score(110.0, 110.0, 110.0, 110.0)
        self.assertLessEqual(score, 100.0)

    def test_score_between_0_and_100(self):
        score = compute_final_score(60.0, 70.0, 80.0, 50.0)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)


class TestRunFullScoring(TestCase):

    def setUp(self):
        self.resume_text = (
            "John Smith - Python Developer\n"
            "5 years of experience with Python, Django, PostgreSQL.\n"
            "Bachelor of Science in Computer Science.\n"
            "Skills: python, django, postgresql, docker, git"
        )
        self.jd_text = (
            "Senior Python Developer\n"
            "3-5 years of experience required.\n"
            "Bachelor's degree required.\n"
            "Skills needed: python, django, postgresql, redis"
        )

    def test_returns_all_keys(self):
        result = run_full_scoring(
            resume_text=self.resume_text,
            resume_skills=['python', 'django', 'postgresql', 'docker'],
            jd_text=self.jd_text,
            jd_skills=['python', 'django', 'postgresql', 'redis'],
            jd_keywords=['python', 'django', 'senior'],
            jd_experience_required='3-5 years',
            jd_education_required='bachelor',
        )
        expected_keys = [
            'skill_match_score', 'keyword_match_score',
            'experience_score', 'education_score', 'final_score',
            'matched_skills', 'missing_skills',
            'matched_keywords', 'missing_keywords',
        ]
        for key in expected_keys:
            self.assertIn(key, result)

    def test_scores_in_valid_range(self):
        result = run_full_scoring(
            resume_text=self.resume_text,
            resume_skills=['python', 'django'],
            jd_text=self.jd_text,
            jd_skills=['python', 'django', 'redis'],
            jd_keywords=['python', 'developer'],
            jd_experience_required='3 years',
            jd_education_required='bachelor',
        )
        for key in ['skill_match_score', 'keyword_match_score',
                    'experience_score', 'education_score', 'final_score']:
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 100.0)

    def test_matched_and_missing_are_lists(self):
        result = run_full_scoring(
            resume_text=self.resume_text,
            resume_skills=['python'],
            jd_text=self.jd_text,
            jd_skills=['python', 'django'],
            jd_keywords=['python'],
            jd_experience_required='',
            jd_education_required='',
        )
        self.assertIsInstance(result['matched_skills'], list)
        self.assertIsInstance(result['missing_skills'], list)
        self.assertIn('python', result['matched_skills'])
        self.assertIn('django', result['missing_skills'])
