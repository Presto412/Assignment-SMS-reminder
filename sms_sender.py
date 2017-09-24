

# author - Priyansh Jain
# date - 24/09/2017



import requests
import time

def sendSMS(message, from_number, password, to_number):

    login_url = 'http://site24.way2sms.com/Login1.action'
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 \
        Safari/537.36'}
    login = requests.post(
        login_url,
        data={
            'username': from_number,
            'password': password},
        headers=headers
    )

    session_cookie = login.request.headers['Cookie']
    token = session_cookie[15:]
    headers.update({'Cookie': session_cookie})

    send_sms_url = 'http://site24.way2sms.com/smstoss.action'
    sms_data = {
        'ssaction': 'ss',
        'Token': token,
        'mobile': str(to_number),
        'message': str(message),
        'msgLen': str(len(message))
    }
    time.sleep(2)
    send_sms = requests.post(
        send_sms_url,
        data=sms_data,
        headers=headers
    )
# if __name__=='__main__':
#     main()
