from app.db.session import engine
from app.db.base import Base
from app.models import customer, product, price, subscription  # import all models

def init():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done.")

if __name__ == "__main__":
    init()
