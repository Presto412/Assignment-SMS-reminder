# author - Priyansh Jain
# date - 24/09/2017

# external libraries
import requests
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

import json

with open("credentials.json", "r") as f:
    creds = json.loads(f)

registration_number = creds["reg_no"]

vtop_password = creds["password"]

semSubId = 'VL2017185'

from_number = creds["from_number"]
way2sms_password = creds["way2sms_pass"]
to_number = creds["to_number"]

today = datetime.date.today()


def send_sms(message_dict):
    message_str = ''.join(
        '{}:{}|'.format(key, val) for key, val in sorted(message_dict.items()))
    message_list = [
        sendSMS(message_str[i:i + 140], from_number, way2sms_password,
                to_number) for i in range(0, len(message_str), 140)
    ]


def compare_dates(topic):
    if topic['due-date'] != '-':
        due_date = datetime.datetime.strptime(topic['due-date'],
                                              "%d-%b-%Y").date()
        if (due_date - today).days <= 2 and (
                due_date - today).days >= 0 and due_date.month == today.month:
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
        data={'classId': course['class_no']},
        verify=False)
    return get_DA_details(da_page)


def main():
     print("Exec started")
    # ssl security warning disable
    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }

    res = requests.get(
        'https://vtopbeta.vit.ac.in/vtop/', headers=headers, verify=False)
    headers.update({"Cookie": "JSESSIONID=" + res.cookies["JSESSIONID"]})
    root = BeautifulSoup(res.text, "html.parser")
    gsid_index = root.text.find("gsid=")
    gsid = root.text[gsid_index:gsid_index + 12]
    if gsid[-1] == ';':
        gsid = gsid[:-1]
    res = requests.get(
        'https://vtopbeta.vit.ac.in/vtop/executeApp?' + gsid,
        headers=headers,
        verify=False)
    res = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/getLogin',
        headers=headers,
        verify=False)
    # captcha solving
    headers.update({"Cookie": "JSESSIONID=" + res.cookies["JSESSIONID"]})
    root = BeautifulSoup(res.text, "html.parser")
    img_data = root.find_all("img")[1]["src"].strip("data:image/png;base64,")
    img = Image.open(BytesIO(base64.b64decode(img_data)))
    captcha_check = CaptchaParse(img)

    login_data = {
        'uname': registration_number,
        'passwd': vtop_password,
        'captchaCheck': captcha_check
    }
    res = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/processLogin',
        data=login_data,
        headers=headers,
        verify=False)
    # timetable scraper
    timetable = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/processViewTimeTable',
        data={'semesterSubId': semSubId},
        headers=headers,
        verify=False)
    root = BeautifulSoup(timetable.text, "html.parser")
    # return
    table = root.find_all("table")[0]
    # print(len(table.find_all("tr")[2:-2]))
    # return
    course_details = [
        process_timetable(row) for row in table.find_all("tr")[2:-2]
    ]
    # digital assignment page pinging
    doDigitalAssignment = requests.post(
        'https://vtopbeta.vit.ac.in/vtop/examinations/doDigitalAssignment',
        data={'semesterSubId': semSubId},
        headers=headers,
        verify=False)
    # dictionary containing all DA related information, key is coursecode
    da_details = {
        course['course_code'] + '/' + course['course_type']: process_da_page(
            headers, course)
        for course in course_details if process_da_page(headers, course)
    }

    # dictionary containing due dates of assignments pending in the next two days
    message_dict = {
        course: [
            compare_dates(topic) for topic in da_details[course]
            if compare_dates(topic)
        ]
        for course in da_details if [
            compare_dates(topic) for topic in da_details[course]
            if compare_dates(topic)
        ]
    }
    print("sending sms")
    send_sms(message_dict)
    print("stopped")


if __name__ == '__main__':
    main()
