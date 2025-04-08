from datetime import timedelta, datetime

from flask_sqlalchemy import SQLAlchemy

from db.models import StoredLayout
from logger import log

# Number of days before a layout expires.
EXPIRATION_TIME_DAYS = 90


def update_timestamp(db: SQLAlchemy, stored_layout: StoredLayout) -> None:
    """
    Updates the timestamp of a StoredLayout object to the current time.
    """
    log.debug(f"Updating timestamp for layout {stored_layout.id}")

    new_timestamp = datetime.now()

    stored_layout.timestamp = new_timestamp
    log.debug(
        f"Updated timestamp for layout: {stored_layout.id} ({stored_layout.timestamp})"
    )

    db.session.commit()


def remove_old_layouts(db: SQLAlchemy) -> None:
    """
    Removes layouts if they are older than the expiration time.
    """
    log.debug("Removing old layouts")

    oldest_allowed_timestamp = datetime.now() - timedelta(days=EXPIRATION_TIME_DAYS)

    old_layouts = (
        db.session.query(StoredLayout)
        .filter(StoredLayout.timestamp < oldest_allowed_timestamp)
        .all()
    )

    for layout in old_layouts:
        log.debug(f"Deleting layout: {layout.id} ({layout.timestamp})")
        db.session.delete(layout)

    db.session.commit()

    log.debug("Old layouts removed")
