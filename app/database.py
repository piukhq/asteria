from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import clear_mappers, mapper, sessionmaker

from settings import POSTGRES_DSN

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


# These models are containers for the metadata of the corresponding table in the DB and will be filled automatically.
@dataclass
class PaymentCardAccount(object):
    id: int
    status: int
    is_deleted: bool


@dataclass
class Issuer(object):
    id: int
    name: str


def load_session() -> "Session":
    engine = create_engine(POSTGRES_DSN, echo=False)
    metadata = MetaData(engine)
    clear_mappers()

    # map container class to relative table in the hermes database
    mapper(PaymentCardAccount, Table("payment_card_paymentcardaccount", metadata, autoload=True))
    mapper(Issuer, Table("payment_card_issuer", metadata, autoload=True))

    session = sessionmaker(bind=engine)
    return session()