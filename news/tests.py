from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest.mock import patch

from .models import CustomUser, Publisher, Article, Newsletter


class BaseAPITestCase(APITestCase):
    """Base test class with setup for all tests."""

    def setUp(self):
        """Create test users, publisher, and articles."""

        # Create test users
        self.reader = CustomUser.objects.create_user(
            username='reader1',
            email='reader@test.com',
            password='testpass123',
            role='reader'
        )
        self.editor = CustomUser.objects.create_user(
            username='editor1',
            email='editor@test.com',
            password='testpass123',
            role='editor'
        )
        self.journalist = CustomUser.objects.create_user(
            username='journalist1',
            email='journalist@test.com',
            password='testpass123',
            role='journalist'
        )

        # Create tokens
        self.reader_token = Token.objects.create(user=self.reader)
        self.editor_token = Token.objects.create(user=self.editor)
        self.journalist_token = Token.objects.create(user=self.journalist)

        # Create test publisher
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )

        # Create test articles
        self.approved_article = Article.objects.create(
            title='Approved Article',
            content='This is an approved article.',
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )
        self.unapproved_article = Article.objects.create(
            title='Unapproved Article',
            content='This is awaiting approval.',
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

    def authenticate(self, token):
        """Set auth token for requests."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')


class ArticleAPITests(BaseAPITestCase):
    """Tests for Article API endpoints."""

    def test_anyone_can_view_approved_articles(self):
        """Test that anyone can view approved articles."""
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unapproved_articles_are_hidden(self):
        """Test that unapproved articles don't show up."""
        response = self.client.get('/api/articles/')
        titles = [article['title'] for article in response.data]
        self.assertNotIn('Unapproved Article', titles)

    def test_journalist_can_create_article(self):
        """Test that journalists can create articles."""
        self.authenticate(self.journalist_token)
        data = {'title': 'New Article', 'content': 'Article content.'}
        response = self.client.post('/api/articles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['approved'])

    def test_reader_cannot_create_article(self):
        """Test that readers cannot create articles."""
        self.authenticate(self.reader_token)
        data = {'title': 'Reader Article', 'content': 'Should fail.'}
        response = self.client.post('/api/articles/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_article(self):
        """Test that unauthenticated users cannot create articles."""
        data = {'title': 'Anonymous Article', 'content': 'Should fail.'}
        response = self.client.post('/api/articles/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_editor_can_delete_article(self):
        """Test that editors can delete articles."""
        self.authenticate(self.editor_token)
        response = self.client.delete(f'/api/articles/{self.approved_article.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reader_cannot_delete_article(self):
        """Test that readers cannot delete articles."""
        self.authenticate(self.reader_token)
        response = self.client.delete(f'/api/articles/{self.approved_article.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscribedArticlesTests(BaseAPITestCase):
    """Tests for the subscribed articles endpoint."""

    def test_unauthenticated_cannot_access_subscribed(self):
        """Test that auth is required for subscribed articles."""
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reader_sees_subscribed_publisher_articles(self):
        """Test that subscribers see articles from their publishers."""
        self.reader.subscribed_publishers.add(self.publisher)
        self.authenticate(self.reader_token)
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reader_with_no_subscriptions_gets_empty_list(self):
        """Test that users with no subscriptions see empty list."""
        self.authenticate(self.reader_token)
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class EditorApproveTests(BaseAPITestCase):
    """Tests for the editor approval workflow."""

    @patch('news.views.send_mail')
    def test_editor_can_approve_article(self, mock_send_mail):
        """Test that editors can approve articles."""
        self.client.login(username='editor1', password='testpass123')
        response = self.client.get(f'/editor/approve/{self.unapproved_article.pk}/')
        self.unapproved_article.refresh_from_db()
        self.assertTrue(self.unapproved_article.approved)

    @patch('news.views.send_mail')
    def test_approval_sends_email_to_subscribers(self, mock_send_mail):
        """Test that approving sends emails to subscribers."""
        self.reader.subscribed_publishers.add(self.publisher)
        self.client.login(username='editor1', password='testpass123')
        self.client.get(f'/editor/approve/{self.unapproved_article.pk}/')
        self.assertTrue(mock_send_mail.called)


class NewsletterTests(BaseAPITestCase):
    """Tests for Newsletter model."""

    def test_newsletter_created_with_articles(self):
        """Test creating a newsletter with articles."""
        newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='A test newsletter',
            author=self.journalist
        )
        newsletter.articles.add(self.approved_article)
        self.assertEqual(newsletter.articles.count(), 1)
        self.assertEqual(newsletter.author.role, 'journalist')

    def test_article_can_be_in_multiple_newsletters(self):
        """Test that articles can belong to multiple newsletters."""
        newsletter1 = Newsletter.objects.create(title='Newsletter 1', author=self.journalist)
        newsletter2 = Newsletter.objects.create(title='Newsletter 2', author=self.journalist)
        newsletter1.articles.add(self.approved_article)
        newsletter2.articles.add(self.approved_article)
        self.assertEqual(self.approved_article.newsletters.count(), 2)

    def test_journalist_can_create_newsletter_via_api(self):
        """Test that journalists can create newsletters via API."""
        self.authenticate(self.journalist_token)
        data = {'title': 'New Newsletter', 'description': 'Test description'}
        response = self.client.post('/api/newsletters/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)