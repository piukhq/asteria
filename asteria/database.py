from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import clear_mappers, mapper, sessionmaker
from sqlalchemy.pool import NullPool

from asteria.settings import POSTGRES_DSN

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


engine = create_engine(POSTGRES_DSN, poolclass=NullPool, echo=False)
SessionMaker = sessionmaker(bind=engine)


# These models are containers for the metadata of the corresponding table in the DB and will be filled automatically.
@dataclass
class PaymentCardAccount:
    id: int
    status: int
    is_deleted: bool
    updated: datetime
    created: datetime


@dataclass
class PaymentCard:
    id: int
    system: str


@dataclass
class User:
    id: int
    date_joined: datetime


@dataclass
class UserClientApplication:
    client_id: int
    name: str


@dataclass
class SchemeAccount:
    id: int
    is_deleted: bool
    created: datetime


@dataclass
class UbiquityServiceConsent:
    user_id: int


@dataclass
class UbiquityPaymentCardAccountEntry:
    id: int
    user_id: int


@dataclass
class UbiquitySchemeAccountEntry:
    id: int
    link_status: int


@dataclass
class VopActivation:
    id: int
    status: int


@contextmanager
def load_session() -> "Generator[Session, None, None]":
    clear_mappers()
    metadata = MetaData(engine)

    # map container class to relative table in the hermes database
    mapper(PaymentCardAccount, Table("payment_card_paymentcardaccount", metadata, autoload=True))
    mapper(PaymentCard, Table("payment_card_paymentcard", metadata, autoload=True))
    mapper(User, Table("user", metadata, autoload=True))
    mapper(UserClientApplication, Table("user_clientapplication", metadata, autoload=True))
    mapper(UbiquityServiceConsent, Table("ubiquity_serviceconsent", metadata, autoload=True))
    mapper(UbiquityPaymentCardAccountEntry, Table("ubiquity_paymentcardaccountentry", metadata, autoload=True))
    mapper(UbiquitySchemeAccountEntry, Table("ubiquity_schemeaccountentry", metadata, autoload=True))
    mapper(SchemeAccount, Table("scheme_schemeaccount", metadata, autoload=True))
    mapper(VopActivation, Table("ubiquity_vopactivation", metadata, autoload=True))

    with SessionMaker() as db_session:
        yield db_session
