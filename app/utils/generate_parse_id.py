from uuid import uuid4


def generate_parse_id() -> str:
    """Generate a unique ID that can be used as a route parameter."""
    return str(uuid4()).replace("-", "")
