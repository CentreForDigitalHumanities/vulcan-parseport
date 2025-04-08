import pickle
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from vulcan.file_loader import BasicLayout
from vulcan.search.search import perform_search_on_layout, SearchFilter

from db.models import StoredLayout
from logger import log
from services.server_methods import get_search_filters_from_data
from utils.generate_parse_id import generate_parse_id


def handle_search(
    db: SQLAlchemy, search_data: dict, standard_layout: BasicLayout
) -> str:
    """
    Apply search filters to the standard layout, save the result  under a newly
    created identifier and return the identifier to the client so the user can
    navigate to the corresponding page.
    """
    search_filters = get_search_filters_from_data(search_data)
    searched_layout = perform_search_on_layout(standard_layout, search_filters)
    identifier = save_search_result_and_filters(searched_layout, search_filters, db)

    return identifier


def save_search_result_and_filters(
    layout: BasicLayout,
    search_filters: list[SearchFilter],
    db: SQLAlchemy,
) -> str:
    """
    Save the search result and the associated filters in the database.
    """

    pickled_layout = pickle.dumps(layout)
    pickled_search_filters = pickle.dumps(search_filters)

    identifier = generate_parse_id()

    new_result = StoredLayout(
        parse_id=identifier,
        timestamp=datetime.now(),
        layout=pickled_layout,
        search_filters=pickled_search_filters,
    )
    db.session.add(new_result)
    db.session.commit()

    log.debug("Search result stored in DB")

    return identifier
