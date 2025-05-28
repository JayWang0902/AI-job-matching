from app.models.user import User
from sqlalchemy.orm import Session

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:  # Simplified password check (hash in production)
        return user
    return None
