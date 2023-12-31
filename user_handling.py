from locale import currency
import sqlite3
import logging
from flask.sessions import SessionMixin

def get_db():
    con = sqlite3.connect("datenbank.db")
    cur = con.cursor()
    return con, cur

class User:
    def __init__(self, username, password, priviledge, current_key) -> None:
        self.username = username
        self.password = password
        self.priviledge = priviledge
        self.current_key = current_key
    
    def is_authorized(self, level: int):
        logging.debug(f"Trying to authorize {self} to Level: {level}")
        return self.priviledge >= level
    
    def get_key(self):
        return self.current_key
    
    def set_key(self, key: str):
        self.current_key = key
    
    def __str__(self):
        return f"Username: {self.username} || Password: {self.password} || Priviledge: {self.priviledge}"

users: list[User] = []

def load_users():
    con, cur = get_db()

    cur.execute("SELECT * FROM users")

    res = cur.fetchall()
    con.close()

    for result in res:
        users.append(User(result[1], result[2], result[3], result[4]))

def get_user_from_key(key: str) -> User | None:
    """Gets a user with a given key

    Args:
        key (str): The key

    Returns:
        User | bool: If a user could be found, returns the user. If not returns false
    """
    for user in users:
        if user.current_key == key:
            return user
    return

def get_user_from_username_and_password(username: str, password: str) -> User | None:
    logging.debug(f"All Users: {str(users)}")
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None

def authenticate_user(session: SessionMixin, required_level: int)  -> bool:
    """Authenticates the user, if authentication fails, returns False

    Args:
        session (SessionMixin): The user's session
        required_level (int): The level required for authentication

    Returns:
        bool: If the user has been authenticated
    """
    if 'secret' in session:
        logging.info("Secret in session")
        user = get_user_from_key(session["secret"])
        if not user:
            return False
        
        if user.priviledge >= required_level:
            return True
        else:
            return False
    else:
        logging.info("Secret NOT in session")
        return False

