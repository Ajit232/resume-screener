"""
Tests for jobs app:
- JobDescription model
- JobDescriptionForm validation
- Upload, detail, delete views
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from jobs.models import JobDescription
from jobs.forms import JobDescriptionForm


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestJobDescriptionModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='jobuser',
            password='JobPass123!'
        )

    def test_create_job_description(self):
        jd = JobDescription.objects.create(
            user=self.user,
            title='Python Developer',
            company='TestCorp',
            raw_text='We need a Python developer with Django experience.',
        )
        self.assertEqual(jd.title, 'Python Developer')
        self.assertEqual(jd.user, self.user)

    def test_str_representation(self):
        jd = JobDescription.objects.create(
            user=self.user,
            title='Data Scientist',
            company='DataCo',
            raw_text='Data scientist role.',
        )
        self.assertIn('Data Scientist', str(jd))

    def test_str_with_company(self):
        jd = JobDescription.objects.create(
            user=self.user,
            title='Dev',
            company='Corp',
            raw_text='Developer role.',
        )
        self.assertIn('Corp', str(jd))

    def test_default_parsed_skills_is_empty_list(self):
        jd = JobDescription.objects.create(
            user=self.user,
            title='Dev',
            raw_text='Some text.',
        )
        self.assertEqual(jd.parsed_skills, [])

    def test_default_parsed_keywords_is_empty_list(self):
        jd = JobDescription.objects.create(
            user=self.user,
            title='Dev',
            raw_text='Some text.',
        )
        self.assertEqual(jd.parsed_keywords, [])

    def test_skill_count_method(self):
        jd = JobDescription.objects.create(
            user=self.user,
            title='Dev',
            raw_text='Some text.',
            parsed_skills=['python', 'django', 'postgresql'],
        )
        self.assertEqual(jd.skill_count(), 3)

    def test_ordering_newest_first(self):
        jd1 = JobDescription.objects.create(
            user=self.user, title='First', raw_text='text')
        jd2 = JobDescription.objects.create(
            user=self.user, title='Second', raw_text='text')
        jds = list(JobDescription.objects.filter(user=self.user))
        self.assertEqual(jds[0].title, 'Second')


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class TestJobDescriptionForm(TestCase):

    def test_valid_with_text(self):
        form = JobDescriptionForm(data={
            'title': 'Python Developer',
            'company': 'TestCorp',
            'raw_text': 'We need a Python developer with 3 years experience. ' * 5,
            'experience_required': '3 years',
            'education_required': 'bachelor',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_without_text_or_file(self):
        form = JobDescriptionForm(data={
            'title': 'Python Developer',
            'company': 'TestCorp',
            'raw_text': '',
        })
        self.assertFalse(form.is_valid())

    def test_title_required(self):
        form = JobDescriptionForm(data={
            'title': '',
            'raw_text': 'Some job description text here for testing purposes.',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_too_short(self):
        form = JobDescriptionForm(data={
            'title': 'AB',
            'raw_text': 'Some job description text here for testing purposes.',
        })
        self.assertFalse(form.is_valid())

    def test_text_too_short(self):
        form = JobDescriptionForm(data={
            'title': 'Python Developer',
            'raw_text': 'Too short.',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('raw_text', form.errors)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class TestJDViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='jdviewuser',
            password='JDViewPass123!'
        )
        self.client.login(username='jdviewuser', password='JDViewPass123!')
        self.jd = JobDescription.objects.create(
            user=self.user,
            title='Test JD',
            raw_text='Python developer needed with Django and PostgreSQL skills.',
            parsed_skills=['python', 'django'],
            parsed_keywords=['python', 'developer'],
        )

    def test_upload_page_loads(self):
        response = self.client.get(reverse('jobs:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/upload.html')

    def test_unauthenticated_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('jobs:upload'))
        self.assertEqual(response.status_code, 302)

    def test_jd_detail_page_loads(self):
        response = self.client.get(reverse('jobs:detail', kwargs={'pk': self.jd.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/detail.html')

    def test_jd_detail_shows_title(self):
        response = self.client.get(reverse('jobs:detail', kwargs={'pk': self.jd.pk}))
        self.assertContains(response, 'Test JD')

    def test_other_user_cannot_see_jd(self):
        other = User.objects.create_user(username='other', password='OtherPass123!')
        self.client.login(username='other', password='OtherPass123!')
        response = self.client.get(reverse('jobs:detail', kwargs={'pk': self.jd.pk}))
        self.assertEqual(response.status_code, 404)

    def test_delete_jd(self):
        response = self.client.post(
            reverse('jobs:delete', kwargs={'pk': self.jd.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            JobDescription.objects.filter(pk=self.jd.pk).exists()
        )

    def test_upload_jd_with_text(self):
        long_text = 'Python developer needed with 3 years of experience. ' * 5
        response = self.client.post(reverse('jobs:upload'), {
            'title': 'New JD',
            'company': 'NewCorp',
            'raw_text': long_text,
            'experience_required': '',
            'education_required': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            JobDescription.objects.filter(title='New JD', user=self.user).exists()
        )
