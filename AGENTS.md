# Agent Instructions

This document provides instructions for AI agents working on this codebase.

## Development Conventions

*   **Code Style**: Follow the PEP 8 style guide for Python code.
*   **Commit Messages**: Write clear and concise commit messages. The first line should be a short summary (50 characters or less), followed by a blank line and a more detailed description if necessary.

## Running the Application

To run the application, you need to start both the backend server and the frontend server.

### Backend

1.  Navigate to the `app` directory:
    ```bash
    cd app
    ```
2.  Run the ADK web server:
    ```bash
    adk web --allow_origins http://localhost:8080
    ```

### Frontend

1.  In a separate terminal, navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Start the Python HTTP server:
    ```bash
    python3 -m http.server 8080
    ```

## Code Review Checklist

Before submitting any changes, ensure that you have:

1.  Run all relevant tests and they pass.
2.  Verified that your changes work as expected by running the application locally.
3.  Updated the `AGENTS.md` file if any of your changes affect the development conventions or running instructions.
4.  Requested a code review using the `request_code_review` tool.
