
from datetime import datetime
from typing import TYPE_CHECKING, Generator

from prometheus_client.metrics_core import GaugeMetricFamily
from settings import PAYMENT_CARD_STATUS_MAP
from sqlalchemy import func

from app.database import PaymentCard, PaymentCardAccount, load_session

if TYPE_CHECKING:
    from prometheus_client import Metric
    from sqlalchemy.orm import Session


def collect_payment_card_status(prefix: str, session: "Session") -> "Metric":
    payment_card_status_metric = GaugeMetricFamily(
        name=prefix + "payment_card_status_total",
        documentation="payment card total current statuses by issuer",
        labels=("status", "issuer"),
    )
    now = datetime.now().timestamp()
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
            timestamp=now,
        )
    return payment_card_status_metric


class CustomCollector(object):
    def __init__(self) -> None:
        self.prefix = "hermes_current_"

    def collect(self) -> Generator:
        session = load_session()

        # add here custom metrics collection
        yield collect_payment_card_status(self.prefix, session)

        session.close()
