
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Generator

from prometheus_client.metrics_core import GaugeMetricFamily
from settings import PAYMENT_CARD_STATUS_MAP
from sqlalchemy import func

from app.database import PaymentCard, PaymentCardAccount, load_session

if TYPE_CHECKING:
    from prometheus_client import Metric
    from sqlalchemy.orm import Session


def collect_payment_card_status(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    payment_card_status_metric = GaugeMetricFamily(
        name=prefix + "payment_card_status_total",
        documentation="payment card total current statuses by issuer",
        labels=("status", "issuer"),
    )
    pcard_status_data = (
        session.query(
            PaymentCard.slug,
            PaymentCardAccount.status,
            func.count(PaymentCardAccount.id),
        )
        .join(PaymentCard)
        .filter(PaymentCardAccount.is_deleted == False)  # noqa
        .group_by(PaymentCard.id, PaymentCardAccount.status)
        .all()
    )
    for issuer, status, count in pcard_status_data:
        payment_card_status_metric.add_metric(
            labels=[PAYMENT_CARD_STATUS_MAP.get(status, "unknwon"), issuer],
            value=count,
            timestamp=timestamp,
        )
    return payment_card_status_metric


def collect_payment_card_pending_overdue(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    payment_card_pending_overdue_metric = GaugeMetricFamily(
        name=prefix + "payment_card_pending_overdue_total",
        documentation="total payment cards in a pending state for more than 24 hours.",
    )
    payment_card_pending_overdue_data = (
        session.query(
            func.count(PaymentCardAccount.id),
        )
        .group_by(PaymentCardAccount.status)
        .filter(
            PaymentCardAccount.is_deleted == False, # noqa
            PaymentCardAccount.status == 0,
            PaymentCardAccount.created < now - timedelta(hours=24),
        )
        .scalar()
    ) or 0
    payment_card_pending_overdue_metric.add_metric(
        labels=[],
        value=payment_card_pending_overdue_data,
        timestamp=timestamp,
    )
    return payment_card_pending_overdue_metric


class CustomCollector(object):
    prefix = "hermes_current_"

    def collect(self) -> Generator:
        now = datetime.now()
        session = load_session()

        # add here custom metrics collection
        yield collect_payment_card_status(self.prefix, session, now)
        yield collect_payment_card_pending_overdue(self.prefix, session, now)

        session.close()
