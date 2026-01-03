from fastapi import FastAPI,Depends,status,HTTPException,Response
import uvicorn
from auth import oauth2_schema
from typing import Annotated
from schema import RegisterRequest,LoginRequest,PostRequest,LikeRequest,CommentRequest,CommentResponse,Comment_Schema
from model import Register,Posts,CategoryModel,PostCategoryModel,LikeModel,CommentModel
from database import engine,Base,db_dependancy
from fastapi.middleware.cors import CORSMiddleware
from hash import hash_password,verify_password
from jwt_token import create_access_token
from current_user import require_permission
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import and_,or_

app=FastAPI()

origins = [
    "http://127.0.0.1:5501",  # frontend
    "http://localhost:5501",
]

Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post('/login')
def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependancy,response:Response):
    try:
        user_name=db.query(Register).filter(Register.name==form_data.username).first()
        if not user_name:
            raise HTTPException(status_code=400,detail="user is not register")
        if not verify_password(form_data.password,user_name.password):
            raise HTTPException(status_code=400,detail="password is wrong")
        
        access_token=create_access_token(subject=user_name.name,            
        role=user_name.role )
        response.set_cookie(
            key="access_token", 
            value=access_token, 
            httponly=True,   
            max_age=3600,    
            samesite="lax",  # Keep as lax for local dev
            secure=False,    # Keep false for HTTP local dev
            path="/",        # Ensure cookie is valid for all paths
        )
        user_detail={
            "name":user_name.name,
            "role":user_name.role,
            "email":user_name.email,
            "address":user_name.address
        }
        return {"msg":"login sucessfully","access_token":access_token,"user_detail":user_detail}

    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")

@app.post('/register')
def register(request:RegisterRequest,db:db_dependancy):
    exist_name=db.query(Register).filter(Register.email==request.email).first()
    if exist_name:
        raise HTTPException(status_code=409,detail=f"user email {request.email} alredy exist")
    
    hash_pass=hash_password(request.password)
    new_user=Register(
        name=request.name,
        address=request.address,
        email=request.email,
        password=hash_pass
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg":"add new user","request":new_user}

@app.post("/blog/post")
def post_blog(post:PostRequest,db:db_dependancy,current_user=Depends(require_permission('write'))):
    user=db.query(Register).filter(Register.name==current_user["username"]).first()
    if not user:
        raise HTTPException(status_code=409,detail=f"user email {current_user.username} alredy exist")
    
    new_post=Posts(
        content=post.content,
        title=post.title,
        user_id=user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    new_category=CategoryModel(
        category_name=post.category
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    post_category=PostCategoryModel(
        category_id=new_category.category_id,
        post_id=new_post.id
    )
    db.add(post_category)
    db.commit()
    db.refresh(post_category)
    return {"msg":"add new post","request":new_post}

@app.get("/blog/post")
def get_post(db:db_dependancy,current_user=Depends(require_permission('view'))):
   
    post=db.query(Posts).all()
    if not post:
        raise HTTPException(status_code=404,detail="Not found")
    return post

@app.get("/blog/edit")
def get_post_edit(db:db_dependancy,current_user=Depends(require_permission('edit'))):
    user=db.query(Register).filter(Register.name==current_user["username"]).first()
    if user=="Author":
        raise HTTPException(403,detail="you are not the author")
    
    post=db.query(Posts).filter(Posts.user_id==user.id).all()

    return post
@app.get("/blog/post/{id}")
def get_post_by_title(id:int,db:db_dependancy,current_user=Depends(require_permission('view'))):
    print(id)
    post=db.query(Posts).filter(Posts.id==id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    
    return post

@app.get("/blog/edit/show/{id}")
def get_post_show(id:int,db:db_dependancy,current_user=Depends(require_permission('edit'))):
    post=db.query(Posts).filter(Posts.id==id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    return post
    

@app.delete("/blog/post/{id}")
def delete_post(id:int,db:db_dependancy,current_user=Depends(require_permission('delete'))):
    post=db.query(Posts).filter(Posts.id==id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    db.delete(post)
    db.commit()
    return {"msg":"delete post"}

@app.post("/blog/post/like")
def post_like(like:LikeRequest,db:db_dependancy,current_user=Depends(require_permission('view'))):

    post=db.query(Posts).filter(Posts.id==like.post_id).first()
    if not post:
        raise HTTPException(404,detail="Post not found") 
    print(post)
    liked_alredy=db.query(LikeModel).filter(LikeModel.post_id==post.id).first()
    if liked_alredy:
        db.delete(liked_alredy)
        db.commit()
        return {"msg":"post not liked","like":"false"}
    print(liked_alredy)
    user=db.query(Register).filter(Register.name==current_user["username"]).first()

    like=LikeModel(
        post_id=post.id,
        user_id=user.id
    )
    db.add(like)
    db.commit()
    db.refresh(like)

    return {"msg":f"like {post.id} by user {user.name}","like":"true"}

@app.get("/blog/post/like/{post_id}")
def get_post_id(post_id:int,db:db_dependancy,current_user=Depends(require_permission('view'))):
    # print(type(post_id))
    post=db.query(Posts).filter(Posts.id==post_id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    user=db.query(Register).filter(Register.name==current_user["username"]).first()
   
    like=db.query(LikeModel).filter(and_(LikeModel.post_id==post.id,LikeModel.user_id==user.id)).all()
  
    if like:
        return {"msg":"true","total":len(like)}
    return {"msg":"false","total":len(like)}


@app.post("/blog/post/comment")
def post_comment(comment:CommentRequest,db:db_dependancy,current_user=Depends(require_permission('view'))):
    post=db.query(Posts).filter(Posts.id==comment.post_id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    
    if comment.content=="":
        raise HTTPException(404,detail="Empty")
    
    user=db.query(Register).filter(Register.name==current_user["username"]).first()

    new_comment=CommentModel(
        post_id=post.id,
        content=comment.content,
        user_id=user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {"msg":"new comment is added","comment":new_comment.content}
   
@app.get("/blog/post/comment/{post_id}")
def get_comment(post_id:int,db:db_dependancy,current_user=Depends(require_permission('view'))):
    post=db.query(Posts).filter(Posts.id==post_id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    
    comment=db.query(CommentModel).filter(CommentModel.post_id==post.id).all()
    list=[Comment_Schema(
        comment=com.content,
        user_name=com.user.name
    ) for com in comment]

    return CommentResponse(comment_list=list)
@app.get("/blog/post/comment/total/{post_id}")
def get_comment(post_id:int,db:db_dependancy,current_user=Depends(require_permission('view'))):
    post=db.query(Posts).filter(Posts.id==post_id).first()
    if not post:
        raise HTTPException(404,detail="Post not found")
    
    comment=db.query(CommentModel).filter(CommentModel.post_id==post.id).all()
    

    return {"total_comment":len(comment)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)