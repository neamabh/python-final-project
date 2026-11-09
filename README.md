# Task Management API

A Python-based REST API built with **FastAPI**, combining task management, data analysis, and AI-powered insights using **Google Gemini**.

The project demonstrates backend development, data processing, API security, statistical analysis, and AI integration in one application.

## Features

### Task Management
- Create, retrieve, update, and delete tasks (CRUD).
- Retrieve a specific task by ID.
- Track overdue tasks and calculate days late.
- Validate task titles and priority levels.
- Store task information in a JSON file.

### Data Analysis
- Fetch sample users and tasks from JSONPlaceholder.
- Merge and process datasets using Pandas.
- Calculate task completion percentages.
- Generate statistical summaries using NumPy.
- Identify users performing below average.
- Analyze task completion by city using pivot tables.
- Support sorting and pagination.

### AI Assistant
- Integration with Google's Gemini API.
- Answer questions using project data and analytical results.
- Generate dynamic system prompts based on project statistics.
- Maintain conversation history using conversation IDs.
- Provide mock responses when the Gemini API key is unavailable.

### Security and Infrastructure
- API Key authentication using the `X-API-Key` header.
- Input validation and custom exception handling.
- Pagination and sorting.
- CORS configuration.
- Request logging and processing-time measurement.
- Appropriate HTTP status codes and error handling.

### AI Usage Logging
- Record conversation IDs and timestamps.
- Track prompt and response lengths.
- Track successful, failed, and mock requests.
- Generate AI usage statistics.

## Technologies Used

- Python
- FastAPI
- Pandas
- NumPy
- Pydantic
- Requests
- Google Gemini API
- Uvicorn
- Python-dotenv

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
├── .gitignore
└── README.md
```

**Note:** The `.env` file is created locally and is intentionally excluded from GitHub.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/neamabh/python-final-project.git
cd python-final-project
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

For Windows:

```bash
.\venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory of the project:

```env
APP_API_KEY=your_app_api_key
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder values with your own API keys.

**Security:** Never upload your `.env` file or expose API keys in a public repository.

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application will be available at:

http://127.0.0.1:8000

### Interactive API Documentation

FastAPI automatically generates Swagger documentation.

Open the following URL in your browser:

http://127.0.0.1:8000/docs

Use Swagger UI to explore and test the API endpoints.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check API status |
| GET | `/tasks` | Retrieve all tasks |
| GET | `/tasks/{task_id}` | Retrieve a specific task |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task |
| GET | `/tasks/overdue` | Retrieve overdue tasks |
| GET | `/stats/users` | User performance statistics |
| GET | `/stats/summary` | Overall performance summary |
| GET | `/stats/cities` | City-based completion statistics |
| GET | `/stats/low-performers` | Identify below-average performers |
| POST | `/ai/ask` | Ask the AI assistant |
| GET | `/ai/logs/stats` | Retrieve AI usage statistics |

**Authentication:** Protected endpoints require an API key in the `X-API-Key` request header.

## Data Source

The application uses [JSONPlaceholder](https://jsonplaceholder.typicode.com/) as an external source for sample user and task data.

The retrieved data is processed and analyzed to generate performance insights and statistics.

## AI Integration

Google Gemini powers the AI assistant.

The assistant receives project statistics and task information through a dynamically generated system prompt.

Conversation history is maintained using conversation IDs, allowing the assistant to retain context across multiple requests.

A mock response mechanism is also available when the Gemini API key is not configured.

## Error Handling

The API handles common errors using appropriate HTTP status codes:

- `400` – Invalid input.
- `401` – Invalid or missing API key.
- `404` – Resource not found.
- `422` – Request validation error.
- `503` – External data source unavailable.

## Author

**Neama Ben Hamo**

Python Final Project

Task Management API with Data Analytics and AI Integration.
