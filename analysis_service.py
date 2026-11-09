
import pandas as pd
import numpy as np

from data_service import (
    get_users_dataframe,
    get_todos_dataframe
)


def get_combined_data():
    users = get_users_dataframe()
    todos = get_todos_dataframe()

    if users is None or todos is None:
        return None

    combined = pd.merge(
        todos,
        users,
        on="user_id",
        how="left"
    )

    return combined


def get_user_statistics():
    combined = get_combined_data()

    if combined is None:
        return None

    statistics = combined.groupby(
        ["user_id", "name", "city"]
    ).agg(
        total_tasks=("id", "count"),
        completed_tasks=("completed", "sum")
    ).reset_index()

    statistics["completion_percentage"] = (
        statistics["completed_tasks"]
        / statistics["total_tasks"] * 100
    ).round(2)

    return statistics


def get_performance_summary():
    statistics = get_user_statistics()

    if statistics is None or statistics.empty:
        return None

    percentages = statistics["completion_percentage"]

    return {
        "average": round(float(np.mean(percentages)), 2),
        "std_deviation": round(float(np.std(percentages)), 2),
        "median": round(float(np.median(percentages)), 2)
    }


def get_low_performers():
    statistics = get_user_statistics()

    if statistics is None or statistics.empty:
        return None

    average = statistics["completion_percentage"].mean()

    low_performers = statistics[
        statistics["completion_percentage"] < average
    ]

    return low_performers


def get_completion_pivot():
    combined = get_combined_data()

    if combined is None:
        return None

    pivot = pd.pivot_table(
        combined,
        index="city",
        columns="completed",
        values="id",
        aggfunc="count",
        fill_value=0
    )

    pivot = pivot.rename(columns={
        False: "pending",
        True: "completed"
    })

    return pivot.reset_index()
