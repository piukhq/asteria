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
    created: datetime


@dataclass
class PaymentCard(object):
    id: int
    system: str


@dataclass
class User(object):
    id: int
    date_joined: datetime


@dataclass
class UserClientApplication(object):
    client_id: int
    name: str


@dataclass
class SchemeAccount(object):
    id: int
    is_deleted: bool
    created: datetime
    status: int


@dataclass
class UbiquitiServiceConsent(object):
    user_id: int


@dataclass
class UbiquitiPaymentCardAccountEntry(object):
    id: int
    user_id: int


@dataclass
class UbiquitiSchemeAccountEntry(object):
    id: int


@dataclass
class VopActivation(object):
    id: int
    status = int


def load_session() -> "Session":
    clear_mappers()
    metadata = MetaData(engine)

    # map container class to relative table in the hermes database
    mapper(PaymentCardAccount, Table("payment_card_paymentcardaccount", metadata, autoload=True))
    mapper(PaymentCard, Table("payment_card_paymentcard", metadata, autoload=True))
    mapper(User, Table("user", metadata, autoload=True))
    mapper(UserClientApplication, Table("user_clientapplication", metadata, autoload=True))
    mapper(UbiquitiServiceConsent, Table("ubiquity_serviceconsent", metadata, autoload=True))
    mapper(UbiquitiPaymentCardAccountEntry, Table("ubiquity_paymentcardaccountentry", metadata, autoload=True))
    mapper(UbiquitiSchemeAccountEntry, Table("ubiquity_schemeaccountentry", metadata, autoload=True))
    mapper(SchemeAccount, Table("scheme_schemeaccount", metadata, autoload=True))
    mapper(VopActivation, Table("ubiquity_vopactivation", metadata, autoload=True))

    return SessionMaker()
