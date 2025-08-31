# users/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from .models import User
import uuid

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'strongpass123'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            first_name='John',
            last_name='Doe',
            password=self.user_data['password']
        )
        # We are clearing cache before every test to avoid conflicts
        cache.clear()

    def test_register(self):
        response = self.client.post('/api/register/', {
            'full_name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'password': 'strongpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'message': 'Signup successful'})
        user = User.objects.get(email='jane.smith@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Smith')

    def test_login(self):
        response = self.client.post('/api/login/', {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        # Verify that access token is a non-empty string
        self.assertTrue(isinstance(response.data['access'], str))
        self.assertTrue(len(response.data['access']) > 0)

    def test_forgot_password_valid_email(self):
        response = self.client.post('/api/forgot-password/', {
            'email': self.user_data['email']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Reset token generated')
        self.assertIn('token', response.data)
        token = response.data['token']
        user_id = cache.get(f'reset_{token}')
        self.assertEqual(user_id, self.user.id)

    def test_forgot_password_invalid_email(self):
        response = self.client.post('/api/forgot-password/', {
            'email': 'nonexistent@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')

    def test_reset_password_valid_token(self):
        # Generate a reset token
        token = str(uuid.uuid4())
        cache.set(f'reset_{token}', self.user.id, timeout=600)
        new_password = 'newpass123'
        response = self.client.post('/api/reset-password/', {
            'token': token,
            'new_password': new_password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset successfully')
        # Verify password was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        # Verify token was deleted from Redis
        self.assertIsNone(cache.get(f'reset_{token}'))

    def test_reset_password_invalid_token(self):
        response = self.client.post('/api/reset-password/', {
            'token': 'randominvalidtoken',
            'new_password': 'newpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid or expired token')
