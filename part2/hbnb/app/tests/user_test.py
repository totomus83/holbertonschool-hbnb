#!/usr/bin/python3
from app.models.user import User

def test_user_creation():
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com", password="testpass", place_list=[], is_admin=False)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.password == "testpass"
    assert user.place_list == []
    assert user.is_admin is False  # Default value
    print("User creation test passed!")

test_user_creation()