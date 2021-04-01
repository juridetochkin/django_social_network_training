from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from posts.models import Post
from django.urls import reverse

User = get_user_model()


class TestPostsApp(TestCase):
    def setUp(self):                 # Preparing test user entry and creating Client instance
        self.client = Client()
        self.username = 'bratok777'
        self.password = '12345678Dj'
        self.client.post(reverse('signup'), {'first_name': 'Michael',
                                             'last_name': 'Circle',
                                             'username': self.username,
                                             'email': 'bratok@brat.ok',
                                             'password1': self.password,
                                             'password2': self.password
                                             },
                         follow=True)

    @staticmethod
    def get_urls(username, post_id):
        return [reverse('index'),
                reverse('profile', kwargs={'username': username}),
                reverse('post', kwargs={'username': username,
                                        'post_id': post_id})]

    def test_post_login(self):
        post_text = 'foobar'
        edited_text = 'edited foobar'

        # Checking if we can login
        response = self.client.login(username=self.username,
                                     password=self.password,
                                     follow=True)
        self.assertEqual(response, True)

        # Checking if the new user profile page was created
        response = self.client.get(reverse('profile',
                                           kwargs={'username': self.username}))
        self.assertEqual(response.status_code, 200)

        # Checking the new post creation
        response = self.client.post(reverse('new_post'),
                                    data={'text': post_text},
                                    follow=True)
        self.assertRedirects(response, '/')

        # Checking for post contain in Index, Profile, Post pages
        post_id = Post.objects.get(text='foobar').id  # Get post_id value here
        for url in self.get_urls(self.username, post_id):
            response = self.client.get(url)
            self.assertContains(response, post_text)

        # Checking if user can edit post
        response = self.client.post(reverse('post_edit',
                                            kwargs={'username': self.username,
                                                    'post_id': post_id}),
                                    data={'text': edited_text},
                                    follow=True)
        self.assertRedirects(response, f'/{self.username}/')

        # Checking if post edition was done on referenced pages
        for url in self.get_urls(self.username, post_id):
            response = self.client.get(url)
            self.assertContains(response, edited_text)

    def test_post_logout(self):
        # Checking that we CAN'T create new post being LOGOUT
        # Also checking redirection path
        logout_text = 'logout text'
        response = self.client.post(reverse('new_post'),
                                    data={'text': logout_text},
                                    follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, logout_text)
