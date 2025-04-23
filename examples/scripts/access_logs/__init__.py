"""
Supports read queries on the acccess logs table
"""

from datetime import datetime, timedelta
from typing import Any, TypedDict

from clickhouse_driver import Client

from script_runner import read, get_function_context

class AccessLogsConfig(TypedDict):
    host: str
    port: int
    database: str
    table_name: str


def get_date_n_days_ago(n: int) -> str:
    # Get today's date
    today = datetime.today()

    # Subtract `n` days from today's date
    n_days_ago = today - timedelta(days=n)

    # Format the result as 'YYYY-MM-DD'
    return n_days_ago.strftime("%Y-%m-%d")


@read
def response_code_by_time(
    request_uri_path: str = "/api/0/organizations/sentry/events/",
    status_code: str = "400",
    num_days: str = "7",
):
    """
    Returns the breakdown of response codes by time.
    `status_code` must be a valid integer
    """

    config: AccessLogsConfig = get_function_context().group_config

    status_code_int = int(status_code)
    num_days_int = int(num_days)

    client = Client(host=config["host"], port=config["port"])

    today = datetime.today()
    n_days_ago = today - timedelta(days=num_days_int)
    start = n_days_ago.strftime("%Y-%m-%d")

    query = f"""
    select
        _date,  count(*) AS c
    FROM {config["database"]}.{config["table_name"]}
    WHERE (_date > '{start}') AND (status = {status_code_int})
    AND (request_uri_path = '{request_uri_path}')
    GROUP BY
        _date
    ORDER BY
        _date
    """

    resp = client.execute(query)

    return [
        {
            "date": d.strftime("%Y-%m-%d"),
            "count": count,
        }
        for (d, count) in resp
    ]


__all__ = ["response_code_by_time"]
