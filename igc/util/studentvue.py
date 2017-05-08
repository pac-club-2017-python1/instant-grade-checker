from splinter import Browser


def check_authentication(studentId, password):
    browser  = Browser('phantomjs')
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
        return False, browser


def get_browser_authenticated(studentId, password):
    isCorrect, browser = check_authentication(studentId, password)
    if isCorrect and browser is not None:
        return browser
    else:
        raise AssertionError("Invalid user credentials")


def get_full_name(browser):
    return browser.find_by_css('.UserHead').find_by_css("*").first.text.title()


def get_welcome_message(browser):
    u = None
    array = browser.find_by_css(".row_subhdr")
    if len(array) > 1:
        u = array[len(array) - 1]
    else:
        u = array.first
    return u.html.replace('<td align="left" valign="top">Resources</td>', "")


def get_table_body(browser):
    tableBody = ""
    list = browser.find_by_css(".altrow1,.altrow2")
    for clazz in list:
        children = clazz.find_by_tag("a")
        tableBody += "<tr>"

        if len(children) == 6:
            for child in children:
                tableBody += ("<td>" + child.text + "</td>")
        else:
            tableBody += ("<td>" + children[0].text + "</td>")
            tableBody += "<td>N/A</td>"
            tableBody += ("<td>" + children[1].text + "</td>")
            tableBody += ("<td>" + children[2].text + "</td>")
            tableBody += ("<td>" + children[3].text + "</td>")
            tableBody += ("<td>" + children[4].text + "</td>")
    tableBody += "<tr>"
    return tableBody