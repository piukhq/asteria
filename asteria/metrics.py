from collections.abc import Generator
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from loguru import logger
from prometheus_client.metrics_core import GaugeMetricFamily
from prometheus_client.registry import Collector
from sqlalchemy import func

from asteria.database import (
    PaymentCard,
    PaymentCardAccount,
    SchemeAccount,
    UbiquityPaymentCardAccountEntry,
    UbiquitySchemeAccountEntry,
    UbiquityServiceConsent,
    User,
    UserClientApplication,
    VopActivation,
    load_session,
)
from asteria.settings import PAYMENT_CARD_STATUS_MAP, PAYMENT_CARD_SYSTEM_MAP, VOP_ACTIVATION_MAP

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
        labels=("provider",),
    )
    payment_card_pending_overdue_data = (
        session.query(
            PaymentCard.system,
            func.count(PaymentCardAccount.id),
        )
        .group_by(PaymentCard.system, PaymentCardAccount.status)
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
        labels=("client_app",),
    )
    metric_data = (
        session.query(
            UserClientApplication.name,
            func.count(User.id),
        )
        .group_by(UserClientApplication.name)
        .join(UbiquityServiceConsent)
        .join(UserClientApplication)
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
        labels=("client_app",),
    )
    metric_data = (
        session.query(
            UserClientApplication.name,
            func.count(User.id),
        )
        .group_by(UserClientApplication.name)
        .join(UbiquityPaymentCardAccountEntry)
        .join(PaymentCardAccount)
        .join(UserClientApplication)
        .filter(
            PaymentCardAccount.is_deleted == False,  # noqa: E712
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
        labels=("client_app",),
    )
    metric_data = (
        session.query(
            UserClientApplication.name,
            func.count(User.id),
        )
        .group_by(UserClientApplication.name)
        .join(UbiquitySchemeAccountEntry)
        .join(SchemeAccount)
        .join(UserClientApplication)
        .filter(
            SchemeAccount.is_deleted == False,  # noqa: E712
            UbiquitySchemeAccountEntry.link_status == 1,
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


def collect_vop_activations(prefix: str, session: "Session", now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "vop_activation_status_total",
        documentation="total count of vop activation status",
        labels=("status",),
    )
    metric_data = session.query(VopActivation.status, func.count(VopActivation.id)).group_by(VopActivation.status).all()

    for status, count in metric_data:
        metric_desc.add_metric(
            labels=(VOP_ACTIVATION_MAP.get(status, "unknown"),),
            value=count,
            timestamp=timestamp,
        )
    return metric_desc


class CustomCollector(Collector):
    prefix = "hermes_current_"

    def collect(self) -> Generator:
        now = datetime.now()  # noqa: DTZ005 we want the local time here
        with load_session() as session:
            # add here custom metrics collection
            yield collect_payment_card_status(self.prefix, session, now)
            yield collect_payment_card_pending_overdue(self.prefix, session, now)
            yield collect_user_count_by_client_app(self.prefix, session, now)
            yield collect_payment_card_count_by_client_app(self.prefix, session, now)
            yield collect_membership_card_count_by_client_app(self.prefix, session, now)
            yield collect_vop_activations(self.prefix, session, now)

        logger.debug("Metrics collected successfully.")