import streamlit as st
import pandas as pd
import folium  # 'folium'을 별칭 없이 임포트합니다.
from streamlit_folium import st_folium

# 데이터 로드 및 전처리
file_path = "gangnamgupublicparking.csv"
data = pd.read_csv(file_path, encoding='utf-8')  # 또는 'latin1', 'iso-8859-1' 등
data = data.copy().fillna(0)  # 결측값을 0으로 채움

# 지도 시각화를 위한 데이터 처리
data['size'] = data['주차구획수']

# 주차장 유형별 색상 지정
parking_type_colors = {'노상': '#37eb91', '부설': '#ebbb37', '노외': '#00FFFF'}
data['color'] = data['주차장유형'].map(parking_type_colors)

# Streamlit 앱 시작
st.title('강남구 공영주차장 안내')

# 지도 표시
st.map(data, latitude='위도', longitude='경도', size='size', color='color')

# 월정기권 요금 필터링을 위한 UI
st.title("유료 월정기권 취급 주차장 정보")

view_option = st.radio(
    "주차장 유형 선택",
    ("유료 월정기권 취급 주차장", "월정기권 미취급 주차장")
)

# 월정기권 요금에 따른 데이터 필터링 및 색상 지정
if view_option == "유료 월정기권 취급 주차장":
    filtered_data = data[data['월정기권요금'] > 0]
    st.subheader("유료 월정기권 취급 주차장")
    filtered_data['color'] = "#FF0000"  # 빨간색
else:
    filtered_data = data[data['월정기권요금'] == 0]
    st.subheader("월정기권 미취급 주차장")
    filtered_data['color'] = "#00FF00"  # 초록색

# Folium 지도 생성
m = folium.Map(location=[filtered_data['위도'].mean(), filtered_data['경도'].mean()], zoom_start=13)

# 주차장 데이터를 지도에 표시
for idx, row in filtered_data.iterrows():
    folium.CircleMarker(
        location=[row['위도'], row['경도']],
        radius=row['size'] / 10,
        color=row['color'],
        fill=True,
        fill_color=row['color'],
        popup=f"주차장명: {row['주차장명']}<br>월정기권요금: {row['월정기권요금']}원"
    ).add_to(m)

# Streamlit에 지도 표시
st_data = st_folium(m, width=800, height=500)

# 주차 요금 계산기
st.title("강남구 공영주차장 요금 계산기")

# 주차 요금 계산을 위한 데이터 준비
columns_needed = ['주차장명', '주차기본시간', '주차기본요금', '추가단위시간', '추가단위요금']
parking_fee_data = data[columns_needed].dropna()

# 데이터 타입 변환
parking_fee_data['주차기본시간'] = parking_fee_data['주차기본시간'].astype(float)
parking_fee_data['주차기본요금'] = parking_fee_data['주차기본요금'].astype(float)
parking_fee_data['추가단위시간'] = parking_fee_data['추가단위시간'].astype(float)
parking_fee_data['추가단위요금'] = parking_fee_data['추가단위요금'].astype(float)

# 주차 요금 계산 함수
def calculate_parking_fee(parking_name, parking_duration):
    parking_info = parking_fee_data[parking_fee_data['주차장명'] == parking_name]
    if parking_info.empty:
        return "주차장 정보를 찾을 수 없습니다."
    
    parking_info = parking_info.iloc[0]
    base_time = parking_info['주차기본시간']
    base_fee = parking_info['주차기본요금']
    additional_time = parking_info['추가단위시간']
    additional_fee = parking_info['추가단위요금']
    
    # 요금 계산
    if parking_duration <= base_time:
        total_fee = base_fee
    else:
        extra_time = parking_duration - base_time
        total_fee = base_fee + (extra_time // additional_time) * additional_fee
        if extra_time % additional_time > 0:
            total_fee += additional_fee  # 남은 시간은 추가 요금 한 번 더 부과
    
    return f"총 주차 요금: {total_fee:.0f}원"

# 주차 요금 계산기 UI
with st.form("parking_fee_form"):
    parking_name = st.selectbox("주차장명", parking_fee_data['주차장명'].unique())
    parking_duration = st.number_input("주차시간(분)", min_value=0, step=1)
    submitted = st.form_submit_button("요금 계산")
    
    if submitted:
        # 주차 요금 계산 및 결과 출력
        fee = calculate_parking_fee(parking_name, parking_duration)
        st.success(fee)
