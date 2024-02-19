import asyncio
import functools
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import aiohttp

logging.basicConfig(level=logging.INFO)


class Response(Enum):
    Success = "Success"
    RetryAfter = "RetryAfter"
    Failure = "Failure"


class ApplicationStatusResponse(Enum):
    Success = "Success"
    Failure = "Failure"


@dataclass
class ApplicationResponse:
    application_id: str
    status: ApplicationStatusResponse
    description: str
    last_request_time: datetime


def retry(func, retry_count: int):
    assert retry_count >= 0

    @functools.wraps(func)
    def persistent_func(*args, **kwargs):
        for i in range(retry_count):
            res = func(*args, **kwargs)
            if res != Response.RetryAfter:
                return res
        return func(*args, **kwargs)

    return persistent_func


async def get_application_status1(identifier: str, server_url: str) -> Response:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(server_url) as response:
                logging.info(f'response: {response} with identifier {identifier}')
                if response.status == 200:
                    return Response.Success
                elif response.status == 429:
                    return Response.RetryAfter
                else:
                    return Response.Failure
    except Exception as e:
        logging.error(f"Error: {e}")
        return Response.Failure


async def get_application_status2(identifier: str, server_url: str) -> Response:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(server_url) as response:
                logging.info(f'response: {response} with identifier {identifier}')
                if response.status == 200:
                    return Response.Success
                elif response.status == 429:
                    return Response.RetryAfter
                else:
                    return Response.Failure
    except Exception as e:
        logging.error(f"Error: {e}")
        return Response.Failure


async def perform_operation(application_id: str, server1_url: str, server2_url: str) -> ApplicationResponse:
    future1 = retry(get_application_status1, 3)(application_id, server1_url)
    future2 = retry(get_application_status2, 3)(application_id, server2_url)
    result1, result2 = await asyncio.gather(future1, future2)
    status = ApplicationStatusResponse.Success if result1 == Response.Success and result2 == Response.Success \
        else ApplicationStatusResponse.Failure
    description = f"Status 1: {result1}, Status 2: {result2}"
    last_request_time = datetime.now()

    return ApplicationResponse(application_id, status, description, last_request_time)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        perform_operation(server1_url='http://127.0.0.1:8080/get_char',
                          server2_url='http://127.0.0.1:4080/get_char',
                          application_id=str(uuid.uuid4())))
    print(f"Application ID: {result.application_id}")
    print(f"Status: {result.status}")
    print(f"Description: {result.description}")
    print(f"Last Request Time: {result.last_request_time}")
