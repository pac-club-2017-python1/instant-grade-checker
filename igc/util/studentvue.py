from splinter import Browser


def check_authentication(studentId, password):
    with Browser('phantomjs') as browser:
        url = 'https://studentvue.vbcps.com/Login_Student_PXP.aspx'
        browser.visit(url)

        browser.find_by_id('username').fill(studentId)
        browser.find_by_id('password').fill(password)
        browser.find_by_id('Submit1').click()

        if browser.url == 'https://studentvue.vbcps.com/Home_PXP.aspx':
            return "OK", browser
    return "Error", browser


def get_browser_authenticated(studentId, password):
   return check_authentication(studentId, password)[1]