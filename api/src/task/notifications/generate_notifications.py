import logging
import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from sqlalchemy import select, update

import src.adapters.db as db
import src.adapters.db.flask_db as flask_db
from src.db.models.opportunity_models import OpportunityChangeAudit
from src.db.models.user_models import UserNotificationLog, UserSavedOpportunity
from src.task.ecs_background_task import ecs_background_task
from src.task.task import Task
from src.task.task_blueprint import task_blueprint
from src.util import datetime_util

logger = logging.getLogger(__name__)


@task_blueprint.cli.command(
    "generate-notifications", help="Send notifications for opportunity and search changes"
)
@ecs_background_task("generate-notifications")
@flask_db.with_db_session()
def run_notification_task(db_session: db.Session) -> None:
    """Run the daily notification task"""
    task = NotificationTask(db_session)
    task.run()


@dataclass
class NotificationContainer:
    """Container for collecting notifications for a single user"""

    saved_opportunities: list[UserSavedOpportunity] = field(default_factory=list)
    # TODO: Change from str to something else
    updated_searches: list[str] = field(default_factory=list)


class NotificationTask(Task):
    """Task that runs daily to collect and send notifications to users about changes"""

    # TODO: Confirm with team if we want to use these metrics
    class Metrics(StrEnum):
        USERS_NOTIFIED = "users_notified"
        OPPORTUNITIES_TRACKED = "opportunities_tracked"
        SEARCHES_TRACKED = "searches_tracked"
        NOTIFICATIONS_SENT = "notifications_sent"

    def __init__(self, db_session: db.Session) -> None:
        super().__init__(db_session)
        self.user_notification_map: dict[uuid.UUID, NotificationContainer] = {}

    def run_task(self) -> None:
        """Main task logic to collect and send notifications"""
        self._collect_opportunity_notifications()
        self._collect_search_notifications()
        self._send_notifications()

    def _collect_opportunity_notifications(self) -> None:
        """Collect notifications for changed opportunities that users are tracking"""
        stmt = (
            select(UserSavedOpportunity)
            .join(
                OpportunityChangeAudit,
                OpportunityChangeAudit.opportunity_id == UserSavedOpportunity.opportunity_id,
            )
            .where(OpportunityChangeAudit.updated_at > UserSavedOpportunity.last_notified_at)
            .distinct()
        )

        results = self.db_session.execute(stmt)

        for row in results.scalars():
            user_id = row.user_id
            if user_id not in self.user_notification_map:
                self.user_notification_map[user_id] = NotificationContainer()
            self.user_notification_map[user_id].saved_opportunities.append(row)

        logger.info(
            "Collected opportunity notifications",
            extra={
                "user_count": len(self.user_notification_map),
                "total_notifications": sum(
                    len(container.saved_opportunities)
                    for container in self.user_notification_map.values()
                ),
            },
        )

    def _collect_search_notifications(self) -> None:
        """Collect notifications for changed saved searches
        To be implemented in future ticket
        """
        logger.info("Search notification collection not yet implemented")
        pass

    def _send_notifications(self) -> None:
        """Send collected notifications to users"""
        for user_id, container in self.user_notification_map.items():
            if not container.saved_opportunities and not container.updated_searches:
                continue

            # TODO: Implement actual notification sending in future ticket
            logger.info(
                "Would send notification to user",
                extra={
                    "user_id": user_id,
                    "opportunity_count": len(container.saved_opportunities),
                    "search_count": len(container.updated_searches),
                },
            )

            # Create notification log entry
            # TODO: Use enum for notification reason?
            notification_log = UserNotificationLog(
                user_id=user_id,
                notification_reason="opportunity_updates",
                notification_sent=True,
            )
            self.db_session.add(notification_log)

            # Update last_notified_at for all opportunities we just notified about
            opportunity_ids = [
                saved_opp.opportunity_id for saved_opp in container.saved_opportunities
            ]
            self.db_session.execute(
                update(UserSavedOpportunity)
                .where(
                    UserSavedOpportunity.user_id == user_id,
                    UserSavedOpportunity.opportunity_id.in_(opportunity_ids),
                )
                .values(last_notified_at=datetime_util.utcnow())
            )

            self.increment(self.Metrics.OPPORTUNITIES_TRACKED, len(container.saved_opportunities))
            self.increment(self.Metrics.SEARCHES_TRACKED, len(container.updated_searches))
            self.increment(self.Metrics.NOTIFICATIONS_SENT)
            self.increment(self.Metrics.USERS_NOTIFIED)
