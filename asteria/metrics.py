from collections.abc import Generator
from datetime import datetime
from typing import TYPE_CHECKING

import psycopg
from loguru import logger
from prometheus_client.metrics_core import GaugeMetricFamily
from prometheus_client.registry import Collector

from asteria.settings import PAYMENT_CARD_STATUS_MAP, PAYMENT_CARD_SYSTEM_MAP, VOP_ACTIVATION_MAP, settings

if TYPE_CHECKING:
    from prometheus_client import Metric


def collect_payment_card_status(prefix: str, cursor: psycopg.Cursor, now: datetime) -> "Metric":
    timestamp = now.timestamp()
    payment_card_status_metric = GaugeMetricFamily(
        name=prefix + "payment_card_status_total",
        documentation="payment card total current statuses by issuer",
        labels=("status", "provider"),
    )
    cursor.execute(
        """
        SELECT
            pc.system,
            pca.status,
            COUNT(pca.id)
        FROM
            payment_card_paymentcardaccount pca
        JOIN
            payment_card_paymentcard pc ON pca.payment_card_id = pc.id
        WHERE
            pca.is_deleted is false
        GROUP BY
            pc.system,
            pca.status
        """
    )

    for system, status, count in cursor.fetchall():
        payment_card_status_metric.add_metric(
            labels=(
                PAYMENT_CARD_STATUS_MAP.get(status, "unknown"),
                PAYMENT_CARD_SYSTEM_MAP.get(system, "unknown"),
            ),
            value=count,
            timestamp=timestamp,
        )
    return payment_card_status_metric


def collect_payment_card_pending_overdue(prefix: str, cursor: psycopg.Cursor, now: datetime) -> "Metric":
    timestamp = now.timestamp()
    payment_card_pending_overdue_metric = GaugeMetricFamily(
        name=prefix + "payment_card_pending_overdue_total",
        documentation="total payment cards in a pending state for more than 24 hours.",
        labels=("provider",),
    )
    cursor.execute(
        """
        SELECT
            pc.system,
            COUNT(pca.id)
        FROM
            payment_card_paymentcardaccount pca
        JOIN
            payment_card_paymentcard pc ON pca.payment_card_id = pc.id
        WHERE
            pca.is_deleted is false
            AND pca.status = 0
            AND pca.updated < %s - interval '1 day'
        GROUP BY
            pc.system,
            pca.status
        """,
        [now],
    )

    for system, count in cursor.fetchall():
        payment_card_pending_overdue_metric.add_metric(
            labels=(PAYMENT_CARD_SYSTEM_MAP.get(system, "unknown"),),
            value=count,
            timestamp=timestamp,
        )

    return payment_card_pending_overdue_metric


def collect_user_count_by_client_app(prefix: str, cursor: psycopg.Cursor, now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "users_total",
        documentation="total users registered in bink per client application",
        labels=("client_app",),
    )

    cursor.execute(
        """
        SELECT
            ca.name,
            COUNT(u.id)
        FROM
            "user" u
        JOIN
            user_clientapplication ca ON u.client_id = ca.client_id
        WHERE
            u.is_active is true
        GROUP BY
            ca.name
        """
    )

    for client_app, count in cursor.fetchall():
        metric_desc.add_metric(
            labels=(client_app,),
            value=count,
            timestamp=timestamp,
        )
    return metric_desc


def collect_payment_card_count_by_client_app(prefix: str, cursor: psycopg.Cursor, now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "payment_cards_total",
        documentation="total payment cards registered in bink per client application",
        labels=("client_app",),
    )
    cursor.execute(
        """
        SELECT
            uca.name,
            COUNT(distinct pca.id)
        FROM
            ubiquity_paymentcardaccountentry pcae
        JOIN
            payment_card_paymentcardaccount pca ON pcae.payment_card_account_id = pca.id
        JOIN
            "user" u ON pcae.user_id = u.id
        JOIN
            user_clientapplication uca ON uca.client_id = u.client_id
        WHERE
            pca.is_deleted is false
        GROUP BY
            uca.name
        """
    )

    for client_app, count in cursor.fetchall():
        metric_desc.add_metric(
            labels=(client_app,),
            value=count,
            timestamp=timestamp,
        )

    return metric_desc


def collect_membership_card_count_by_client_app(prefix: str, cursor: psycopg.Cursor, now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "membership_cards_total",
        documentation="total membership cards registered in bink per client application",
        labels=("client_app",),
    )

    cursor.execute(
        """
        SELECT
            ca.name,
            COUNT(distinct sa.id)
        FROM
            ubiquity_schemeaccountentry sae
        JOIN
            scheme_schemeaccount sa ON sae.scheme_account_id = sa.id
        JOIN
            "user" u ON sae.user_id = u.id
        JOIN
            user_clientapplication ca ON ca.client_id = u.client_id
        WHERE
            sa.is_deleted is false
            AND sae.link_status = 1
        GROUP BY
            ca.name;
        """
    )

    for client_app, count in cursor.fetchall():
        metric_desc.add_metric(
            labels=(client_app,),
            value=count,
            timestamp=timestamp,
        )
    return metric_desc


def collect_vop_activations(prefix: str, cursor: psycopg.Cursor, now: datetime) -> "Metric":
    timestamp = now.timestamp()
    metric_desc = GaugeMetricFamily(
        name=prefix + "vop_activation_status_total",
        documentation="total count of vop activation status",
        labels=("status",),
    )
    cursor.execute(
        """
        SELECT
            va.status,
            COUNT(va.id)
        FROM
            ubiquity_vopactivation va
        GROUP BY
            va.status
        """
    )

    for status, count in cursor.fetchall():
        metric_desc.add_metric(
            labels=(VOP_ACTIVATION_MAP.get(status, "unknown"),),
            value=count,
            timestamp=timestamp,
        )

    return metric_desc


class CustomCollector(Collector):
    prefix = "hermes_current_"

    def collect(self) -> Generator:
        now = datetime.now(tz=settings.TZINFO)

        with psycopg.connect(settings.POSTGRES_DSN) as conn, conn.cursor() as cursor:
            # add here custom metrics collection
            yield collect_payment_card_status(self.prefix, cursor, now)
            yield collect_payment_card_pending_overdue(self.prefix, cursor, now)
            yield collect_user_count_by_client_app(self.prefix, cursor, now)
            yield collect_payment_card_count_by_client_app(self.prefix, cursor, now)
            yield collect_membership_card_count_by_client_app(self.prefix, cursor, now)
            yield collect_vop_activations(self.prefix, cursor, now)

        logger.debug("Metrics collected successfully.")
