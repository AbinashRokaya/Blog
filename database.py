from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from typing import Annotated
from fastapi import Depends
import os


DATABASE_URL = os.getenv("DATABASE_URL", "").replace(
    "postgres://", "postgresql://"  # Render sometimes returns "postgres://"
)

engine=create_engine(DATABASE_URL)
sessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base=declarative_base()



def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy=Annotated[Session,Depends(get_db)]