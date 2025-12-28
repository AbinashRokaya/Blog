from fastapi import FastAPI,Depends,status,HTTPException,Response
import uvicorn
from auth import oauth2_schema
from typing import Annotated
from schema import RegisterRequest,LoginRequest,PostRequest
from model import Register,Posts
from database import engine,Base,db_dependancy
from fastapi.middleware.cors import CORSMiddleware
from hash import hash_password,verify_password
from jwt_token import create_access_token
from current_user import require_permission
from fastapi.security import OAuth2PasswordRequestForm

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
        user_id=user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"msg":"add new post","request":new_post}

@app.get("/blog/post")
def get_post(db:db_dependancy,current_user=Depends(require_permission('view'))):
    post=db.query(Posts).all()
    if not post:
        raise HTTPException(status_code=404,detail="Not found")
    return post

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)