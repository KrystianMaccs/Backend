import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from .models import Artist

User = get_user_model()

@pytest.fixture
def user_data():
    # Create a sample user
    user = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="password"
    )
    return user

@pytest.fixture
def artist_data(user_data):
    # Create a sample artist associated with the user
    artist = Artist.objects.create(
        user=user_data,
        artist_field1="value1",  # Replace with actual artist fields
        artist_field2="value2",
        # Add more fields as needed
    )
    return artist

@pytest.fixture
def api_client():
    # Create an API client for making API requests
    client = APIClient()
    return client

@pytest.fixture
def authenticated_api_client(api_client, user_data):
    # Authenticate the API client with a user token
    token, _ = Token.objects.get_or_create(user=user_data)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return api_client
