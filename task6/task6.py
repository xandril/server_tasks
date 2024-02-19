import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List

logging.basicConfig(level=logging.DEBUG)


@dataclass
class Payload:
    data: str


@dataclass
class Address:
    host: str


@dataclass
class Event:
    recipients: List[Address]
    payload: Payload


class Result(Enum):
    Accepted = 1
    Rejected = 2


async def read_data() -> Event:
    recipients = [Address(f'recipient_{i}') for i in range(4)]
    payload = Payload(data="big data")
    logging.info(f'read {payload} from {recipients}')
    return Event(recipients=recipients, payload=payload)


async def send_data(dest: Address, payload: Payload) -> Result:
    try:
        logging.info(f"send payload: {payload} to {dest}")
        await asyncio.sleep(1)
        return Result.Accepted
    except Exception as e:
        logging.error(f"Error sending data to {dest}: {e}")
        return Result.Rejected


async def perform_operation() -> None:
    while True:
        try:
            event = await read_data()
            futures = [send_data(recipient, event.payload) for recipient in event.recipients]
            res = await asyncio.gather(*futures)  # send_data гарантированно не падает с ошибкой
            logging.info(f'statuses: {res}')

        except Exception as e:
            logging.error(f"Error processing data: {e}")



if __name__ == "__main__":
    asyncio.run(perform_operation())
