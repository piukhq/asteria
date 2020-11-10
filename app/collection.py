from datetime import datetime
from typing import TYPE_CHECKING

from prometheus_client.metrics_core import GaugeMetricFamily
from sqlalchemy import func

from app.database import Issuer, PaymentCardAccount
from settings import PAYMENT_CARD_STATUS_MAP

if TYPE_CHECKING:
    from prometheus_client import Metric
    from sqlalchemy.orm import Session


def collect_payment_card_status(prefix: str, session: "Session") -> "Metric":
    PAYMENT_CARD_STATUS = GaugeMetricFamily(
        name=prefix + "payment_card_status_total",
        documentation="payment card total current statuses by issuer",
        labels=("status", "issuer"),
    )
    now = datetime.now().timestamp()
    pcard_status_data = (
        session.query(
            Issuer.name,
            PaymentCardAccount.status,
            func.count(PaymentCardAccount.id),
        )
        .join(Issuer)
        .filter(PaymentCardAccount.is_deleted == False)  # noqa
        .group_by(Issuer.name, PaymentCardAccount.status)
        .all()
    )
    for issuer, status, count in pcard_status_data:
        PAYMENT_CARD_STATUS.add_metric(
            labels=[PAYMENT_CARD_STATUS_MAP.get(status, "unknwon"), issuer],
            value=count,
            timestamp=now,
        )
    return PAYMENT_CARD_STATUS
