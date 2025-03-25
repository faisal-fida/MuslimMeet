from fastapi import FastAPI
from app.routers import auth, users, matches, chats, location
from app.database import Base, engine

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(chats.router, prefix="/api/chats", tags=["Chats"])
app.include_router(location.router, prefix="/api/location", tags=["Location"])
