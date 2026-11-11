import hashlib, hmac
from database import query, execute

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), stored_hash)

def create_user(username, password, role):
    if role not in ("admin", "faculty", "student"):
        raise ValueError("Invalid role.")
    return execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                   (username.strip(), hash_password(password), role))

def authenticate(username, password):
    rows = query("SELECT * FROM users WHERE username=? AND active=1", (username.strip(),))
    if rows and verify_password(password, rows[0]["password_hash"]):
        return {k: rows[0][k] for k in ("id", "username", "role")}
    return None

def change_password(user_id, new_password):
    execute("UPDATE users SET password_hash=? WHERE id=?",
            (hash_password(new_password), user_id))
