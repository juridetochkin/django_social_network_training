from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse

User = get_user_model()


class TestPostsApp(TestCase):
    # Preparing test user account and creating Client instance
    def setUp(self):
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
        post_id = Post.objects.get(text=post_text).id  # Get post id
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


class Test404(TestCase):

    def test_404(self):
        self.client = Client()
        response = self.client.get('/group/foo/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/foo/')
        self.assertEqual(response.status_code, 404)


class TestImages(TestCase):
    # Preparing test user account and creating Client instance
    def setUp(self):
        self.client = Client()
        self.username = 'bratok777'
        self.password = '12345678Dj'
        self.text = 'Hello! I\'m a test text :)'
        self.client.post(reverse('signup'), {'first_name': 'Michael',
                                             'last_name': 'Circle',
                                             'username': self.username,
                                             'email': 'bratok@brat.ok',
                                             'password1': self.password,
                                             'password2': self.password
                                             },
                         follow=True)
        self.group = Group.objects.create(title='Test Group',
                                          slug='test-group')

        # Login test user
        self.client.login(username=self.username,
                          password=self.password,
                          follow=True)

    @staticmethod
    def get_urls(username, post_id, group_slug):
        return [reverse('index'),
                reverse('profile', kwargs={'username': username}),
                reverse('post', kwargs={'username': username,
                                        'post_id': post_id}),
                reverse('group', kwargs={'slug': group_slug})]

    def test_mp3_loading(self):
        with open(
                'C:/mp3_not_img.mp3',
                'rb') as f:
            response = self.client.post(reverse('new_post'),
                                        data={
                                            'text': self.text,
                                            'image': f
                                        },
                                        follow=True)
        self.assertNotEqual(response, 200)

    def test_image_loading(self):
        with open('media/posts/banner_2532.jpg', 'rb') as img:
            self.client.post('/new/',
                             data={
                                 'text': self.text,
                                 'image': img,
                                 'group': self.group.id
                             },
                             follow=True)

        post = Post.objects.get(text=self.text)

        for url in self.get_urls(self.username,
                                 post.id,
                                 self.group.slug):
            response = self.client.get(url)
            self.assertContains(response, '<img')
