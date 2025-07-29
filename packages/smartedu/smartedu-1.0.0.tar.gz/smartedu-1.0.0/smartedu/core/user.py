# Create an super class User to accept user_id,name and email. Then create child classes student to inherit from User.

class User:
    def __init__(self,user_id,name,email):
        self._user_id = user_id
        self._name = name 
        self._email = email
        
    def display_info():
        print(f"User ID: {self._user_id}, Name:{self._name}, Email ID: {self._email}")

    @property
    def user_id(self):
        return self._user_id