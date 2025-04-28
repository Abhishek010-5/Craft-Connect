import requests
import json
BASE_URL = "http://localhost:5000/auth"

class TestSignup:
    def __init__(self):
        print("State: Initializing TestSignup class")
        print("Test are running for signup")

    def test_empty_payload(self):
        print("State: Testing signup with empty payload")
        payload = {}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_empty_name(self):
        print("State: Testing signup with empty name")
        payload = {"name":"", "password":"password", "email":"email"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_empty_email(self):
        print("State: Testing signup with empty email")
        payload = {"name":"name", "password":"password", "email":""}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_empty_password(self):
        print("State: Testing signup with empty password")
        payload = {"name":"name", "password":"", "email":"email"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_invalid_password(self):
        print("State: Testing signup with invalid password")
        payload = {"name":"John", "password":"password", "email":"email"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_invalid_email(self):
        print("State: Testing signup with invalid email format")
        payload = {"name":"John", "password":"John@1234", "email":"johnmail"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_invalid_char_in_email(self):
        print("State: Testing signup with invalid characters in email")
        payload = {"name":"John", "password":"John@1234", "email":"john&@gmail.com"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_invalid_char_in_password(self):
        print("State: Testing signup with invalid characters in password")
        payload = {"name":"John", "password":"Joh<n@1234", "email":"john@gmail.com"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def test_user_already_exists(self):
        print("State: Testing signup for existing user")
        payload = {"name":"Abhishek", "password":"Abhi@12345", "email":"abhishek@gmail.com"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def valid_signup_to_pending_signup_without_mail_verification(self):
        print("State: Testing valid signup added to pending without email verification")
        payload = {"name":"Samay", "password":"Samay@1234", "email":"samay@gmail.com"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output: ", response.text)

    def valid_singup_to_pending_signup_with_mail_verification(self):
        print("State: Testing valid signup with email verification process")
        payload = {"name":"Samay", "password":"Samay@1234", "email":"samay@gmail.com"}
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print("Output for signup: ", response.text)

        try:
            email = response.json().get('user')  # Safely get email from response
            print("State: Retrieved user email for verification", email)

            # Verify the email
            print("State: Attempting to verify email")
            res = requests.post(f"{BASE_URL}/verify_email/{email}/signup", json={"otp":"123456"})
            print("Output for email verification: ", res.text)
        except (ValueError, KeyError, AttributeError) as e:
            print("Error: Could not process email verification - ", str(e))

def main():
    tester = TestSignup()
    tester.test_empty_payload()
    tester.test_empty_name()
    tester.test_empty_email()
    tester.test_empty_password()
    tester.test_invalid_password()
    tester.test_invalid_email()
    tester.test_invalid_char_in_email()
    tester.test_invalid_char_in_password()
    tester.test_user_already_exists()
    tester.valid_signup_to_pending_signup_without_mail_verification()
    tester.valid_singup_to_pending_signup_with_mail_verification()

if __name__ == "__main__":
    # main()
    