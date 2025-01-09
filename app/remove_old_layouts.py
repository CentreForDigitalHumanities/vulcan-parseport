from app import create_app, db
from utils.timestamps import remove_old_layouts


# Designed to run as part of a cronjob (or similar) to remove old layouts from the database.
def main() -> None:
    app = create_app()
    with app.app_context():
        remove_old_layouts(db)


if __name__ == "__main__":
    main()
