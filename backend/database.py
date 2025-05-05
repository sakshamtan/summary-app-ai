from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

SQLALCHEMY_DATABASE_URL = "sqlite:///./summary_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create a test user if none exists
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "testuser").first():
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=bcrypt.hashpw("secret".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True
            )
            db.add(test_user)
            db.commit()
    finally:
        db.close() 