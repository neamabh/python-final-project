# Task Management API

A Python-based Task Management API built with FastAPI.  
The project combines task management, data analysis, and AI-powered insights using Google's Gemini API.

## Features

### 1. Task Management (CRUD)
- Create new tasks.
- Retrieve all tasks or a specific task.
- Update existing tasks.
- Delete tasks.
- Identify overdue tasks and calculate days late.
- Validate task titles and priority levels.

### 2. Data Analysis
- Fetch users and tasks from JSONPlaceholder.
- Merge and process data using Pandas.
- Calculate task completion percentages.
- Generate performance statistics using NumPy.
- Identify users performing below average.
- Create a city-based pivot table.

### 3. AI Assistant
- AI-powered question answering using Google Gemini.
- Dynamic system prompt based on project data.
- Conversation history using conversation IDs.
- Mock responses when the Gemini API key is unavailable.

### 4. Security and Infrastructure
- API Key authentication.
- Request validation and error handling.
- Pagination and sorting.
- CORS configuration.
- Request logging and processing-time measurement.
- HTTP status codes for error handling.

### 5. AI Logging
- Log conversation IDs and timestamps.
- Track prompt and response lengths.
- Track successful, failed, and mock requests.
- Calculate AI usage statistics.

## Technologies

- Python
- FastAPI
- Pandas
- NumPy
- Pydantic
- Requests
- Google Gemini API
- Uvicorn

## Project Structure

```text
python-final-project/
│
├── main.py
├── task_service.py
├── data_service.py
├── analysis_service.py
├── ai_service.py
│
├── tasks.json
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd python-final-project
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
APP_API_KEY=your_api_key
GEMINI_API_KEY=your_gemini_api_key
```

Never commit your `.env` file or expose API keys publicly.

## Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{task_id}` | Get a specific task |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |
| GET | `/tasks/overdue` | Get overdue tasks |
| GET | `/stats/users` | User performance statistics |
| GET | `/stats/summary` | Overall performance summary |
| GET | `/stats/cities` | City completion statistics |
| GET | `/stats/low-performers` | Below-average performers |
| POST | `/ai/ask` | Ask the AI assistant |
| GET | `/ai/logs/stats` | AI usage statistics |

## Data Source

The project uses the JSONPlaceholder API to retrieve sample users and tasks.

## AI Integration

The project integrates Google's Gemini API to provide intelligent answers based on task data and analytical results.

Conversation history is maintained using conversation IDs, allowing the assistant to retain context across messages.

## Author

Developed as a Python Final Project.
