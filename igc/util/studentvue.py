from splinter import Browser


def check_authentication(studentId, password):
    browser  = Browser('phantomjs')
    url = 'https://parentvue.vbcps.com/Login_Student_PXP.aspx'
    browser.visit(url)

    browser.find_by_id('username').fill(studentId)
    browser.find_by_id('password').fill(password)
    browser.find_by_id('Submit1').click()

    if browser.url == 'https://parentvue.vbcps.com/Home_PXP.aspx':
        return True, browser
    else:
        return False, browser


def get_browser_authenticated(studentId, password):
    isCorrect, browser = check_authentication(studentId, password)
    if isCorrect:
        return browser
    else:
        raise AssertionError("Invalid user credentials")
