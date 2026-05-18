from database.db import execute_query


def login(username: str, password: str):
    rows = execute_query(
        "SELECT id,username,full_name,role FROM users "
        "WHERE username=%s AND password=SHA2(%s,256) AND is_active=1",
        (username, password), fetch=True,
    )
    return rows[0] if rows else None


def is_admin(user: dict) -> bool:
    return user.get("role") == "admin"
