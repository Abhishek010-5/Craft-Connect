import requests


reponse = requests.get("http://localhost:5000/user/get_user_profile",json={"email":"abhishek@gmail.com"}).text
print(reponse)