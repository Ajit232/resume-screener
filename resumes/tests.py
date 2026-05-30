"""
Tests for resumes app:
- Resume model including versioning and word_count
- ResumeUploadForm and ResumeEditForm validation
- Upload, detail, editor, delete views
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from resumes.models import Resume
from resumes.forms import ResumeUploadForm, ResumeEditForm


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestResumeModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='resumeuser',
            password='ResumePass123!'
        )

    def test_create_resume(self):
        resume = Resume.objects.create(
            user=self.user,
            title='My Resume',
            raw_text='Python developer with 5 years experience.',
        )
        self.assertEqual(resume.title, 'My Resume')
        self.assertEqual(resume.version, 1)
        self.assertFalse(resume.is_optimized)

    def test_str_representation(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            raw_text='Some text.',
        )
        self.assertIn('Test Resume', str(resume))
        self.assertIn('v1', str(resume))

    def test_optimized_str_has_tag(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Optimised Resume',
            raw_text='Some text.',
            is_optimized=True,
        )
        self.assertIn('optimised', str(resume))

    def test_word_count(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Test',
            raw_text='one two three four five',
        )
        self.assertEqual(resume.word_count(), 5)

    def test_word_count_empty_text(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Test',
            raw_text='',
        )
        self.assertEqual(resume.word_count(), 0)

    def test_get_all_versions_single(self):
        resume = Resume.objects.create(
            user=self.user,
            title='Test',
            raw_text='text',
        )
        versions = resume.get_all_versions()
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0], resume)

    def test_get_all_versions_with_children(self):
        parent = Resume.objects.create(
            user=self.user, title='Parent', raw_text='v1 text', version=1
        )
        child = Resume.objects.create(
            user=self.user, title='Child', raw_text='v2 text',
            version=2, parent=parent
        )
        versions = parent.get_all_versions()
        self.assertIn(parent, versions)
        self.assertIn(child, versions)

    def test_default_version_is_1(self):
        resume = Resume.objects.create(
            user=self.user, title='Test', raw_text='text'
        )
        self.assertEqual(resume.version, 1)

    def test_ordering_newest_first(self):
        r1 = Resume.objects.create(user=self.user, title='First', raw_text='text')
        r2 = Resume.objects.create(user=self.user, title='Second', raw_text='text')
        resumes = list(Resume.objects.filter(user=self.user))
        self.assertEqual(resumes[0].title, 'Second')


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class TestResumeEditForm(TestCase):

    def test_valid_form(self):
        form = ResumeEditForm(data={
            'title': 'My Resume',
            'raw_text': 'A' * 150,
        })
        self.assertTrue(form.is_valid())

    def test_text_too_short(self):
        form = ResumeEditForm(data={
            'title': 'My Resume',
            'raw_text': 'Too short',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('raw_text', form.errors)

    def test_title_required(self):
        form = ResumeEditForm(data={
            'title': '',
            'raw_text': 'A' * 150,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class TestResumeViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='resumeviewuser',
            password='ResumeViewPass123!'
        )
        self.client.login(username='resumeviewuser', password='ResumeViewPass123!')
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            raw_text='Python developer with 5 years of experience in Django. ' * 10,
        )

    def test_upload_page_loads(self):
        response = self.client.get(reverse('resumes:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/upload.html')

    def test_unauthenticated_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('resumes:upload'))
        self.assertEqual(response.status_code, 302)

    def test_resume_detail_loads(self):
        response = self.client.get(
            reverse('resumes:detail', kwargs={'pk': self.resume.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/detail.html')

    def test_resume_detail_shows_title(self):
        response = self.client.get(
            reverse('resumes:detail', kwargs={'pk': self.resume.pk})
        )
        self.assertContains(response, 'Test Resume')

    def test_other_user_cannot_see_resume(self):
        other = User.objects.create_user(
            username='otherresume', password='OtherPass123!'
        )
        self.client.login(username='otherresume', password='OtherPass123!')
        response = self.client.get(
            reverse('resumes:detail', kwargs={'pk': self.resume.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_editor_page_loads(self):
        response = self.client.get(
            reverse('resumes:editor', kwargs={'pk': self.resume.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/editor.html')

    def test_editor_saves_new_version(self):
        long_text = 'Updated resume content. ' * 20
        response = self.client.post(
            reverse('resumes:editor', kwargs={'pk': self.resume.pk}),
            {'title': 'Updated Resume', 'raw_text': long_text}
        )
        self.assertEqual(response.status_code, 302)
        new_version = Resume.objects.filter(
            user=self.user, title='Updated Resume'
        ).first()
        self.assertIsNotNone(new_version)
        self.assertEqual(new_version.version, 2)
        self.assertEqual(new_version.parent, self.resume)

    def test_delete_resume(self):
        response = self.client.post(
            reverse('resumes:delete', kwargs={'pk': self.resume.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resume.objects.filter(pk=self.resume.pk).exists())
