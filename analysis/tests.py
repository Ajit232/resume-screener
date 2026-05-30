"""
Tests for analysis app:
- AnalysisResult model methods
- RunAnalysisForm validation
- Run, result, history, delete views
- Full end-to-end analysis integration test
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from jobs.models import JobDescription
from resumes.models import Resume
from analysis.models import AnalysisResult
from analysis.forms import RunAnalysisForm


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestAnalysisResultModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='analysisuser',
            password='AnalysisPass123!'
        )
        self.jd = JobDescription.objects.create(
            user=self.user,
            title='Python Developer',
            raw_text='Python developer needed.',
            parsed_skills=['python', 'django'],
            parsed_keywords=['python', 'developer'],
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='My Resume',
            raw_text='Python developer with experience.',
        )

    def _make_result(self, final_score=75.0):
        return AnalysisResult.objects.create(
            user=self.user,
            resume=self.resume,
            job_description=self.jd,
            skill_match_score=80.0,
            keyword_match_score=70.0,
            experience_score=60.0,
            education_score=100.0,
            final_score=final_score,
            matched_skills=['python'],
            missing_skills=['django'],
            matched_keywords=['python'],
            missing_keywords=['developer'],
            suggestions=['Add more skills.'],
        )

    def test_create_analysis_result(self):
        result = self._make_result()
        self.assertEqual(result.final_score, 75.0)
        self.assertEqual(result.user, self.user)

    def test_get_label_strong(self):
        result = self._make_result(final_score=85.0)
        self.assertEqual(result.get_label(), 'Strong Match')

    def test_get_label_good(self):
        result = self._make_result(final_score=65.0)
        self.assertEqual(result.get_label(), 'Good Match')

    def test_get_label_partial(self):
        result = self._make_result(final_score=50.0)
        self.assertEqual(result.get_label(), 'Partial Match')

    def test_get_label_low(self):
        result = self._make_result(final_score=30.0)
        self.assertEqual(result.get_label(), 'Low Match')

    def test_get_label_color_strong(self):
        result = self._make_result(final_score=85.0)
        self.assertEqual(result.get_label_color(), 'success')

    def test_get_label_color_good(self):
        result = self._make_result(final_score=65.0)
        self.assertEqual(result.get_label_color(), 'info')

    def test_get_label_color_partial(self):
        result = self._make_result(final_score=50.0)
        self.assertEqual(result.get_label_color(), 'warning')

    def test_get_label_color_low(self):
        result = self._make_result(final_score=30.0)
        self.assertEqual(result.get_label_color(), 'danger')

    def test_get_score_class_strong(self):
        result = self._make_result(final_score=85.0)
        self.assertEqual(result.get_score_class(), 'strong')

    def test_get_score_class_good(self):
        result = self._make_result(final_score=65.0)
        self.assertEqual(result.get_score_class(), 'good')

    def test_get_score_class_partial(self):
        result = self._make_result(final_score=50.0)
        self.assertEqual(result.get_score_class(), 'partial')

    def test_get_score_class_low(self):
        result = self._make_result(final_score=30.0)
        self.assertEqual(result.get_score_class(), 'low')

    def test_str_includes_score(self):
        result = self._make_result(final_score=75.0)
        self.assertIn('75.0', str(result))

    def test_ordering_newest_first(self):
        r1 = self._make_result(final_score=50.0)
        r2 = self._make_result(final_score=80.0)
        results = list(AnalysisResult.objects.filter(user=self.user))
        self.assertEqual(results[0].final_score, 80.0)


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class TestRunAnalysisForm(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='formuser',
            password='FormPass123!'
        )
        self.jd = JobDescription.objects.create(
            user=self.user,
            title='Python Developer',
            raw_text='Python developer needed with Django experience.',
            parsed_skills=['python'],
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='My Resume',
            raw_text='Python developer with 5 years of experience.',
        )

    def test_valid_form(self):
        form = RunAnalysisForm(self.user, data={
            'resume': self.resume.pk,
            'job_description': self.jd.pk,
        })
        self.assertTrue(form.is_valid())

    def test_missing_resume(self):
        form = RunAnalysisForm(self.user, data={
            'resume': '',
            'job_description': self.jd.pk,
        })
        self.assertFalse(form.is_valid())

    def test_missing_jd(self):
        form = RunAnalysisForm(self.user, data={
            'resume': self.resume.pk,
            'job_description': '',
        })
        self.assertFalse(form.is_valid())

    def test_only_shows_user_resumes(self):
        other_user = User.objects.create_user(
            username='otherformuser', password='pass'
        )
        other_resume = Resume.objects.create(
            user=other_user,
            title='Other Resume',
            raw_text='Some text.',
        )
        form = RunAnalysisForm(self.user)
        resume_ids = list(form.fields['resume'].queryset.values_list('pk', flat=True))
        self.assertNotIn(other_resume.pk, resume_ids)
        self.assertIn(self.resume.pk, resume_ids)

    def test_only_shows_user_jds(self):
        other_user = User.objects.create_user(
            username='otherjdformuser', password='pass'
        )
        other_jd = JobDescription.objects.create(
            user=other_user, title='Other JD', raw_text='Some text.'
        )
        form = RunAnalysisForm(self.user)
        jd_ids = list(
            form.fields['job_description'].queryset.values_list('pk', flat=True)
        )
        self.assertNotIn(other_jd.pk, jd_ids)
        self.assertIn(self.jd.pk, jd_ids)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class TestAnalysisViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='analysisviewuser',
            password='AnalysisViewPass123!'
        )
        self.client.login(username='analysisviewuser', password='AnalysisViewPass123!')
        self.jd = JobDescription.objects.create(
            user=self.user,
            title='Python Developer',
            raw_text='Python developer needed with Django experience.',
            parsed_skills=['python', 'django'],
            parsed_keywords=['python', 'developer'],
            experience_required='3 years',
            education_required='bachelor',
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='My Resume',
            raw_text='Python developer with 5 years of experience in Django. ' * 5,
        )
        self.result = AnalysisResult.objects.create(
            user=self.user,
            resume=self.resume,
            job_description=self.jd,
            skill_match_score=80.0,
            keyword_match_score=70.0,
            experience_score=100.0,
            education_score=100.0,
            final_score=85.0,
            matched_skills=['python'],
            missing_skills=['django'],
            matched_keywords=['python'],
            missing_keywords=['developer'],
            suggestions=['Add more skills.'],
        )

    def test_run_page_loads(self):
        response = self.client.get(reverse('analysis:run'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/run.html')

    def test_unauthenticated_redirected(self):
        self.client.logout()
        response = self.client.get(reverse('analysis:run'))
        self.assertEqual(response.status_code, 302)

    def test_result_page_loads(self):
        response = self.client.get(
            reverse('analysis:result', kwargs={'pk': self.result.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/result.html')

    def test_result_shows_score(self):
        response = self.client.get(
            reverse('analysis:result', kwargs={'pk': self.result.pk})
        )
        self.assertContains(response, '85')

    def test_other_user_cannot_see_result(self):
        other = User.objects.create_user(
            username='otheranalysis', password='OtherPass123!'
        )
        self.client.login(username='otheranalysis', password='OtherPass123!')
        response = self.client.get(
            reverse('analysis:result', kwargs={'pk': self.result.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_history_page_loads(self):
        response = self.client.get(reverse('analysis:history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/history.html')

    def test_history_shows_results(self):
        response = self.client.get(reverse('analysis:history'))
        self.assertContains(response, 'Python Developer')

    def test_delete_analysis(self):
        response = self.client.post(
            reverse('analysis:delete', kwargs={'pk': self.result.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            AnalysisResult.objects.filter(pk=self.result.pk).exists()
        )

    def test_run_analysis_creates_result(self):
        initial_count = AnalysisResult.objects.filter(user=self.user).count()
        response = self.client.post(reverse('analysis:run'), {
            'resume': self.resume.pk,
            'job_description': self.jd.pk,
        })
        self.assertEqual(response.status_code, 302)
        new_count = AnalysisResult.objects.filter(user=self.user).count()
        self.assertEqual(new_count, initial_count + 1)


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestFullAnalysisFlow(TestCase):
    """
    End-to-end test: signup → add JD → upload resume → run analysis → view result
    """

    def setUp(self):
        self.client = Client()

    def test_full_flow(self):
        # Step 1: Create user
        user = User.objects.create_user(
            username='flowuser',
            password='FlowPass123!'
        )
        self.client.login(username='flowuser', password='FlowPass123!')

        # Step 2: Confirm dashboard loads
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)

        # Step 3: Create job description directly (bypassing file upload)
        jd = JobDescription.objects.create(
            user=user,
            title='Full Stack Developer',
            raw_text=(
                'We need a full stack developer with 3 years of experience. '
                'Bachelor degree required. '
                'Skills: python, django, react, postgresql, docker, git.'
            ),
            parsed_skills=['python', 'django', 'react', 'postgresql'],
            parsed_keywords=['python', 'full', 'stack', 'developer'],
            experience_required='3 years',
            education_required='bachelor',
        )

        # Step 4: Create resume directly
        resume = Resume.objects.create(
            user=user,
            title='My Resume',
            raw_text=(
                'John Smith. Python developer with 4 years of experience. '
                'Bachelor of Science in Computer Science. '
                'Skills: python, django, postgresql, git, docker.'
            ),
        )

        # Step 5: Run analysis via POST
        response = self.client.post(reverse('analysis:run'), {
            'resume': resume.pk,
            'job_description': jd.pk,
        })
        self.assertEqual(response.status_code, 302)

        # Step 6: Check result was created
        result = AnalysisResult.objects.filter(user=user).first()
        self.assertIsNotNone(result)
        self.assertGreater(result.final_score, 0.0)
        self.assertLessEqual(result.final_score, 100.0)
        self.assertIsInstance(result.matched_skills, list)
        self.assertIsInstance(result.missing_skills, list)
        self.assertIsInstance(result.suggestions, list)

        # Step 7: View result page
        response = self.client.get(
            reverse('analysis:result', kwargs={'pk': result.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Step 8: Check history
        response = self.client.get(reverse('analysis:history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Full Stack Developer')
