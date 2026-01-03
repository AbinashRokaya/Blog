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
    comments=relationship(
        "CommentModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title=Column(String,nullable=False)
    user_id = Column(Integer, ForeignKey("register.id", ondelete="CASCADE"))
    content = Column(String, nullable=False)

    user = relationship("Register", back_populates="posts")

    
class CategoryModel(Base):
    __tablename__="category"

    category_id=Column(Integer,primary_key=True,index=True)
    category_name=Column(String,default=None)

class PostCategoryModel(Base):
    __tablename__="postcategory"
    id=Column(Integer,primary_key=True,index=True)
    category_id=Column(Integer,ForeignKey("category.category_id",ondelete="CASCADE"))
    post_id=Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"))

class LikeModel(Base):
    __tablename__="likes"
    like_id=Column(Integer,primary_key=True,index=True)
    post_id=Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"))
    user_id=Column(Integer,ForeignKey("register.id",ondelete="CASCADE"))

class CommentModel(Base):
    __tablename__="comment"
    comment_id=Column(Integer,primary_key=True,index=True)
    post_id=Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"))
    user_id=Column(Integer,ForeignKey("register.id",ondelete="CASCADE"))
    content=Column(String)

    user = relationship("Register", back_populates="comments")