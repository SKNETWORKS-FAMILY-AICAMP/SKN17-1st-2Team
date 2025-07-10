
import streamlit as st
import pandas as pd
import os
import altair as alt

# CSV 경로 설정
DATA_DIR = r"C:\python_basic\Project"

@st.cache_data
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path, parse_dates=['RegistrationMonth'])

# 페이지 설정
st.set_page_config(page_title="자동차 등록 추세 대시보드", layout="wide")
st.title("🚗 월별 차량 등록 통계 대시보드")

# 데이터 로딩
df = load_csv("Monthly_Registration_Summary.csv")

# 전체 등록 추세
with st.expander("📈 월별 등록 추세 보기", expanded=True):
    st.subheader("🗓️ 월별 총 등록 대수 추이")

    monthly_total = (
        df.groupby("RegistrationMonth")["RegisteredCount"]
        .sum()
        .reset_index()
        .sort_values("RegistrationMonth")
    )

    chart = alt.Chart(monthly_total).mark_line(point=True).encode(
        x=alt.X("RegistrationMonth:T", title="등록월"),
        y=alt.Y("RegisteredCount:Q", title="등록대수", scale=alt.Scale(zero=False)),
        tooltip=["RegistrationMonth", "RegisteredCount"]
    ).properties(width="container", height=350).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.subheader("🚘 차량유형별 등록 추이")
    monthly_by_type = (
        df.groupby(["RegistrationMonth", "VehicleType"])["RegisteredCount"]
        .sum()
        .reset_index()
    )

    chart_by_type = alt.Chart(monthly_by_type).mark_line(point=True).encode(
        x=alt.X("RegistrationMonth:T", title="등록월"),
        y=alt.Y("RegisteredCount:Q", title="등록대수", scale=alt.Scale(zero=False)),
        color="VehicleType:N",
        tooltip=["RegistrationMonth", "VehicleType", "RegisteredCount"]
    ).properties(width="container", height=350).interactive()

    st.altair_chart(chart_by_type, use_container_width=True)

# 지역별 등록 상위 TOP 10
with st.expander("🏙️ 지역별 등록 규모", expanded=False):
    st.subheader("📌 지역별 전체 등록 대수 (TOP 10)")
    top_regions = (
        df.groupby(["Sido", "Sigungu"])["RegisteredCount"]
        .sum()
        .reset_index()
        .sort_values("RegisteredCount", ascending=False)
        .head(10)
    )
    top_regions["지역"] = top_regions["Sido"] + " " + top_regions["Sigungu"]

    chart_bar = alt.Chart(top_regions).mark_bar().encode(
        x=alt.X("지역:N", sort="-y", title="지역"),
        y=alt.Y("RegisteredCount:Q", title="등록대수"),
        tooltip=["지역", "RegisteredCount"]
    ).properties(width="container", height=350)

    st.altair_chart(chart_bar, use_container_width=True)
