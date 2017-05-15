from contextlib import contextmanager

from sqlalchemy.orm import Session

db = None
models = None

@contextmanager
def session_scope(db):
    session = Session(db.engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()