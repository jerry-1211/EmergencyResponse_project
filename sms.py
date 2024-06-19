# import sys
# from sdk.api.message import Message
# from sdk.exceptions import CoolsmsException

# class SmsSender:
#     def __init__(self,api_key,api_secret):
#         self.api_key = api_key
#         self.api_secret = api_secret
#         self.cool = Message(self.api_key, self.api_secret)
    
#     def send_sms(self, to, from_, text):
#         params = dict()
#         params['type'] = 'sms' 
#         params['to'] = to 
#         params['from'] = from_
#         params['text'] = text

#         try:
#             response = self.cool.send(params)
#             print("Success Count : %s" % response['success_count'])
#             print("Error Count : %s" % response['error_count'])
#             print("Group ID : %s" % response['group_id'])

#             if "error_list" in response:
#                 print("Error List : %s" % response['error_list'])

#         except CoolsmsException as e:
#             print("Error Code : %s" % e.code)
#             print("Error Message : %s" % e.msg)

# sms = SmsSender("NCSNJQ6SJGFSBCKT","D0BL78J93ENXTEW1WMTWATZHW2GWFXEO")
# sms.send_sms("01024934320", '01024934320', '딴 짓 누적 !! 집중하세요')


import json
from src.lib import message

class SMS :
    def __init__(self) :
        self.data = {
        'messages': [
            {
                'to': '',
                'from': '',
                'text': ''
            },
           
        ]
    }
    
    def send_emergency(self,user,g_ph):
        self.data["messages"][0]["to"] = g_ph
        self.data["messages"][0]["from"] = "01024934320"
        self.data["messages"][0]["text"] = f"📌{user}님이 현재 쓰러짐의 행동을 취하셨습니다.</br> {user}님의 상태를 주의있게 봐주세요⛑️"
        res = message.send_many(self.data)
        print(f'현재 남은 금액 : {res.json()["log"][2]["newBalance"]}')

# mg = SMS()
# mg.send_typeA("김지현","01024934320","01024934320")
