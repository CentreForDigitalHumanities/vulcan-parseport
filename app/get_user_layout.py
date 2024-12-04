from flask import Request
from flask_sqlalchemy import SQLAlchemy
from vulcan.file_loader import BasicLayout
from db.models import ParseResult
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from logger import log


def get_user_layout(request: Request, db: SQLAlchemy) -> BasicLayout | None:
    """
    Get the layout for the user based on the 'id' query parameter.

    If the user has a parse output stored in the database, it will be turned
    into a Layout object and returned.

    If there is no 'id' provided, if the provided 'id' is not found in the
    database, or if multiple layouts are found for the user, None will be 
    returned.
    """
    layout_id = request.args.get("id")

    if layout_id is None:
        log.info("No layout ID provided.")
        return None

    try:
        parse_result = db.session.query(ParseResult).filter_by(user_id=layout_id).one()

        # layout = create_layout_from_parse_result(parse_result)
        layout = None

        return layout
    except NoResultFound:
        log.error(
            f"No layout found with ID {layout_id}."
        )
        return None
    except MultipleResultsFound:
        log.error(
            f"Multiple layouts found with ID {layout_id}."
        )
        return None
