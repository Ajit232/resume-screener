"""
Tests for dashboard app.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from jobs.models import JobDescription
from resumes.models import Resume
from analysis.models import AnalysisResult


class TestDashboardView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashboarduser',
            password='DashPass123!'
        )
        self.client.login(username='dashboarduser', password='DashPass123!')

    def test_dashboard_loads(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')

    def test_unauthenticated_redirected(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_shows_zero_counts_for_new_user(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertContains(response, '0')

    def test_dashboard_shows_correct_resume_count(self):
        Resume.objects.create(
            user=self.user, title='Resume 1', raw_text='Some text.')
        Resume.objects.create(
            user=self.user, title='Resume 2', raw_text='Some text.')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.context['resume_count'], 2)

    def test_dashboard_shows_correct_jd_count(self):
        JobDescription.objects.create(
            user=self.user, title='JD 1', raw_text='Some text.')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.context['jd_count'], 1)

    def test_dashboard_shows_correct_analysis_count(self):
        jd = JobDescription.objects.create(
            user=self.user, title='JD', raw_text='text')
        resume = Resume.objects.create(
            user=self.user, title='Resume', raw_text='text')
        AnalysisResult.objects.create(
            user=self.user, resume=resume, job_description=jd,
            final_score=75.0, matched_skills=[], missing_skills=[],
            matched_keywords=[], missing_keywords=[], suggestions=[],
        )
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.context['analysis_count'], 1)

    def test_dashboard_context_has_required_keys(self):
        response = self.client.get(reverse('dashboard:index'))
        required = [
            'analyses', 'resumes', 'jds',
            'resume_count', 'jd_count', 'analysis_count',
        ]
        for key in required:
            self.assertIn(key, response.context)

    def test_only_own_data_shown(self):
        other_user = User.objects.create_user(
            username='otheruser', password='OtherPass123!'
        )
        Resume.objects.create(
            user=other_user, title='Other Resume', raw_text='text')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.context['resume_count'], 0)
