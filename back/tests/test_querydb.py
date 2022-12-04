
import sys
sys.path.append("..")
from app import models 
from app.routers import query
from app import queryutils

def main():

    SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:password123@localhost:5432/cohortiden'


    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    db = get_db()
    q = query.operate( operator= queryutils.TokenType.DESCENDANTS , term1='SNOMED:196416002', db=db)
    print(q.all())


if __name__ == '__main__':
    main()