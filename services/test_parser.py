"""
Unit tests for services/parser.py
Tests experience extraction, education extraction, and JD parsing.
"""

from django.test import TestCase
from services.parser import (
    extract_experience_requirement,
    extract_education_requirement,
    extract_requirement_sentences,
    extract_years_as_int,
    parse_jd,
)


class TestExtractExperienceRequirement(TestCase):

    def test_range_format(self):
        text = "We require 3-5 years of experience in Python."
        result = extract_experience_requirement(text)
        self.assertIn('3', result)
        self.assertIn('5', result)

    def test_plus_format(self):
        text = "Minimum 3+ years of experience required."
        result = extract_experience_requirement(text)
        self.assertIn('3', result)

    def test_at_least_format(self):
        text = "At least 2 years of relevant experience."
        result = extract_experience_requirement(text)
        self.assertIn('2', result)

    def test_minimum_of_format(self):
        text = "Minimum of 5 years experience in software development."
        result = extract_experience_requirement(text)
        self.assertIn('5', result)

    def test_years_of_experience_format(self):
        text = "Candidate must have 4 years of experience with Django."
        result = extract_experience_requirement(text)
        self.assertIn('4', result)

    def test_no_experience_mentioned(self):
        text = "We are looking for a talented developer."
        result = extract_experience_requirement(text)
        self.assertEqual(result, '')

    def test_case_insensitive(self):
        text = "Requires 2+ Years of Experience in cloud computing."
        result = extract_experience_requirement(text)
        self.assertIn('2', result)


class TestExtractEducationRequirement(TestCase):

    def test_bachelor_detected(self):
        text = "Bachelor's degree in Computer Science required."
        result = extract_education_requirement(text)
        self.assertEqual(result, 'bachelor')

    def test_master_detected(self):
        text = "Master's degree or equivalent preferred."
        result = extract_education_requirement(text)
        self.assertEqual(result, 'master')

    def test_phd_detected(self):
        text = "PhD in Machine Learning or related field."
        result = extract_education_requirement(text)
        self.assertEqual(result, 'phd')

    def test_diploma_detected(self):
        text = "Diploma in Information Technology acceptable."
        result = extract_education_requirement(text)
        self.assertEqual(result, 'diploma')

    def test_no_education_mentioned(self):
        text = "Strong problem solving skills required."
        result = extract_education_requirement(text)
        self.assertEqual(result, '')

    def test_phd_beats_bachelor(self):
        text = "Bachelor's degree required, PhD preferred."
        result = extract_education_requirement(text)
        self.assertEqual(result, 'phd')

    def test_master_beats_bachelor(self):
        text = "Bachelor's or Master's degree in CS."
        result = extract_education_requirement(text)
        self.assertEqual(result, 'master')


class TestExtractRequirementSentences(TestCase):

    def test_extracts_required_sentences(self):
        text = (
            "We are a great company.\n"
            "Experience with Python is required.\n"
            "Must have knowledge of SQL databases.\n"
            "Nice to have: Docker experience."
        )
        result = extract_requirement_sentences(text)
        self.assertTrue(len(result) >= 1)
        self.assertTrue(any('Python' in s for s in result))

    def test_returns_list(self):
        result = extract_requirement_sentences("Some job description text.")
        self.assertIsInstance(result, list)

    def test_max_20_results(self):
        lines = [f"Must have skill number {i}." for i in range(50)]
        text = '\n'.join(lines)
        result = extract_requirement_sentences(text)
        self.assertLessEqual(len(result), 20)

    def test_empty_text(self):
        result = extract_requirement_sentences("")
        self.assertEqual(result, [])


class TestExtractYearsAsInt(TestCase):

    def test_range_returns_minimum(self):
        self.assertEqual(extract_years_as_int('3-5 years'), 3)

    def test_plus_format(self):
        self.assertEqual(extract_years_as_int('5+ years'), 5)

    def test_single_number(self):
        self.assertEqual(extract_years_as_int('4 years'), 4)

    def test_empty_returns_zero(self):
        self.assertEqual(extract_years_as_int(''), 0)

    def test_none_returns_zero(self):
        self.assertEqual(extract_years_as_int(None), 0)


class TestParseJD(TestCase):

    def test_full_parse(self):
        text = (
            "Senior Python Developer\n"
            "Requirements:\n"
            "- 3-5 years of experience with Python\n"
            "- Bachelor's degree required\n"
            "- Knowledge of Django and PostgreSQL required\n"
        )
        result = parse_jd(text)
        self.assertIn('experience_required', result)
        self.assertIn('education_required', result)
        self.assertIn('requirement_sentences', result)
        self.assertIn('3', result['experience_required'])
        self.assertEqual(result['education_required'], 'bachelor')

    def test_returns_dict(self):
        result = parse_jd("Some job text.")
        self.assertIsInstance(result, dict)
