from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Generator

from prometheus_client.metrics_core import GaugeMetricFamily
from sqlalchemy import func

from app.database import PaymentCard, PaymentCardAccount, load_session, UserClientApplication, User, \
    UbiquitiSchemeAccountEntry, UbiquitiPaymentCardAccountEntry, UbiquitiServiceConsent, SchemeAccount
from settings import PAYMENT_CARD_STATUS_MAP, PAYMENT_CARD_SYSTEM_MAP

if TYPE_CHECKING:
    from prometheus_client import Metric
    from sqlalchemy.orm import Session


def collect_payment_card_status(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    payment_card_status_metric = GaugeMetricFamily(
        name=prefix + "payment_card_status_total",
        documentation="payment card total current statuses by issuer",
        labels=("status", "provider"),
    )
    pcard_status_data = (
        session.query(
            PaymentCard.system,
            PaymentCardAccount.status,
            func.count(PaymentCardAccount.id),
        )
        .join(PaymentCard)
        .filter(PaymentCardAccount.is_deleted == False)  # noqa
        .group_by(PaymentCard.id, PaymentCardAccount.status)
        .all()
    )
    for system, status, count in pcard_status_data:
        payment_card_status_metric.add_metric(
            labels=(
                PAYMENT_CARD_STATUS_MAP.get(status, "unknown"),
                PAYMENT_CARD_SYSTEM_MAP.get(system, "unknown"),
            ),
            value=count,
            timestamp=timestamp,
        )
    return payment_card_status_metric


def collect_payment_card_pending_overdue(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    payment_card_pending_overdue_metric = GaugeMetricFamily(
        name=prefix + "payment_card_pending_overdue_total",
        documentation="total payment cards in a pending state for more than 24 hours.",
        labels=("provider",)
    )
    payment_card_pending_overdue_data = (
        session.query(
            PaymentCard.system,
            func.count(PaymentCardAccount.id),
        )
        .group_by(
            PaymentCard.system,
            PaymentCardAccount.status
        )
        .join(PaymentCard)
        .filter(
            PaymentCardAccount.is_deleted == False,  # noqa
            PaymentCardAccount.status == 0,
            PaymentCardAccount.updated < now - timedelta(hours=24),
        )
        .all()
    )
    for system, count in payment_card_pending_overdue_data:
        payment_card_pending_overdue_metric.add_metric(
            labels=(PAYMENT_CARD_SYSTEM_MAP.get(system, "unknown"),),
            value=count,
            timestamp=timestamp,
        )
    return payment_card_pending_overdue_metric


def collect_user_count_by_client_app(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "users_total",
        documentation="total users registered in bink per client application",
        labels=("client_app",)
    )
    metric_data = (
        session.query(
            UserClientApplication.name,
            func.count(User.id),
        )
        .group_by(
            UserClientApplication.name
        )
        .join(UbiquitiServiceConsent)
        .join(UserClientApplication)
        .filter(
            User.date_joined < func.current_date()
        )
        .all()
    )

    for client_app, count in metric_data:
        metric_desc.add_metric(
            labels=(client_app,),
            value=count,
            timestamp=timestamp,
        )
    return metric_desc


def collect_payment_card_count_by_client_app(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "payment_cards_total",
        documentation="total payment cards registered in bink per client application",
        labels=("client_app",)
    )
    metric_data = (
        session.query(
            UserClientApplication.name,
            func.count(User.id),
        )
        .group_by(
            UserClientApplication.name
        )
        .join(UbiquitiPaymentCardAccountEntry)
        .join(PaymentCardAccount)
        .join(UserClientApplication)
        .filter(
            PaymentCardAccount.is_deleted == False,  # noqa: E712
            PaymentCardAccount.created < func.current_date()
        )
        .all()
    )

    for client_app, count in metric_data:
        metric_desc.add_metric(
            labels=(client_app,),
            value=count,
            timestamp=timestamp,
        )
    return metric_desc


def collect_membership_card_count_by_client_app(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "membership_cards_total",
        documentation="total membership cards registered in bink per client application",
        labels=("client_app",)
    )
    metric_data = (
        session.query(
            UserClientApplication.name,
            func.count(User.id),
        )
        .group_by(
            UserClientApplication.name
        )
        .join(UbiquitiSchemeAccountEntry)
        .join(SchemeAccount)
        .join(UserClientApplication)
        .filter(
            SchemeAccount.is_deleted == False,  # noqa: E712
            SchemeAccount.status == 1,
            SchemeAccount.created < func.current_date()
        )
        .all()
    )

    for client_app, count in metric_data:
        metric_desc.add_metric(
            labels=(client_app,),
            value=count,
            timestamp=timestamp,
        )
    return metric_desc


class CustomCollector(object):
    prefix = "hermes_current_"

    def collect(self) -> Generator:
        now = datetime.now()
        session = load_session()

        # add here custom metrics collection
        yield collect_payment_card_status(self.prefix, session, now)
        yield collect_payment_card_pending_overdue(self.prefix, session, now)
        yield collect_user_count_by_client_app(self.prefix, session, now)
        yield collect_payment_card_count_by_client_app(self.prefix, session, now)
        yield collect_membership_card_count_by_client_app(self.prefix, session, now)

        session.close()
