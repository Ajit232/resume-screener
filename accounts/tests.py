"""
Tests for accounts app:
- UserProfile signal creation
- SignupForm validation
- Login/logout views
- Profile view
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile
from accounts.forms import SignupForm, LoginForm


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestUserProfileSignal(TestCase):

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='TestPass123!'
        )
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_profile_is_one_to_one(self):
        user = User.objects.create_user(
            username='testuser2',
            password='TestPass123!'
        )
        profile = user.profile
        self.assertIsInstance(profile, UserProfile)

    def test_profile_str(self):
        user = User.objects.create_user(
            username='testuser3',
            password='TestPass123!'
        )
        self.assertIn('testuser3', str(user.profile))

    def test_superuser_gets_profile(self):
        user = User.objects.create_superuser(
            username='admintest',
            password='AdminPass123!'
        )
        self.assertTrue(hasattr(user, 'profile'))


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class TestSignupForm(TestCase):

    def get_valid_data(self):
        return {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_valid_form(self):
        form = SignupForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())

    def test_missing_email(self):
        data = self.get_valid_data()
        data['email'] = ''
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='taken@example.com',
            password='pass'
        )
        data = self.get_valid_data()
        data['email'] = 'taken@example.com'
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        data = self.get_valid_data()
        data['password2'] = 'DifferentPass123!'
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())

    def test_short_username(self):
        data = self.get_valid_data()
        data['username'] = 'ab'
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_duplicate_username(self):
        User.objects.create_user(username='takenuser', password='pass')
        data = self.get_valid_data()
        data['username'] = 'takenuser'
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class TestSignupView(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:signup')

    def test_signup_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_successful_signup_redirects(self):
        response = self.client.post(self.url, {
            'username': 'brandnewuser',
            'email': 'brandnew@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='brandnewuser').exists())

    def test_invalid_signup_shows_errors(self):
        response = self.client.post(self.url, {
            'username': '',
            'email': 'bad',
            'password1': 'pass',
            'password2': 'different',
        })
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected(self):
        User.objects.create_user(username='already', password='pass123!')
        self.client.login(username='already', password='pass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class TestLoginView(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='loginuser',
            password='LoginPass123!'
        )

    def test_login_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_valid_login_redirects(self):
        response = self.client.post(self.url, {
            'username': 'loginuser',
            'password': 'LoginPass123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_login_shows_error(self):
        response = self.client.post(self.url, {
            'username': 'loginuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected(self):
        self.client.login(username='loginuser', password='LoginPass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class TestLogoutView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='logoutuser',
            password='LogoutPass123!'
        )

    def test_logout_redirects_home(self):
        self.client.login(username='logoutuser', password='LogoutPass123!')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_user_logged_out_after_logout(self):
        self.client.login(username='logoutuser', password='LogoutPass123!')
        self.client.post(reverse('accounts:logout'))
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)


class TestProfileView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='profileuser',
            password='ProfilePass123!'
        )
        self.client.login(username='profileuser', password='ProfilePass123!')

    def test_profile_page_loads(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_unauthenticated_redirected(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
