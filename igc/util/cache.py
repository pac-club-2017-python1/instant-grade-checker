import base64
import threading
import time

from igc.util import studentvue, util, crypto
from igc.util.util import session_scope

lock = threading.Lock()
_students = {}
ALLOW_PIN_CACHE = True

def initalizeCache():
    from igc.controller import auth_controller
    if ALLOW_PIN_CACHE:
        User = util.models["user"]
        with session_scope(util.db) as session:
            users = session.query(User).all()
            for user in users:
                if user.pid != "NULL":
                    key = crypto.generate_fernet_key(base64.urlsafe_b64decode(str(user.pid)), user.salt)
                    fernet = crypto.get_fernet_with_key(key)
                    success, password = crypto.login(fernet, user.hash)
                    if success:
                        auth_controller.user_keys[int(user.student_id)] = password
                        _students[user.student_id] = {"password": password, "lastUpdated": 0, "table_body": None, "full_name": None, "welcome_message": None}

def addStudent(studentId, password):
    lock.acquire()
    try:
        if type(studentId) is not int:
            raise AssertionError("Student ID must be int")
        if not _students.has_key(studentId):
            _students[studentId] = {"password": password, "lastUpdated": 0, "table_body": None, "full_name": None, "welcome_message": None}
        return _students[studentId]
    finally:
        lock.release()
    return None

def getStudent(studentId, lockMethod=True):
    if lockMethod:
        lock.acquire()
    try:
        return _students[studentId]
    finally:
        if lockMethod:
            lock.release()

def cacheStudentData(studentId, student):
    lock.acquire()
    try:
        password = student["password"]
    finally:
        lock.release()

    print("Caching for student id: " + str(studentId) + " on thread: " +  str(threading.current_thread()))
    browser = studentvue.get_browser_authenticated(studentId, password)

    if not browser:
        _students.pop(int(studentId))
        return

    browser.click_link_by_partial_href('PXP_Gradebook.aspx?AGU=0')
    full_name = studentvue.get_full_name(browser)
    outputs = studentvue.get_grade_info(browser)
    table_headers = studentvue.get_table_headers(outputs)
    table_body = studentvue.get_table_body(outputs)
    browser.quit()

    lock.acquire()
    try:
        student["full_name"] = full_name
        student["table_headers"] = table_headers
        student["table_body"] = table_body
        student["lastUpdated"] = int(time.time())
        print("Finished caching for student id: " + str(studentId)  + " on thread: " +  str(threading.current_thread()))
    finally:
        lock.release()


class CacheThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Cache started on thread: " + str(threading.current_thread()))
        while True:
            updateArray = []
            try:
                lock.acquire()
                for studentId in _students:
                    student = getStudent(studentId, False)
                    lastUpdated = student["lastUpdated"]
                    currentTime = int(time.time())
                    shouldUpdate = (currentTime - lastUpdated) > (60*30)
                    if shouldUpdate:
                        updateArray.append({"studentId" : studentId, "student" : student})
            finally:
                lock.release()

            for studentObj in updateArray:
                cacheStudentData(studentObj["studentId"], studentObj["student"])
            time.sleep(10)
