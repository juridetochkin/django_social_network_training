from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


class TestPostsApp(TestCase):
    def setUp(self):                                     # Preparing test user entry and creating Client instance
        self.client = Client()
        self.client.post("/auth/signup/", {'first_name': 'Michael',
                                           'last_name': 'Circle',
                                           'username': 'bratok777',
                                           'email': 'bratok@brat.ok',
                                           'password1': '13151315To',
                                           'password2': '13151315To'
                                           },
                         follow=True)

    def test_post(self):

        post_text = 'foobar'
        new_text = 'TEST TEXT'

        # Checking if new user profile page was created
        response = self.client.get('/bratok777/')
        self.assertEqual(response.status_code, 200)

        # Login our user and checking the new post creation
        self.client.login(username='bratok777', password='13151315To', follow=True)
        response = self.client.post('/new/', {'text': post_text}, follow=True)
        self.assertRedirects(response, '/')

        # Checking if we can create new post being LOGOUT
        # Also checking redirection path
        self.client.logout()
        response = self.client.post('/new/', {'text': 'LOGOUT TEST TEXT'},
                                    follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

        # Checking for post containing in INDEX page
        response = self.client.get('/')
        self.assertContains(response, post_text)

        # Checking for post containing in PROFILE page
        response = self.client.get('/bratok777/')
        self.assertContains(response, post_text)

        # Checking if post contains on POST page (Also we get post id in the next line)
        post_id = Post.objects.get(text='foobar').id
        response = self.client.get(f'/bratok777/{post_id}/')
        self.assertContains(response, post_text)

        # Checking if user can edit post
        self.client.login(username='bratok777', password='13151315To')
        response = self.client.post(f'/bratok777/{post_id}/edit/', {'text': new_text},
                                    follow=True)
        self.assertRedirects(response, '/bratok777/')

        # Checking if post edition was done on referenced paged
        response = self.client.get('/')
        self.assertContains(response, new_text)
        response = self.client.get('/bratok777/')
        self.assertContains(response, new_text)
        response = self.client.get(f'/bratok777/{post_id}/')
        self.assertContains(response, new_text)
