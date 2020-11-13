from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import clear_mappers, mapper, sessionmaker
from sqlalchemy.pool import NullPool

from settings import POSTGRES_DSN

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


engine = create_engine(
    POSTGRES_DSN,
    poolclass=NullPool,
    echo=False,
)
SessionMaker = sessionmaker(bind=engine)

# These models are containers for the metadata of the corresponding table in the DB and will be filled automatically.
@dataclass
class PaymentCardAccount(object):
    id: int
    status: int
    is_deleted: bool
    updated: datetime


@dataclass
class PaymentCard(object):
    id: int
    system: str


def load_session() -> "Session":
    clear_mappers()
    metadata = MetaData(engine)

    # map container class to relative table in the hermes database
    mapper(PaymentCardAccount, Table("payment_card_paymentcardaccount", metadata, autoload=True))
    mapper(PaymentCard, Table("payment_card_paymentcard", metadata, autoload=True))

    return SessionMaker()
