from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User
from utils.hashing import hash_password

def create_admin():
    db: Session = SessionLocal()
    
    # Check if admin with same email or username already exists
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip()
    
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        print(f"User with username '{username}' or email '{email}' already exists. Aborting.")
        db.close()
        return
    
    # Check if any admin already exists (optional - remove if you want multiple admins)
    existing_admin = db.query(User).filter_by(role="admin").first()
    if existing_admin:
        response = input("An admin already exists. Create another admin? (y/n): ").strip().lower()
        if response != 'y':
            print("Aborting.")
            db.close()
            return

    password = input("Admin password: ").strip()
    
    if len(password) < 6:
        print("Password must be at least 6 characters long. Aborting.")
        db.close()
        return

    # Hash password using the same method as the rest of the application
    password_hash = hash_password(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role="admin",
        token_version=0
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Admin created successfully with ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
