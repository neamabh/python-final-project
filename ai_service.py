
import os
import csv
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from google import genai

from task_service import get_all_tasks
from analysis_service import (
    get_user_statistics,
    get_completion_pivot,
    get_performance_summary
)

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-3.5-flash-lite"

client = genai.Client(api_key=API_KEY) if API_KEY else None

LOG_FILE = Path("ai_logs.csv")

conversation_history = {}


# PROJECT SUMMARY

def get_project_summary():
    tasks = get_all_tasks()
    statistics = get_user_statistics()
    cities = get_completion_pivot()
    performance = get_performance_summary()

    average_completion = 0
    median_completion = 0
    top_performers = []
    strongest_city = "Not available"

    if performance is not None:
        average_completion = performance["average"]
        median_completion = performance["median"]

    if statistics is not None and not statistics.empty:
        top_performers = (
            statistics
            .sort_values(
                by="completion_percentage",
                ascending=False
            )
            .head(3)[["name", "completion_percentage"]]
            .to_dict(orient="records")
        )

    if cities is not None and not cities.empty:
        cities = cities.copy()

        cities["total"] = (
            cities["completed"] + cities["pending"]
        )

        cities["completion_percentage"] = (
            cities["completed"]
            / cities["total"].replace(0, 1)
            * 100
        )

        strongest_city = cities.sort_values(
            by="completion_percentage",
            ascending=False
        ).iloc[0]["city"]

    return {
        "total_tasks": len(tasks),
        "average_completion": average_completion,
        "median_completion": median_completion,
        "top_performers": top_performers,
        "strongest_city": strongest_city
    }


# AI LOGS

def save_ai_log(
    conversation_id,
    prompt_length,
    response_length,
    status
):
    fields = [
        "conversation_id",
        "timestamp",
        "prompt_length",
        "response_length",
        "status"
    ]

    file_exists = LOG_FILE.exists()

    # Replace an old log format automatically
    if file_exists and LOG_FILE.stat().st_size > 0:
        with open(
            LOG_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            old_fields = next(csv.reader(file), [])

        if old_fields != fields:
            with open(
                LOG_FILE,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=fields
                )
                writer.writeheader()

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        if LOG_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerow({
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_length": prompt_length,
            "response_length": response_length,
            "status": status
        })


# MOCK RESPONSE

def get_mock_response(prompt):
    summary = get_project_summary()

    return (
        "Mock AI Response - Gemini API key is not configured.\n"
        f"Your question was: {prompt}\n"
        f"Total tasks: {summary['total_tasks']}\n"
        f"Average completion: {summary['average_completion']}%\n"
        f"Median completion: {summary['median_completion']}%"
    )


# ASK AI

def ask_ai(prompt: str, conversation_id: str):

    history = conversation_history.setdefault(
        conversation_id, []
    )

    answer = ""
    status = "error"

    try:
        if not client:
            answer = get_mock_response(prompt)
            status = "mock"

        else:
            project_summary = get_project_summary()
            tasks = get_all_tasks()

            system_prompt = f"""
            You are an intelligent task management assistant.

            Project statistics:
            {project_summary}

            Tasks:
            {tasks}

            Instructions:
            - Answer clearly and accurately.
            - Use the project data when relevant.
            - Never invent information.
            - Use average and median completion statistics.
            - Identify the top three performers when relevant.
            """

            previous_conversation = "\n".join(
                [
                    f"User: {item['prompt']}\n"
                    f"Assistant: {item['answer']}"
                    for item in history
                ]
            )

            full_prompt = f"""
            {system_prompt}

            Previous conversation:
            {previous_conversation}

            Current question:
            {prompt}
            """

            result = client.models.generate_content(
                model=MODEL,
                contents=full_prompt
            )

            answer = result.text or "No answer was generated."
            status = "success"

    except Exception as error:
        print(f"AI error: {error}")

        answer = (
            "AI service is currently unavailable. "
            "Please try again later."
        )

        status = "error"

    finally:
        history.append({
            "prompt": prompt,
            "answer": answer
        })

        try:
            save_ai_log(
                conversation_id=conversation_id,
                prompt_length=len(prompt),
                response_length=len(answer),
                status=status
            )

        except Exception as log_error:
            print(f"Could not save AI log: {log_error}")

    return answer
