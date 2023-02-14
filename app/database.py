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


@dataclass
class UbiquityServiceConsent(object):
    user_id: int


@dataclass
class UbiquityPaymentCardAccountEntry(object):
    id: int
    user_id: int


@dataclass
class UbiquitySchemeAccountEntry(object):
    id: int
    link_status: int


@dataclass
class VopActivation(object):
    id: int
    status: int


def load_session() -> "Session":
    clear_mappers()
    metadata = MetaData(engine)

    # map container class to relative table in the hermes database
    mapper(PaymentCardAccount, Table("payment_card_paymentcardaccount", metadata))
    mapper(PaymentCard, Table("payment_card_paymentcard", metadata))
    mapper(User, Table("user", metadata))
    mapper(UserClientApplication, Table("user_clientapplication", metadata))
    mapper(UbiquityServiceConsent, Table("ubiquity_serviceconsent", metadata))
    mapper(UbiquityPaymentCardAccountEntry, Table("ubiquity_paymentcardaccountentry", metadata))
    mapper(UbiquitySchemeAccountEntry, Table("ubiquity_schemeaccountentry", metadata))
    mapper(SchemeAccount, Table("scheme_schemeaccount", metadata))
    mapper(VopActivation, Table("ubiquity_vopactivation", metadata))

    return SessionMaker()
