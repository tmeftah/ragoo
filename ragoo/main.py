# FastAPI application initialization
from fastapi import FastAPI
from .routes import user_routes, rag_routes, health
from .database import models
from .database.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(health.router)  # Add this line
app.include_router(user_routes.router, prefix="/users")
app.include_router(rag_routes.router, prefix="/rag")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
