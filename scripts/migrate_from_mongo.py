import os
import sys
import django
from pymongo import MongoClient
from bson import ObjectId

# ===== Django init =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from quotes.models import Author, Quote


# ===== Mongo connect =====
MONGO_URI = "mongodb+srv://mongo_user:mongo_pass@cluster0.m7ejzko.mongodb.net/quotes_db?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
mongo_db = client["quotes_db"]

authors_col = mongo_db["authors"]
quotes_col = mongo_db["quotes"]


def normalize(name):
    if not name:
        return ""
    return str(name).strip().lower()


# ===== Load authors into a dictionary by _id and by normalized fullname =====
def load_authors_from_mongo():
    authors_by_id = {}
    authors_by_name = {}

    for a in authors_col.find():
        mid = a["_id"]
        fullname = a.get("fullname", "").strip()

        authors_by_id[mid] = a
        authors_by_name[normalize(fullname)] = a

    return authors_by_id, authors_by_name


# ===== Migrate AUTHORS to Postgres =====
def migrate_authors(authors_by_name):
    print("➡️ Migrating authors...")

    django_authors = {}

    for norm_name, a in authors_by_name.items():
        fullname_raw = a.get("fullname", "").strip()

        obj, created = Author.objects.get_or_create(
            fullname=fullname_raw,
            defaults={
                "born_date": a.get("born_date", ""),
                "born_location": a.get("born_location", ""),
                "description": a.get("description", ""),
            }
        )

        django_authors[norm_name] = obj

        print(f"   {'✔️ created' if created else '✓ exists'} — {fullname_raw}")

    print("✅ Authors migration done.")
    return django_authors


# ===== Migrate QUOTES to Postgres =====
def migrate_quotes(authors_by_id, django_authors):
    print("\n➡️ Migrating quotes...")

    for q in quotes_col.find():
        quote_text = q.get("quote", "").strip()
        if not quote_text:
            continue

        author_field = q.get("author")

        # Case 1: author is ObjectId
        if isinstance(author_field, ObjectId):
            a = authors_by_id.get(author_field)
            if a:
                fullname_raw = a.get("fullname", "").strip()
            else:
                fullname_raw = "Unknown Author"

        # Case 2: author is normal string
        elif isinstance(author_field, str):
            fullname_raw = author_field.strip()

        else:
            fullname_raw = "Unknown Author"


        # Normalize for dictionary lookup
        norm_name = normalize(fullname_raw)

        # Case 3: If author not in migrated authors → create new
        if norm_name not in django_authors:
            print(f"⚠️ Author '{fullname_raw}' not found → creating...")
            author_obj, _ = Author.objects.get_or_create(fullname=fullname_raw)
            django_authors[norm_name] = author_obj
        else:
            author_obj = django_authors[norm_name]

        tags_str = ",".join(q.get("tags", []))

        obj, created = Quote.objects.get_or_create(
            quote=quote_text,
            author=author_obj,
            defaults={"tags": tags_str}
        )

        print(f"   {'✔️ created' if created else '✓ exists'} — {quote_text[:60]}")

    print("✅ Quotes migration done.")


# ===== MAIN =====
if __name__ == "__main__":
    print("🚀 Starting MongoDB → PostgreSQL migration...\n")

    authors_by_id, authors_by_name = load_authors_from_mongo()
    django_authors = migrate_authors(authors_by_name)
    migrate_quotes(authors_by_id, django_authors)

    print("\n🎉 Migration completed successfully!")
