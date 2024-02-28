import hashlib
import re
import sqlite3
from typing import Tuple

from funix import funix_method, funix_class, funix
from funix.hint import Image, Video


def __init_database():
    con = sqlite3.connect("tutorial.db", check_same_thread=False)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user      TEXT    NOT NULL UNIQUE,
        password  TEXT    NOT NULL
    )
    """)
    con.commit()
    return con


db = __init_database()


def __is_valid_username(username: str):
    if len(username) < 3:
        return False

    if not username[0].isalpha():
        return False

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False

    if username.endswith('_'):
        return False

    return True


def __is_valid_password(pwd: str):
    if len(pwd) < 8:
        return False

    if not re.match(r'^[a-zA-Z0-9_!@#$%^&*]+$', pwd):
        return False

    if pwd.endswith('_'):
        return False

    return True


@funix(disable=True)
def validate_user(username: str, password: str) -> bool:
    cur = db.cursor()
    _hash: str = cur.execute(
        "SELECT password FROM users WHERE user = ?;",
        (username,)
    ).fetchone()
    if _hash is None:
        return False
    _hash = _hash[0]

    login_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    return login_hash == _hash


@funix(
    title="Register",
    widgets={"password": "password"},
)
def register(username: str, password: str) -> str:
    """
    Simple register for demo purpose
    """
    if not __is_valid_username(username):
        return "Invalid username"

    cur = db.cursor()
    count = cur.execute(
        "SELECT COUNT(*) FROM users WHERE user = ?;",
        (username,)
    ).fetchone()
    if count is None:
        return "Database error"
    count = count[0]

    if count > 0:
        return "This username is already taken"

    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cur.execute("INSERT INTO users (user, password) VALUES (?, ?)", (username, pwd_hash))
    db.commit()

    return "Register successfully!"


@funix_class()
class Manager:
    session = None

    @funix_method(
        title="Login to System",
        description="Login to the system using your username and password",
        widgets={"password": "password"},
        print_to_web=True,
    )
    def __init__(self, username: str, password: str):
        if validate_user(username, password):
            self.session = username  # fake session for demo purpose
            print(f"Welcome {username}")
        else:
            raise Exception("Invalid username or password")

    @funix_method(
        title="My Info"
    )
    def my_info(self) -> str:
        return f"Your username: {self.session}"

    @funix_method(
        title="Review Multimedia",
    )
    def review_multimedia(self) -> Tuple[Image, Video]:
        if self.session is None:
            raise Exception("You need to login first")
        else:
            return (
                "https://picsum.photos/200/300",
                "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            )

