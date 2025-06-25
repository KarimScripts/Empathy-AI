from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query, where
from typing import List
from datetime import datetime, timedelta
import uuid

# --- Local AI Modules ---
from empathy_ai.emotion_detector import EmotionDetector
from empathy_ai.response_generator import ResponseGenerator

# --- Configuration ---
SECRET_KEY = "a-very-secret-key"  # In production, use a secure, environment-variable-managed key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Database ---
db = TinyDB('users_db.json')
users_table = db.table('users')
chat_history_table = db.table('chat_history')
UserQuery = Query()

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Pydantic Models ---
class User(BaseModel):
    username: str
    name: str

class UserCreate(User):
    password: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class ChatTurn(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    title: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[ChatTurn] = []

class ConversationSummary(BaseModel):
    id: str
    title: str
    timestamp: str

class ChatRequest(BaseModel):
    user_message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    ai_response: str
    conversation_id: str
    detected_emotion: str | None = None

# --- Auth Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = users_table.get(UserQuery.username == token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    # In the future, you could add a `disabled` flag to the user model
    # and check it here.
    return current_user

# --- Helper Functions ---
def generate_chat_title(message: str) -> str:
    """Generates a short title from the first user message."""
    words = message.split()
    title = " ".join(words[:5])
    if len(words) > 5:
        title += "..."
    return title

# --- App Initialization ---
app = FastAPI(
    title="Empathy AI",
    description="A conversational AI with a focus on empathetic communication.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI Components ---
emotion_detector = EmotionDetector()
response_generator = ResponseGenerator()

# --- API Endpoints ---
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_table.get(UserQuery.username == form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/signup", response_model=User)
async def signup_user(user: UserCreate):
    db_user = users_table.get(UserQuery.username == user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    users_table.insert({
        'username': user.username, 
        'name': user.name, 
        'hashed_password': hashed_password
    })
    return User(username=user.username, name=user.name)

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    # Ensure the response always includes the name by explicitly creating the Pydantic model.
    return User(username=current_user['username'], name=current_user.get('name', 'friend'))

@app.get("/history", response_model=List[ConversationSummary])
async def get_history(current_user: User = Depends(get_current_active_user)):
    user_chats = chat_history_table.search(where('username') == current_user['username'])
    # Sort by timestamp, newest first
    sorted_chats = sorted(user_chats, key=lambda x: x['timestamp'], reverse=True)
    return [ConversationSummary(**chat) for chat in sorted_chats]

@app.get("/history/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str, current_user: User = Depends(get_current_active_user)):
    conversation_doc = chat_history_table.get(
        (where('id') == conversation_id) & (where('username') == current_user['username'])
    )
    if not conversation_doc:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return Conversation(**conversation_doc)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Main chat endpoint. Receives user message and optional conversation ID.
    Handles conversation persistence and returns AI response.
    """
    user_message_turn = ChatTurn(role="user", content=request.user_message)

    if request.conversation_id:
        # Load existing conversation
        conversation_doc = chat_history_table.get(where('id') == request.conversation_id)
        if not conversation_doc or conversation_doc['username'] != current_user['username']:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation = Conversation(**conversation_doc)
        conversation.messages.append(user_message_turn)
    else:
        # Create new conversation
        conversation = Conversation(
            username=current_user['username'],
            title=generate_chat_title(request.user_message),
            messages=[user_message_turn]
        )

    # 1. Detect emotion from the user's message
    emotion_data = emotion_detector.detect_emotion(request.user_message)
    detected_emotion = emotion_data.get("emotion", "neutral")

    # 2. Generate an empathetic response
    recent_context = conversation.messages[-10:] # Use last 10 turns for context
    ai_response_text = response_generator.generate_response(
        emotion=detected_emotion,
        user_message=request.user_message,
        recent_context=recent_context
    )
    
    ai_response_turn = ChatTurn(role="ai", content=ai_response_text)
    conversation.messages.append(ai_response_turn)

    # 3. Save conversation to DB
    chat_history_table.upsert(conversation.dict(), where('id') == conversation.id)

    return ChatResponse(
        ai_response=ai_response_text,
        detected_emotion=detected_emotion,
        conversation_id=conversation.id
    ) 