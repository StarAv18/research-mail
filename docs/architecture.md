# Research Internship Agent - Architecture

## Overview
The Research Internship Agent is designed using Clean Architecture principles to ensure maintainability, scalability, and testability. The project is split into a Next.js frontend and a FastAPI backend.

## Tech Stack
- **Frontend**: Next.js, TypeScript, TailwindCSS
- **Backend**: FastAPI
- **Storage**: Local JSON files (Repository Pattern for easy migration to DB later)
- **AI**: Provider Pattern supporting Ollama, OpenRouter, and Gemini

## Project Structure

### Root Directory
- `/frontend`: Next.js application.
- `/backend`: FastAPI application.
- `/docs`: Project documentation and architecture details.

### Backend Architecture (`/backend/app`)
Follows a modular structure where business logic is separated from the API layer.

- **`api/`**: Contains API route handlers (Controllers). Versioned (e.g., `v1/`).
    - **`v1/discovery.py`**: Professor profile extraction.
    - **`v1/drafts.py`**: CRUD for email outreach drafts.
    - **`v1/outreach.py`**: AI email generation and bulk sending.
- **`core/`**: Centralized configuration (`config.py`), security, and error handling. Uses `pydantic-settings` for environment management.
- **`models/`**: Pydantic schemas for data validation and standardized API responses (`response.py`).
- **`services/`**: Business logic layer.
    - **`university_scraper.py`**: Robust scraper for professor profiles using requests/BS4.
    - **`ai/`**: Implementation of the Provider Pattern for AI models.
        - `base.py`: Abstract base class for AI providers.
        - `ollama.py`, `openrouter.py`, `gemini.py`: Specific provider implementations.
    - **`summarization.py`**: Refactored service with improved parsing and template usage.
    - **`email_generation.py`**: AI-driven personalized email generation.
    - **`outreach_service.py`**: Business logic for tracking communications.
    - **`bulk_email_service.py`**: Orchestration for mass outreach and provider integration.
    - **`safety_service.py`**: Guardrails for daily limits and duplicate prevention.
- **`repository/`**: Data access layer. Handles storage abstraction.
    - **`draft_repository.py`**: JSON-based storage for email drafts.
    - **`outreach_repository.py`**: JSON-based storage for communication history.
- **`data/`**: Directory where JSON data files are stored.
- **`tests/`**: Unit and integration tests using Pytest.

## Security & Reliability
- **Configuration**: Managed via `BaseSettings` for secure environment variable handling.
- **Standardized Responses**: All API endpoints return a consistent `APIResponse` format to simplify frontend integration.
- **Concurrency**: The Repository layer should implement file locking or use a proper database if concurrent writes become a bottleneck.
- **State Management**: Frontend uses `zustand` for lightweight, scalable state management.

### Frontend Architecture (`/frontend/src`)
Uses Next.js App Router and a component-based architecture.

- **`app/`**: Next.js pages, layouts, and routing logic.
- **`components/`**: Reusable UI components.
- **`hooks/`**: Custom React hooks for shared logic.
- **`services/`**: API client logic to communicate with the FastAPI backend.
- **`types/`**: TypeScript interfaces and types for frontend-specific data.
- **`lib/`**: Utility functions, constants, and configurations.

## AI Provider Pattern
The backend implements a Provider Pattern for AI interactions. 
1. An abstract base class defines the `generate` and `stream` methods.
2. Concrete classes implement these methods for Ollama, OpenRouter, and Gemini.
3. A factory or dependency injection mechanism provides the correct provider based on configuration.

## Data Storage
Initially, data is stored in JSON files. The `repository` layer abstracts these operations, making it trivial to swap JSON storage for a database like PostgreSQL or MongoDB in the future without changing the business logic in `services`.
