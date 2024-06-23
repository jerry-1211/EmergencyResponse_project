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
<<<<<<< HEAD
        self.data["messages"][0]["text"] = f"{user}님이 현재 쓰러짐의 행동을 취하셨습니다. {user}님의 상태를 주의있게 봐주세요!!"
        res = message.send_many(self.data)
        print(f'현재 남은 금액 : {res.json()["log"][2]["newBalance"]}')

    def send_urgent(self,user,g_ph):
        self.data["messages"][0]["to"] = g_ph
        self.data["messages"][0]["from"] = "01024934320"
        self.data["messages"][0]["text"] = f"{'#' * 24}{user}님이 쓰러지셨습니다. {'#' * 24}"
=======
        self.data["messages"][0]["text"] = f"{user}님이 현재 쓰러짐의 행동을 취하셨습니다 {user}님의 상태를 주의있게 봐주세요!!"
>>>>>>> 6f1bb88aeda8becd144eca4f6ab7d39fddf41e9e
        res = message.send_many(self.data)
        print(f'현재 남은 금액 : {res.json()["log"][2]["newBalance"]}')

# mg = SMS()
# mg.send_urgent("김지현","01024934320")
