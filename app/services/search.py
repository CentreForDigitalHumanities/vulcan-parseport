import pickle
from datetime import datetime

from flask import Request
from flask_sqlalchemy import SQLAlchemy

from vulcan.file_loader import BasicLayout
from vulcan.search.search import perform_search_on_layout, SearchFilter

from db.models import StoredLayout
from logger import log
from services.server_methods import get_search_filters_from_data
from services.get_user_layout import get_stored_layout, unpack_layout
from utils.generate_parse_id import generate_parse_id


def handle_search(
    request: Request, db: SQLAlchemy, search_data: dict, standard_layout: BasicLayout
) -> str:
    """
    Extract the user's current layout, apply search filters, save the result
    under a newly created identifier and return the identifier to the client
    so the user can navigate to it.

    If we cannot find a layout, we simply use the standard layout.

    If the current layout has a base layout, we use that as the base for a new search.

    If the current layout does not have a base layout, it means it the
    original result of a parse, so we use that as our base.
    """

    stored_layout = get_stored_layout(request, db)
    if stored_layout is None:
        layout = standard_layout
        base_id = None
    elif stored_layout.based_on is None:
        layout = unpack_layout(stored_layout)
        base_id = stored_layout.parse_id
    else:
        # The user's current layout is itself based on another layout, so
        # we use that as our base.
        layout = unpack_layout(stored_layout.based_on)
        base_id = stored_layout.based_on.parse_id

    # Converts the filters of type FilterInfo (JS) to SearchFilter (Python).
    search_filters = get_search_filters_from_data(search_data)
    searched_layout = perform_search_on_layout(layout, search_filters)

    identifier = save_search_result_and_filters(
        searched_layout, search_filters, db, base_id
    )

    return identifier


def save_search_result_and_filters(
    layout: BasicLayout,
    search_filters: list[SearchFilter],
    db: SQLAlchemy,
    base_id: int,
) -> str:
    """
    Save the search result and the associated filters in the database.
    """
    pickled_layout = pickle.dumps(layout)
    pickled_search_filters = pickle.dumps(search_filters)

    identifier = generate_parse_id()

    new_result = StoredLayout(
        timestamp=datetime.now(),
        parse_id=identifier,
        layout=pickled_layout,
        search_filters=pickled_search_filters,
        based_on_id=base_id,
    )
    db.session.add(new_result)
    db.session.commit()

    log.debug("Search result stored in DB")

    return identifier
