import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="전기차 통계 대시보드", layout="wide")

# ------------------ 사이드 메뉴 ------------------
st.sidebar.title("📊 메뉴")
menu = st.sidebar.radio("이동할 기능을 선택하세요", ["차량 등록 통계", "충전소 인프라", "FAQ 검색", "통계 분석"])

# ------------------ 차량 등록 통계 ------------------
if menu == "차량 등록 통계":
    st.title("🚗 차량 등록 통계 대시보드")
    st.markdown("차량 등록 현황을 지역과 기간별로 시각화합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        region = st.selectbox("지역 선택", ["서울", "경기", "부산", "대구", "광주"])
    with col2:
        vehicle_type = st.selectbox("차량 유형", ["승용", "화물", "승합", "특수"])
    with col3:
        car_type = st.selectbox("차종", ["전기", "수소", "하이브리드", "내연기관"])

    year_range = st.slider("기간 선택 (년도)", 2011, 2025, (2018, 2025))

    st.subheader("📈 등록 대수 추이 (예시 데이터)")
    df = pd.DataFrame({
        "연도": list(range(year_range[0], year_range[1] + 1)),
        "등록대수": np.random.randint(10000, 50000, year_range[1] - year_range[0] + 1)
    })
    st.line_chart(df.set_index("연도"))

    st.metric(label="총 등록대수", value=f"{df['등록대수'].sum():,} 대")
    st.metric(label="연평균 증가율", value=f"{df['등록대수'].pct_change().mean()*100:.1f}%")

# ------------------ 충전소 인프라 ------------------
elif menu == "충전소 인프라":
    st.title("🔌 전기차 충전소 인프라")
    st.markdown("전국 충전소 위치 및 운영 정보를 제공합니다.")

    col1, col2 = st.columns(2)
    with col1:
        selected_region = st.selectbox("지역", ["서울", "경기", "부산", "대전", "전국"])
    with col2:
        charge_type = st.selectbox("충전 타입", ["급속", "완속", "초급속"])

    st.subheader("🗺️ 지도 기반 충전소 위치 (더미 데이터)")
    dummy_map_data = pd.DataFrame({
        'lat': [37.5665, 37.4563, 35.1796],
        'lon': [126.9780, 126.7052, 129.0756],
    })
    st.map(dummy_map_data)

    st.subheader("🔍 충전소 목록")
    st.table(pd.DataFrame({
        "충전소명": ["서울역 충전소", "부산 센터", "인천 남동"],
        "충전기 수": [3, 5, 2],
        "운영상태": ["운영 중", "점검 중", "운영 중"]
    }))

# ------------------ FAQ 검색 ------------------
elif menu == "FAQ 검색":
    st.title("❓ FAQ 검색 시스템")
    st.markdown("자주 묻는 질문을 검색하고 답변을 확인하세요.")

    question = st.text_input("무엇이 궁금한가요?")
    category = st.selectbox("FAQ 카테고리", ["전체", "차량 등록", "충전소", "보조금", "환경규제"])

    if st.button("검색"):
        st.subheader("🔍 검색 결과 (예시)")
        with st.expander("Q. 전기차 보조금은 얼마나 받을 수 있나요?"):
            st.write("A. 지역별로 다르며 최대 약 700만원까지 받을 수 있습니다.")
        with st.expander("Q. 충전소 고장은 어디에 신고하나요?"):
            st.write("A. 환경부 무공해차 통합누리집 또는 관할 지자체에 신고하세요.")

# ------------------ 통계 분석 자리 ------------------
elif menu == "통계 분석":
    st.title("📊 통계 분석 (데이터 연결 예정)")
    st.info("데이터가 연결되면 아래에 다양한 분석 시각화가 표시될 예정입니다.")

    st.markdown("예시 차트 영역 (현재는 임시 데이터)")
    df_demo = pd.DataFrame({
        "월": pd.date_range("2025-01", periods=6, freq="M"),
        "전기차 등록": np.random.randint(500, 2000, size=6)
    })
    st.bar_chart(df_demo.set_index("월"))

    st.warning("🚧 이 영역은 추후 통계 분석 자료와 연동됩니다.")