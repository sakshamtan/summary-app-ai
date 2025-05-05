from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db, User, init_db
from dotenv import load_dotenv
import groq
import logging
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from local.env
load_dotenv('local.env')

# Debug environment variables
logger.info("Checking environment variables...")
logger.info(f"GROQ_API_KEY exists: {'GROQ_API_KEY' in os.environ}")
logger.info(f"SECRET_KEY exists: {'SECRET_KEY' in os.environ}")

# Initialize Groq client
try:
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Groq client: {str(e)}")
    raise

# Initialize database
init_db()

app = FastAPI(title="Summary Generator API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class TextInput(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str

class BulletPointsResponse(BaseModel):
    bullet_points: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.cookies.get("token")
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = Response(
        content="Login successful",
        status_code=status.HTTP_200_OK
    )
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to False for development
        samesite="lax",  # More permissive than 'strict'
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"  # Make sure the cookie is available on all paths
    )
    return response

@app.post("/logout")
async def logout():
    response = Response(content="Logged out successfully")
    response.delete_cookie("token")
    return response

async def generate_summary_with_llm(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise and informative summaries."},
                {"role": "user", "content": f"Please provide a clear and concise summary of the following text:\n\n{text}"}
            ],
            max_tokens=150,
            temperature=0.7,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in generate_summary_with_llm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )

async def generate_bullet_points_with_llm(text: str) -> List[str]:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates clear and concise bullet points."},
                {"role": "user", "content": f"Please provide 3-5 key bullet points from the following text:\n\n{text}"}
            ],
            max_tokens=200,
            temperature=0.7,
            stream=False
        )
        # Split the response into bullet points and clean them up
        bullet_points = response.choices[0].message.content.strip().split('\n')
        # Remove any empty points and clean up formatting
        bullet_points = [point.strip('- ').strip() for point in bullet_points if point.strip()]
        return bullet_points
    except Exception as e:
        logger.error(f"Error in generate_bullet_points_with_llm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating bullet points: {str(e)}"
        )

@app.post("/generate-summary/", response_model=SummaryResponse)
async def generate_summary(
    text_input: TextInput,
    current_user: User = Depends(get_current_user)
):
    summary = await generate_summary_with_llm(text_input.text)
    return SummaryResponse(summary=summary)

@app.post("/generate-bullet-points/", response_model=BulletPointsResponse)
async def generate_bullet_points(
    text_input: TextInput,
    current_user: User = Depends(get_current_user)
):
    bullet_points = await generate_bullet_points_with_llm(text_input.text)
    return BulletPointsResponse(bullet_points=bullet_points)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 