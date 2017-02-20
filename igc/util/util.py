from contextlib import contextmanager

from sqlalchemy.orm import Session


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