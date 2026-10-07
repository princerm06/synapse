import argparse

from app.database import SessionLocal
from app.models.page_db import Page
from app.services.reprocessing import rebuild_page_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild chunks for existing Synapse pages from stored content."
    )
    parser.add_argument("page_ids", nargs="+", type=int)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the rebuild. Without this flag the command is a dry run.",
    )
    args = parser.parse_args()

    requested_ids = list(dict.fromkeys(args.page_ids))

    with SessionLocal() as db:
        pages = (
            db.query(Page)
            .filter(Page.id.in_(requested_ids))
            .order_by(Page.id)
            .all()
        )
        found_ids = {page.id for page in pages}
        missing = [page_id for page_id in requested_ids if page_id not in found_ids]
        if missing:
            raise RuntimeError(f"Pages not found: {missing}")

        if not args.apply:
            print("Dry run only; no database changes will be committed.")
            for page in pages:
                print(
                    f"{page.id:>2} | content_chars={len(page.content):>7} | {page.title}"
                )
            print("Re-run with --apply to rebuild these pages.")
            return

        try:
            for page in pages:
                count = rebuild_page_chunks(db, page)
                print(f"{page.id:>2} | rebuilt_chunks={count:>3} | {page.title}")
            db.commit()
        except Exception:
            db.rollback()
            raise

    print("Reprocessing committed successfully.")


if __name__ == "__main__":
    main()
