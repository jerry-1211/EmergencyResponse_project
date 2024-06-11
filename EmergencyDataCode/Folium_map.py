import requests
import pandas as pd 
import numpy as np
import xmltodict
import json
import re
import warnings
import folium
import datetime
from NaverSearchApi import searchApi


search  = searchApi()

class folium_map:
    def __init__(self):        
        search.save_location()
        self.hospital_info = pd.read_csv("EmergencyData/emergency_data.csv")
    
    

    def process_data(self):
        hospital_info = self.hospital_info
        
        for col in ["hvoc","hvgc"]:
            if col in hospital_info.columns:
                # 문자열을 NaN으로 변환하고, NaN을 0으로 대체
                hospital_info[col] = pd.to_numeric(hospital_info[col], errors='coerce').fillna(99999999).astype(int)

        hospital_info.fillna(99999999, inplace=True)
        for col in hospital_info.columns:
            hospital_info[col] = hospital_info[col].replace(99999999,"Unknown")

        hospital_info = hospital_info.astype(str).replace('99999999', 'Unknown')
        
        hospital_info.to_csv("EmergencyData/emergency_data.csv",index=False)  # 병원별 위치 저장 
        return hospital_info



    def make_map(self):
        emergency = self.process_data()

        m = folium.Map(location=[ 36.321655, 127.378953],zoom_start=7)
       
        for idx,hospital in enumerate(emergency["dutyName"]) : 
            popup_html = f'''
            <div style="font-style:italic; font-size: 11pt;">
                <b>병원명:</b> {hospital}<br>
                <b>주소:</b> {emergency["address"][idx]}<br>
                <b>응급 상황판:</b><br>
                - 응급실: {emergency["hvec"][idx]}<br>
                - 수술실: {emergency["hvoc"][idx]}<br>
                - 입원실: {emergency["hvgc"][idx]}<br>
                - MRI가용: {emergency["hvmriayn"][idx]}<br>
                - 인공호흡기가용: {emergency["hvventiayn"][idx]}<br>
                - 구급차가용: {emergency["hvamyn"][idx]}<br>
                <b>응급실전화:</b> {emergency["dutyTel3"][idx]}<br>
                <b>홈페이지:</b> {emergency["hospital_link"][idx]}
            </div>
            '''
            popup = folium.Popup(popup_html, max_width=600, max_height=600)
            
            icon = folium.Icon(
                color = "red",
                icon_color='white',
                icon='a-solid fa-star',
                prefix='fa'
            )
            
            folium.Marker(
                [emergency["mapy"][idx],emergency["mapx"][idx]],
                popup=popup,
                tooltip=f"<b>{hospital}</b>",
                icon=icon
            ).add_to(m)
        
        m.save("templates/map.html")


    # js 코드 추가  (지도 자동 확대 기능)
    def add_custom_script(self,file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            html_content = file.read()

        # map 객체 이름 추출
        map_name_pattern = re.compile(r'var (map_[a-z0-9]+) = L\.map', re.IGNORECASE)
        map_name_match = map_name_pattern.search(html_content)

        if map_name_match:
            map_name = map_name_match.group(1)
            custom_script = f"""
            window.map = {map_name};

            // 부모 창으로부터 메시지를 수신하여 지도 업데이트
            window.addEventListener("message", function (event) {{
                if (event.data && event.data.lat && event.data.lon) {{
                    console.log(event)
                    var map = window.map;
                    // 위도, 경도, zoom 확대
                    map.setView([event.data.lat, event.data.lon], 14);
                }}
            }});
            """

            # 모든 <script> 태그 찾기
            script_pattern = re.compile(r'(<script>[\s\S]*?)</script>', re.IGNORECASE)
            matches = list(script_pattern.finditer(html_content))

            if matches:
                # 마지막 <script> 태그에 custom_script 삽입
                last_match = matches[-1]
                new_script_content = last_match.group(1) + custom_script + '</script>'
                html_content = html_content[:last_match.start()] + new_script_content + html_content[last_match.end():]

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)

        else:
            print("Map object not found in the HTML file.")


    # 하루 최대 1 업데이트 
    def update_last_run_date(self):
        with open("last_run_date.txt", "w") as file:
            file.write(datetime.datetime.now().strftime("%Y-%m-%d"))



# 클래스의 인스턴스를 생성
map_instance = folium_map()


# 인스턴스에서 메서드 호출
map_instance.make_map()
map_instance.add_custom_script("templates/map.html")

map_instance.update_last_run_date()
