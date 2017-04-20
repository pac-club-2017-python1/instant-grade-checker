import threading

import time

from igc.util import studentvue

students = {}

def addStudent(studentId, password):
    if type(studentId) is not int:
        raise AssertionError("Student ID must be int")

    if not students.has_key(studentId):
        students[studentId] = {"password": password, "lastUpdated": 0, "table_body": None, "full_name": None, "welcome_message": None}

def cacheStudentData(studentId, student):
    password = student["password"]
    print("Caching for student id: " + str(studentId))
    browser = studentvue.get_browser_authenticated(studentId, password)
    browser.click_link_by_partial_href('PXP_Gradebook.aspx?AGU=0')
    full_name = studentvue.get_full_name(browser)
    welcome_message = studentvue.get_welcome_message(browser)
    table_body = studentvue.get_table_body(browser)
    browser.quit()

    student["full_name"] = full_name
    student["welcome_message"] = welcome_message
    student["table_body"] = table_body
    student["lastUpdated"] = int(time.time())
    print("Finished caching for student id: " + str(studentId))

class CacheThread(threading.Thread):

    def __init__(self):
        print("Cache started")
        threading.Thread.__init__(self)

    def run(self):
        while True:
            for studentId in students:
                student = students[studentId]
                lastUpdated = student["lastUpdated"]
                currentTime = int(time.time())
                shouldUpdate = (currentTime - lastUpdated) > 60*60
                if shouldUpdate:
                    cacheStudentData(studentId, student)
                time.sleep(2)
            time.sleep(10)