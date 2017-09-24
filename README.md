# Assignment-SMS-reminder
Checks your VTOP student portal for upcoming assignments and sends a reminder SMS


This script scrapes your VTOP student login and checks for any assignments pending. If found with due-date in the following couple of days,it sends sms with the details of all assignments




The message sending part is handled by the script sms_sender, that uses way2sms scraping to send message. Obviously, you have to register an account with way2sms to get this script working.



To install dependencies 
'''
$ pip install -r requirements.txt
'''



I scheduled this on cron to run every night at 9pm.

To execute the main file,

'''python
$ python main.py
'''


That's all, Folks.
