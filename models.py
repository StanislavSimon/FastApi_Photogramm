from sqlalchemy import Column, Integer, String
from passlib.context import CryptContext
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def set_password(self, password: str):
        self.hashed_password = self.pwd_context.hash(password)

    def verify_password(self, password: str):
        return self.pwd_context.verify(password, self.hashed_password)
