


# author - Priyansh Jain
# date - 24/09/2017



# external libraries
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
from PIL import Image

# stock library imports
from getpass import getpass
import base64
from pprint import pprint
import datetime
import os
import sys

# for not creating .pyc files
sys.dont_write_bytecode = True

# file-system imports
from DAscraper import *
from captchaparser import *
from sms_sender import sendSMS


# registration_number = "your_registration_number_here"
registration_number = raw_input("Enter registration number:")

# vtop_password = "your_password_here"
vtop_password = getpass("Enter VTOP password:")

# the current semester code, update on sem change
semSubId = 'VL2017185'

# to_number = "to_mobile_number_here"
from_number = raw_input("Enter sender number:")
way2sms_password = getpass("Enter way2sms password:")
to_number = raw_input("Enter recipient number:")

today = datetime.date.today()

def send_sms(message_dict):
    message_str = ''.join('{}:{}|'.format(key, val) for key, val in sorted(message_dict.items()))
    message_list = [sendSMS(message_str[i:i+140], from_number, way2sms_password, to_number)
                    for i in range(0,len(message_str),140)]

def compare_dates(topic):
    if topic['due-date'] != '-':
        due_date = datetime.datetime.strptime(
            topic['due-date'], "%d-%b-%Y").date()
        if (due_date - today).days <= 2 and (due_date - today).days >= 0 and due_date.month == today.month:
            return topic['title'] + '-' + str((due_date - today).days)
        else:
            return
    else:
        return

def process_timetable(row):
    cells = row.find_all("td")
    return {
        'course_code': cells[2].text.strip().encode('utf-8'),
        'course_title': cells[3].text.strip().encode('utf-8'),
        'course_type': cells[4].text.strip().encode('utf-8'),
        'class_no': cells[7].text.strip().encode('utf-8'),
        'slot': cells[8].text.strip().replace('+', ' ').encode('utf-8'),
        'venue': cells[9].text.strip().encode('utf-8'),
        'faculty_name': cells[10].text.strip().split('\n')[0].encode('utf-8')
    }

def process_da_page(headers, course):
    da_page = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/examinations/processDigitalAssignment',
            headers=headers,
            data={
                'classId': course['class_no']},
            verify=False)
    return get_DA_details(da_page)

def main():
    # ssl security warning disable
    requests.packages.urllib3.disable_warnings(
        InsecureRequestWarning)

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 \
        Safari/537.36'}

    main_page = requests.get(
        'https://vtopbeta.vit.ac.in/vtop/',
        headers=headers,
        verify=False)

    # session_cookie
    session_cookie = main_page.cookies['JSESSIONID']
    session_cookie = 'JSESSIONID=' + session_cookie
    headers.update({'cookie': session_cookie})

    # captcha solving
    root = BeautifulSoup(main_page.text, "html.parser")
    img_data = root.find_all("img")[1]["src"].strip("data:image/png;base64,")
    with open("captcha.png", "wb") as fh:
        fh.write(base64.b64decode(img_data))
    img = Image.open("captcha.png")
    captcha_check = CaptchaParse(img)
    os.remove("captcha.png")

    # user login
    login_data = {
        'uname': registration_number,
        'passwd': vtop_password,
        'captchaCheck': captcha_check}
    login = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/processLogin',
        headers=headers,
        data=login_data,
        verify=False)

    # timetable scraper
    timetable = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/processViewTimeTable',
        headers=headers,
        data={'semesterSubId': semSubId},
        verify=False)
    root = BeautifulSoup(timetable.text, "html.parser")
    table = root.find_all(class_="table")[0]
    course_details = [process_timetable(row)
                      for row in table.find_all("tr")[2:-2]]

    # digital assignment page pinging
    doDigitalAssignment = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/examinations/doDigitalAssignment',
        data={'semesterSubId': semSubId},
        headers=headers,
        verify=False)


    # dictionary containing all DA related information, key is coursecode
    da_details = {course['course_code'] + '/' + course['course_type']: process_da_page(headers,course)
                  for course in course_details if process_da_page(headers,course)}

    # dictionary containing due dates of assignments pending in the next two days
    message_dict = {course : [compare_dates(topic) for topic in da_details[course] if compare_dates(topic)]
                    for course in da_details if [compare_dates(topic) for topic in da_details[course] if compare_dates(topic)]}

    send_sms(message_dict)

if __name__ == '__main__':
    main()
