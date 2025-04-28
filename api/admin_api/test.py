import requests

BASE_URL = "http://localhost:5000/admin"

class Admin:
    # Test for pending signups it is get mehtod
    def pending_signups(self):
        print("Calling the route pending signups")
        response = requests.get(f"{BASE_URL}/pending_signups").text
        print({"Response for pending singups":response})
    
    # test for approve or reject pendind signups
    def approve_or_reject(self):
        print("Testing approver or rject pending signups")
        print("Test with no JSON")
        response = requests.post(f"{BASE_URL}/approve_or_reject_pending_signups").text
        print(response)
        
        # test for empty json
        print("Test for the empty JSON ")
        payload = {}
        response = requests.post(f"{BASE_URL}/approve_or_reject_pending_signups",json=payload).text
        print(response)
        
        # test one filed missing
        print("Test for one filed missing (status)")
        payload = {"email":"kapil@gmail.com","staus":""}
        response = requests.post(f"{BASE_URL}/approve_or_reject_pending_signups",json=payload).text
        print(response)
        
        # test for invalid email format
        print("Test for invalid email format")
        payload = {"email":"kapilgmail.com","status":"approved"}
        response = requests.post(f"{BASE_URL}/approve_or_reject_pending_signups",json=payload).text
        print(response)
        
        # test for valid invalid status
        print("Test for invlaid status")
        payload = {"email":"kapil@gmail.com","status":"approve"}
        response = requests.post(f"{BASE_URL}/approve_or_reject_pending_signups",json=payload).text
        print(response)
        
        # test for valid email and status
        print("Test for valid email and status")
        payload = {"email":"Kapil@gmail.com","status":"approved"}
        response = requests.post(f"{BASE_URL}/approve_or_reject_pending_signups",json=payload).text
        print(response)
        

    