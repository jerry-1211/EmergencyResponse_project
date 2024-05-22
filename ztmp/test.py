import folium

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=10)

# 저장
m.save('map_test.html')