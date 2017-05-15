from contextlib import contextmanager

import sys

import datetime
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

class DummyLogger(object):
    def __init__(self, stream, *files):
        self.stream = stream
        self.files = files

    def write(self, obj):
        self.stream.write(obj)
        for f in self.files:
            i = datetime.datetime.now()
            if str(obj).strip() != "":
                date = "[" + i.strftime('%Y/%m/%d %H:%M:%S') + "] "
                f.write(date + str(obj).strip() + "\n")
        self.flush()
    def flush(self) :
        self.stream.flush()
        for f in self.files:
            f.flush()

def setupLog():
    f = open('output.log', 'a+')
    sys.stdout = DummyLogger(sys.stdout, f)
    sys.stderr = DummyLogger(sys.stderr, f)