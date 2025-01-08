import pickle

from flask import Request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from vulcan.file_loader import BasicLayout

from db.models import StoredLayout
from logger import log
from utils.timestamps import update_timestamp


def get_stored_layout(request: Request, db: SQLAlchemy) -> StoredLayout | None:
    """
    Get the StoredLayout object for the user based on the 'id' query parameter.

    If there is no 'id' provided, if the provided 'id' is not found in the
    database, or if multiple layouts are found for the user, None will be
    returned.

    Everytime we access a stored layout, we update its timestamp.
    """
    parse_id = request.args.get("id")

    if parse_id is None or parse_id == "":
        log.info("No layout ID provided.")
        return None

    layout = None
    try:
        layout = db.session.query(StoredLayout).filter_by(parse_id=parse_id).one()
    except NoResultFound:
        log.error(f"No layout found with ID {parse_id}.")
    except MultipleResultsFound:
        log.error(f"Multiple layouts found with ID {parse_id}.")

    update_timestamp(db, layout)
    return layout


def unpack_layout(layout_object: StoredLayout) -> BasicLayout | None:
    """
    Unpickles the layout data from a StoredLayout DB object.
    """
    pickled_layout = layout_object.layout
    try:
        layout = pickle.loads(pickled_layout)
    except pickle.UnpicklingError:
        log.error(
            f"An error occurred while unpickling the layout for ID {layout_object.parse_id}."
        )
        return None
    return layout


def get_and_unpack_layout(request: Request, db: SQLAlchemy) -> BasicLayout | None:
    """
    Convenience method that combines get_stored_layout and unpack_layout.
    """
    stored_layout = get_stored_layout(request, db)
    if stored_layout is None:
        return None
    return unpack_layout(stored_layout)
