from datetime import timedelta, datetime

from flask_sqlalchemy import SQLAlchemy

from db.models import StoredLayout
from logger import log

# Number of days before a layout expires.
EXPIRATION_TIME_DAYS = 90


def update_timestamp(db: SQLAlchemy, stored_layout: StoredLayout) -> None:
    """
    Updates the timestamp of a StoredLayout object and its associated objects to the current time.
    """
    log.debug("Updating timestamp for layout:", stored_layout.id)

    new_timestamp = datetime.now()

    stored_layout.timestamp = new_timestamp
    log.debug(
        "Updated timestamp for layout:", stored_layout.id, stored_layout.timestamp
    )

    if stored_layout.based_on:
        stored_layout.based_on.timestamp = new_timestamp
        log.debug(
            "Updated timestamp for base layout:",
            stored_layout.id,
            stored_layout.timestamp,
        )

    for derived_layout in stored_layout.derived_layouts:
        derived_layout.timestamp = new_timestamp
        log.debug(
            "Updated timestamp for derived layout:",
            stored_layout.id,
            stored_layout.timestamp,
        )

    db.session.commit()


def remove_old_layouts(db: SQLAlchemy) -> None:
    """
    Removes layouts (and their children) if they are older than the expiration time.
    """
    log.debug("Removing old layouts")

    oldest_allowed_timestamp = datetime.now() - timedelta(days=EXPIRATION_TIME_DAYS)

    old_layouts = (
        db.session.query(StoredLayout)
        .filter(StoredLayout.timestamp < oldest_allowed_timestamp)
        .all()
    )

    # Child layouts are marked for deletion as well.
    for layout in old_layouts:
        children = layout.derived_layouts
        for child in children:
            log.debug("Deleting child layout:", child.id, child.timestamp)
            db.session.delete(child)
        log.debug("Deleting (parent) layout:", layout.id, layout.timestamp)
        db.session.delete(layout)

    db.session.commit()
