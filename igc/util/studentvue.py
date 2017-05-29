import re
from splinter import Browser

from igc.util import util
from igc.util.util import session_scope
import signal

service_args = [
    '--proxy=127.0.0.1:1080',
    '--proxy-type=socks5',
]

def quit_browser(browser):
    try:
        browser.driver.service.process.send_signal(signal.SIGTERM)
        browser.quit()
    except OSError as e:
        print "Ran into OSError: " + e.message

def check_authentication(studentId, password):
    browser  = Browser('phantomjs', service_args=service_args)
    url = 'https://parentvue.vbcps.com/Login_Student_PXP.aspx'
    browser.visit(url)

    try:
        browser.find_by_id('username').fill(studentId)
        browser.find_by_id('password').fill(password)
        browser.find_by_id('Submit1').click()
    except AttributeError:
        return False, None


    if browser.url == 'https://parentvue.vbcps.com/Home_PXP.aspx':
        return True, browser
    else:
        User = util.models["user"]
        with session_scope(util.db) as session:
            user = session.query(User).filter(User.student_id == studentId).first()
            if user:
                user.needsUpdate = True

        return False, browser


def get_browser_authenticated(studentId, password):
    isCorrect, browser = check_authentication(studentId, password)

    if isCorrect == False and browser is not None:
        print "Invalid user credentials for: " + str(studentId)
        return None, True
    elif isCorrect and browser is not None:
        return browser, False
    else:
        return None, False

def get_full_name(browser):
    return browser.find_by_css('.UserHead').find_by_css("*").first.text.title()


def get_grade_info(browser):
    output = []
    tables = browser.find_by_css(".info_tbl")
    for table in tables:
        titles_array = table.find_by_css(".row_subhdr")[0].find_by_css("*")
        titles = []
        for title in titles_array:
            titles.append(str(title.text).strip())

        classes_array = table.find_by_css(".altrow1,.altrow2")
        for clazz in classes_array:
            clazzObj = {}
            children = clazz.find_by_tag("td")
            for i in range(0, len(children)):
                clazzObj[titles[i]] = str(children[i].text).strip()
            output.append(clazzObj)

    #Merger
    markForDeletion = []
    for i in range(0, len(output)):
        firstClass = output[i]
        for i2 in range(i+1, len(output)):
            secondClass = output[i2]
            if firstClass["Course Title"] == secondClass["Course Title"]:
                for key in dict.keys(firstClass):
                    if str(key).isupper() and secondClass[key] == "N/A (0)":
                        secondClass[key] = firstClass[key]
                markForDeletion.append(i)
    for delete in markForDeletion:
        output.pop(delete)

    return output


def get_table_headers(outputs):
    table_header =  \
    """
    <td align="left" style="width:3%;">Period</td>
    <td align="left">Course Title</td>
    """

    for key in dict.keys(outputs[0]):
        if str(key).isupper():
            table_header += ("<td align='left' style='width:13%;'>" + key + "</td>")
    return table_header

def get_table_body(outputs):
    tableBody = ""
    for clazz in outputs:
        tableBody += "<tr>"
        tableBody += ("<td>" + clazz["Period"] + "</td>")
        tableBody += ("<td>" + re.sub(r'\([^)]*\)', '', clazz["Course Title"]).strip() + "</td>")

        for key in dict.keys(clazz):
            if str(key).isupper():
                tableBody += ("<td>" + clazz[key] + "</td>")
        tableBody += "</tr>"
    return tableBody


def get_class_schedule(outputs):
    table_header = \
    """
    <td align="left" style="width:3%;">Period</td>
    <td align="left">Course Title</td>
    <td align="left" style="width:15%;">Room</td>
    <td align="left" style="width:25%;">Teacher</td>
    """
    table_body = ""
    for clazz in outputs:
        table_body += "<tr>"
        table_body += ("<td>" + clazz["Period"] + "</td>")
        table_body += ("<td>" + re.sub(r'\([^)]*\)', '', clazz["Course Title"]).strip() + "</td>")
        table_body += ("<td>" + clazz["Room Name"] + "</td>")
        table_body += ("<td>" + clazz["Teacher"] + "</td>")
        table_body += "</tr>"


    return "<thead>" + table_header + "</thead><tbody>" + table_body + "</tbody>"