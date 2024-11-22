from fastapi import HTTPException

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_user, login_user, verify_token, users_collection, admin_required, verify_password, \
    create_access_token

from schemas import UserResponse, UserCreate

app = FastAPI()

@app.post("/users/", response_model=UserResponse)
async def register_user(user: UserCreate):
    return await create_user(user)

# Route pour se connecter et obtenir un JWT
@app.post("/login")
async def login_user(credentials: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": credentials.username})
    if user is None:
        print("User not found:", credentials.username)  # Ajouter un log
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(credentials.password, user['password']):
        print("Password mismatch for user:", credentials.username)  # Ajouter un log
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
#test api "hello world"
@app.get("/")
async def read_root():
    return {"Hello": "Wo"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)