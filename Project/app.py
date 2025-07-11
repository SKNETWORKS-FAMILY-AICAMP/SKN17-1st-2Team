import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="전기차 통계 대시보드", layout="wide")

# CSV 경로 설정
DATA_DIR = r"C:\python_basic\Project"

@st.cache_data
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, parse_dates=["RegistrationMonth"])

@st.cache_data
def load_faq_data():
    kor = pd.read_csv("faq_data_kor.csv")
    eng = pd.read_csv("faq_data_eng.csv")
    key = pd.read_csv("faq_data_key.csv")
    return kor, eng, key

@st.cache_data
def load_charger_data():
    df = pd.read_csv("chargers.csv")
    return df

# ------------------ 사이드 메뉴 ------------------
st.sidebar.title("📊 메뉴")
menu = st.sidebar.radio("이동할 기능을 선택하세요", ["차량 등록 통계", "충전소 인프라", "FAQ 검색", "통계 분석"])

# ------------------ 차량 등록 통계 ------------------
if menu == "차량 등록 통계":
    st.title("🚗 차량 등록 통계 대시보드")
    st.markdown("차량 등록 현황을 지역과 기간별로 시각화합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        region = st.selectbox("지역 선택", ["전국", "서울", "경기", "부산", "대구", "광주"])
    with col2:
        vehicle_type = st.selectbox("차량 유형", ["전체", "승용", "화물"])
    with col3:
        car_type = st.selectbox("차종", ["전체", "전기", "하이브리드"])

    year_range = st.slider("기간 선택 (연도)", 2021, 2025, (2021, 2025), step=1)
    df = load_csv("Monthly_Registration_Summary.csv")

    if region != "전국":
        df = df[df["Sido"] == region]
    if vehicle_type != "전체":
        df = df[df["VehicleType"] == vehicle_type]

    monthly_sum = (
        df.groupby("RegistrationMonth")["RegisteredCount"]
        .sum()
        .reset_index()
        .sort_values("RegistrationMonth")
    )
    monthly_sum["월간증가량"] = monthly_sum["RegisteredCount"].diff().fillna(0)
    monthly_sum["Year"] = monthly_sum["RegistrationMonth"].dt.year

    filtered = monthly_sum[
        (monthly_sum["Year"] >= year_range[0]) & (monthly_sum["Year"] <= year_range[1])
    ]

    yearly_df = (
        filtered.groupby("Year")["월간증가량"]
        .sum()
        .reset_index()
        .rename(columns={"Year": "연도", "월간증가량": "등록대수"})
    )

    st.subheader("📈 등록 대수 추이 (실제 신규 등록)")
    if yearly_df.empty:
        st.warning("해당 조건에 맞는 데이터가 없습니다.")
    else:
        st.line_chart(yearly_df.set_index("연도"))
        total = yearly_df["등록대수"].sum()
        growth_rate = yearly_df["등록대수"].pct_change().mean() * 100
        st.metric(label="총 등록대수", value=f"{total:,.0f} 대")
        st.metric(label="연평균 증가율", value=f"{growth_rate:.1f}%")

# ------------------ 충전소 인프라 ------------------
elif menu == "충전소 인프라":
    st.title("🔌 충전소 인프라 분포도")
    st.markdown("전국 충전소 위치를 지도에서 확인할 수 있습니다.")

    df = load_charger_data()

    st.subheader("🗺️ 전국 충전소 지도")
    if "lat" in df.columns and "lng" in df.columns:
        map_df = df.rename(columns={"lat": "lat", "lng": "lon"})
        st.map(map_df)
    else:
        st.warning("위도 및 경도 정보가 부족하여 지도를 표시할 수 없습니다.")

    st.subheader("🔍 충전소 샘플")
    st.write(f"총 충전소 수: {len(df):,} 개")
    st.dataframe(df.head(20))

# ------------------ FAQ 검색 ------------------
elif menu == "FAQ 검색":
    st.title("❓ 전기차 FAQ 검색 시스템")
    faq_kor, faq_eng, faq_key = load_faq_data()
    language = st.radio("언어 선택", ["한국어", "English"], horizontal=True)
    faq_df = faq_kor if language == "한국어" else faq_eng
    df = faq_df.merge(faq_key, on="key_num", how="left")

    category_options = ["전체"] + sorted(df["key_name"].dropna().unique().tolist())
    selected_category = st.selectbox("카테고리 선택", category_options)
    query = st.text_input("궁금한 내용을 입력하세요:")

    results = df.copy()
    if selected_category != "전체":
        results = results[results["key_name"] == selected_category]
    if query.strip():
        results = results[
            results["title"].str.contains(query, case=False, na=False) |
            results["content"].str.contains(query, case=False, na=False)
        ]

    if results.empty:
        st.warning("표시할 FAQ가 없습니다. 카테고리나 검색어를 다시 확인해주세요.")
    else:
        st.success(f"총 {len(results)}건의 FAQ를 찾았습니다.")
        for _, row in results.iterrows():
            with st.expander(f"Q. {row['title']}"):
                st.markdown(f"{row['content']}")

# # ------------------ 통계 분석 ------------------
# elif menu == "통계 분석":
#     st.title("📊 통계 분석 (데이터 연결 예정)")
#     st.info("데이터가 연결되면 아래에 다양한 분석 시각화가 표시될 예정입니다.")
#     st.markdown("예시 차트 영역 (현재는 임시 데이터)")
#     df_demo = pd.DataFrame({
#         "월": pd.date_range("2025-01", periods=6, freq="M"),
#         "전기차 등록": np.random.randint(500, 2000, size=6)
#     })
#     st.bar_chart(df_demo.set_index("월"))
#     st.warning("🚧 이 영역은 추후 통계 분석 자료와 연동됩니다.")



elif menu == "종료":
    st.title("👋 앱 종료 안내")
    st.info("""
        이 Streamlit 애플리케이션을 종료하려면,
        앱을 실행한 **터미널(명령 프롬프트) 창**으로 돌아가서
        `Ctrl + C` 키를 누르세요.
        """)
    st.warning("브라우저 탭을 닫는다고 해서 앱 서버가 종료되는 것은 아닙니다.")


