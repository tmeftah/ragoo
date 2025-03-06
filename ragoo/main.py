# FastAPI application initialization
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ragoo.routes import user_routes, rag_routes, health
from ragoo.database import models
from ragoo.database.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost",  # Adjust this to the specific origins you need to allow
    "http://localhost:8080",  # adjust this to the port you want to allow
    "https://your-frontend-domain.com",  # replace with your domain
    "*",  # WARNING:  Allowing all origins is generally  NOT recommended for production due to security reasons.  Use with caution and *only* if you absolutely need it and understand the risks.
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allows all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)


app.include_router(health.router)  # Add this line
app.include_router(user_routes.router, prefix="/users")
app.include_router(rag_routes.router, prefix="/rag")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
