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
    <td align="left" style="width:5%;">Period</td>
    <td align="left">Course Title</td>
    <td align="left">Room Name</td>
    <td align="left">Teacher</td>
    """

    for key in dict.keys(outputs[0]):
        if str(key).isupper():
            table_header += ("<td align='left' style='width:10%;'>" + key + "</td>")
    return table_header

def get_table_body(outputs):
    tableBody = ""
    for clazz in outputs:
        tableBody += "<tr>"
        tableBody += ("<td>" + clazz["Period"] + "</td>")
        tableBody += ("<td>" + clazz["Course Title"] + "</td>")
        tableBody += ("<td>" + clazz["Room Name"] + "</td>")
        tableBody += ("<td>" + clazz["Teacher"] + "</td>")

        for key in dict.keys(clazz):
            if str(key).isupper():
                tableBody += ("<td>" + clazz[key] + "</td>")
        tableBody += "</tr>"
    return tableBody