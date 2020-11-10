from typing import Generator

from app.collection import collect_payment_card_status
from app.database import load_session


class CustomCollector(object):
    def __init__(self) -> None:
        self.prefix = "hermes_current_"

    def collect(self) -> Generator:
        session = load_session()

        # add here custom metrics collection
        yield collect_payment_card_status(self.prefix, session)

        session.close()
