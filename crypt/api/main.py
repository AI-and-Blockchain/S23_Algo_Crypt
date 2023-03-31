from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    algorand_address = Column(String, unique=True, index=True)
    password = Column(String)

    def __repr__(self):
        return f"<User {self.algorand_address}>"


Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    algorand_address: str
    password: str


class UserLogin(BaseModel):
    algorand_address: str
    password: str


class HashedPassword(BaseModel):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/signup")
async def signup(user: UserCreate):
    db = SessionLocal()
    hashed_password = get_password_hash(user.password)
    query = User.__table__.insert().values(
        algorand_address=user.algorand_address, password=hashed_password
    )
    try:
        db.execute(query)
        db.commit()
        return {"message": "User created successfully"}
    except:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Algorand address already exists"
        )
    finally:
        db.close()


@app.post("/login")
async def login(user: UserLogin):
    db = SessionLocal()
    query = User.__table__.select().where(
        User.algorand_address == user.algorand_address
    )
    result = db.execute(query).first()
    if not result:
        raise HTTPException(
            status_code=400, detail="Invalid algorand address or password"
        )
    if not verify_password(user.password, result.password):
        raise HTTPException(
            status_code=400, detail="Invalid algorand address or password"
        )
    return {"message": "Login successful"}