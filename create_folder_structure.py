import os


def create_project_structure():
    """
    Creates a FastAPI project structure with the specified directories and files.
    """

    # Define the directory structure
    directories = [
        "ragoo",
        "ragoo/core",
        "ragoo/database",
        "ragoo/schemas",
        "ragoo/services",
        "ragoo/routes",
        "ragoo/vectorestore",
        "tests",
    ]

    # Define the files and their content (can be empty)
    files = {
        "ragoo/__init__.py": "",
        "ragoo/core/__init__.py": "",
        "ragoo/core/config.py": "# Application configuration goes here",
        "ragoo/core/security.py": "# Security-related functions (JWT, password hashing)",
        "ragoo/database/__init__.py": "",
        "ragoo/database/database.py": "# Database connection and session management",
        "ragoo/database/models.py": "# SQLAlchemy models",
        "ragoo/schemas/__init__.py": "",
        "ragoo/schemas/user.py": "# User schemas (Pydantic)",
        "ragoo/schemas/document.py": "# Document schemas (Pydantic)",
        "ragoo/schemas/query.py": "# Query schemas for LLM",
        "ragoo/services/__init__.py": "",
        "ragoo/services/user_service.py": "# User service logic",
        "ragoo/services/rag_service.py": "# RAG service logic",
        "ragoo/routes/__init__.py": "",
        "ragoo/routes/user_routes.py": "# User routes (API endpoints)",
        "ragoo/routes/rag_routes.py": "# RAG routes (API endpoints)",
        "ragoo/vectorestore/__init__.py": "",
        "ragoo/vectorestore/chroma_handler.py": "# Logic to implement vector database using chroma",
        "ragoo/vectorestore/vectorstore_interface.py": "# to make the vectorstore agnostic",
        "ragoo/vectorestore/vectorstore_manager.py": "# Class that handles the initialization of vectorestore",
        "ragoo/main.py": "# FastAPI application initialization",
        "tests/__init__.py": "",
        "tests/conftest.py": "# Fixtures for testing",
        "tests/test_user_routes.py": "# Test user routes",
        "tests/test_rag_routes.py": "# Test rag routes",
        ".env": "DEBUG=True\n# Add other environment variables here",
        "requirements.txt": "fastapi\nuvicorn[standard]\npydantic\nSQLAlchemy\n# Add other dependencies here",
        "README.md": "# Project Description\n\n## Setup Instructions\n\n...\n",
        "docker-compose.yml": '# Docker compose configuration\n\nversion: "3.9"\nservices:\n  web:\n    build: .\n    ports:\n      - "8000:8000"\n    volumes:\n      - .:/app\n    command: uvicorn ragoo.main:app --host 0.0.0.0 --reload',
    }

    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    # Create files
    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created file: {filepath}")


if __name__ == "__main__":
    create_project_structure()
    print("Project structure created successfully.")
