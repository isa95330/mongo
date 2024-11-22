import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends

from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer
from schemas import UserCreate, UserResponse

# Charger les variables d'environnement depuis .env
load_dotenv()

# Connexion à MongoDB
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client["userdatabase"]
users_collection = db["users"]

# CryptContext pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer récupère le token JWT envoyé avec la requête
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fonction pour hacher le mot de passe
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Fonction pour vérifier le mot de passe
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Créer un JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Fonction pour créer un utilisateur
async def create_user(user: UserCreate) -> UserResponse:
    hashed_password = hash_password(user.password)
    new_user = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "password": hashed_password,
        "address": user.address,  # Ajoutez l'adresse
        "phone_number": user.phone_number,  # Ajoutez le numéro de téléphone
        "is_admin": user.is_admin  # Assurez-vous que ce champ est géré
    }
    result = await users_collection.insert_one(new_user)
    return UserResponse(
        id=str(result.inserted_id),
        first_name=new_user["first_name"],
        last_name=new_user["last_name"],
        email=new_user["email"],
        is_admin=new_user.get("is_admin", False),
        address=new_user["address"],  # Ajoutez l'adresse
        phone_number=new_user["phone_number"]  # Ajoutez le numéro de téléphone
    )



# Fonction pour se connecter et retourner un JWT
async def login_user(email: str, password: str) -> dict:
    user = await users_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"], "is_admin": user.get("is_admin", False)},
            expires_delta=access_token_expires
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {str(e)}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False),
        }
    }


# Fonction pour vérifier les droits d'administration
async def admin_required(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=403,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        is_admin: bool = payload.get("is_admin", False)
        if not is_admin:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

# Vérifier et extraire les informations du token JWT
def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return email