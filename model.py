from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from role import Role_Schema


class Register(Base):
    __tablename__ = "register"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(
        Enum(Role_Schema, name="role_enum"),
        default=Role_Schema.User,
        nullable=False
    )

    posts = relationship(
        "Posts",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("register.id", ondelete="CASCADE"))
    content = Column(String, nullable=False)

    user = relationship("Register", back_populates="posts")

