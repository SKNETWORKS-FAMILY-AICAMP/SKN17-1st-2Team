import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime


# Streamlit의 secrets.toml에 설정된 DB 연결 정보를 사용해 연결 객체를 생성합니다.
# 이 연결은 캐싱되어 성능을 최적화합니다.
conn = st.connection(
    "mysql",
    type="sql",
    dialect="mysql",
    host="localhost",
    database="project1db",
    username="sehee",
    password="sehee"
)

# 페이지 설정
st.set_page_config(page_title="전기차 통계 대시보드", layout="wide")


@st.cache_data
def load_new_reg_data():
    # e_car 테이블과 regi 테이블을 조인하여 신규 차량 등록 데이터를 가져옵니다.
    query = """
    SELECT
        r.r_name AS Sido,
        ec.e_year AS Year,
        ec.e_ener AS CarType,
        ec.e_new AS RegisteredCount
    FROM
        e_car ec
    JOIN
        regi r ON ec.r_code = r.r_code;
    """
    df = conn.query(query, ttl="1h")
    return df

@st.cache_data
def load_total_reg_data():
    # car 테이블과 regi 테이블을 조인하여 총 차량 등록 데이터를 가져옵니다.
    query = """
    SELECT
        r.r_name AS Sido,
        c.year AS Year,
        c.RegisteredCount AS TotalRegistered
    FROM
        car c
    JOIN
        regi r ON c.r_code = r.r_code;
    """
    df = conn.query(query, ttl="1h")
    return df

@st.cache_data
def load_faq_data():
    # kia_faq (한국어 FAQ) 테이블에서 데이터를 가져옵니다.
    faq_kor_query = "SELECT faq_id, title, content, key_num FROM kia_faq;"
    faq_kor = conn.query(faq_kor_query, ttl="1h")

    # ford_faq (영어 FAQ) 테이블에서 데이터를 가져옵니다.
    faq_eng_query = "SELECT faq_id, title, content, key_num FROM ford_faq;"
    faq_eng = conn.query(faq_eng_query, ttl="1h")

    # keyword 테이블에서 데이터를 가져옵니다.
    key_query = "SELECT key_num, key_name FROM keyword;"
    key = conn.query(key_query, ttl="1h")

    return faq_kor, faq_eng, key

@st.cache_data
def load_charger_data():
    # chargers 테이블에서 데이터를 가져옵니다.
    query = "SELECT unique_id, lat, lng, r_code FROM chargers;"
    df = conn.query(query, ttl="1h")
    return df

@st.cache_data
def load_regional_charger_data():
    # 지역별 충전소 수를 계산합니다.
    query = """
    SELECT
        r.r_name AS RegionName,
        r.lat AS lat,
        r.lon AS lon,
        COUNT(c.unique_id) AS ChargerCount
    FROM
        chargers c
    JOIN
        regi r ON c.r_code = r.r_code
    GROUP BY
        r.r_name, r.lat, r.lon;
    """
    df = conn.query(query, ttl="1h")
    return df

@st.cache_data
def load_shortage_analysis_data():
    # 지역별 전기차/하이브리드차 등록 대수
    car_query = """
    SELECT
        r.r_name AS RegionName,
        SUM(ec.e_new) AS TotalEVHybridCars
    FROM
        e_car ec
    JOIN
        regi r ON ec.r_code = r.r_code
    WHERE
        ec.e_ener IN ('전기', '하이브리드')
    GROUP BY
        r.r_name;
    """
    cars_df = conn.query(car_query, ttl="1h")

    # 지역별 충전소 수
    charger_query = """
    SELECT
        r.r_name AS RegionName,
        COUNT(c.unique_id) AS TotalChargers
    FROM
        chargers c
    JOIN
        regi r ON c.r_code = r.r_code
    GROUP BY
        r.r_name;
    """
    chargers_df = conn.query(charger_query, ttl="1h")

    # 데이터프레임 병합
    merged_df = pd.merge(cars_df, chargers_df, on="RegionName", how="outer").fillna(0)

    # 차량 1대당 충전소 수 계산 (충전소가 0개인 경우 무한대 처리)
    merged_df["CarsPerCharger"] = merged_df.apply(
        lambda row: row["TotalEVHybridCars"] / row["TotalChargers"] if row["TotalChargers"] > 0 else np.inf,
        axis=1
    )
    merged_df = merged_df.sort_values(by="CarsPerCharger", ascending=False)
    return merged_df

@st.cache_data
def load_ev_hybrid_new_reg_data():
    # 지역별 전기차/하이브리드차 신규 등록 대수
    ev_hybrid_query = """
    SELECT
        r.r_name AS RegionName,
        SUM(ec.e_new) AS EVHybridNewReg
    FROM
        e_car ec
    JOIN
        regi r ON ec.r_code = r.r_code
    WHERE
        ec.e_ener IN ('전기', '하이브리드')
    GROUP BY
        r.r_name;
    """
    ev_hybrid_df = conn.query(ev_hybrid_query, ttl="1h")

    ev_hybrid_df = ev_hybrid_df.sort_values(by="EVHybridNewReg", ascending=False)
    return ev_hybrid_df

# ------------------ 사이드 메뉴 ------------------
st.sidebar.title(" 메뉴")
menu = st.sidebar.radio("이동할 기능을 선택하세요", ["차량 등록 통계", "충전소 인프라", "FAQ 검색"])

# ------------------ 차량 등록 통계 ------------------
if menu == "차량 등록 통계":
    st.title("차량 등록 통계 대시보드")
    st.markdown("전기차/하이브리드차 신규 등록 및 전체 차량 대비 등록 현황을 시각화합니다.")

    analysis_type = st.selectbox("분석 유형 선택", ["연도별 신규 등록 추이", "전체 차량 대비 누적 등록 비율"])

    df_new_reg_raw = load_new_reg_data()
    df_total_reg_raw = load_total_reg_data()

    col1, col2 = st.columns(2)
    with col1:
        regions_query = "SELECT DISTINCT r_name FROM regi;"
        available_regions = conn.query(regions_query, ttl="1h")['r_name'].tolist()
        region = st.selectbox("지역 선택", ["전국"] + sorted(available_regions))
    with col2:
        cartypes_query = "SELECT DISTINCT e_ener FROM e_car;"
        available_cartypes = conn.query(cartypes_query, ttl="1h")['e_ener'].tolist()
        car_type = st.selectbox("차종", ["전체"] + sorted(available_cartypes))

    year_range = st.slider("기간 선택 (연도)", 2021, 2025, (2021, 2025), step=1)

    # Filter data based on selection
    df_new_reg = df_new_reg_raw.copy()
    df_total_reg = df_total_reg_raw.copy()

    if region != "전국":
        df_new_reg = df_new_reg[df_new_reg["Sido"] == region]
        df_total_reg = df_total_reg[df_total_reg["Sido"] == region]

    if car_type != "전체":
        df_new_reg = df_new_reg[df_new_reg["CarType"] == car_type]

    df_new_reg = df_new_reg[(df_new_reg['Year'] >= year_range[0]) & (df_new_reg['Year'] <= year_range[1])]
    df_total_reg = df_total_reg[(df_total_reg['Year'] >= year_range[0]) & (df_total_reg['Year'] <= year_range[1])]

    if analysis_type == "연도별 신규 등록 추이":
        st.subheader(f"'{region}' 지역 '{car_type}' 차량 신규 등록 대수 추이")

        yearly_sum = df_new_reg.groupby("Year")["RegisteredCount"].sum().reset_index()

        if yearly_sum.empty:
            st.warning("해당 조건에 맞는 데이터가 없습니다.")
        else:
            st.line_chart(yearly_sum.set_index("Year")["RegisteredCount"])
            total = yearly_sum["RegisteredCount"].sum()
            st.metric(label=f"기간 내 총 신규 등록 대수", value=f"{total:,.0f} 대")

            # 연평균 증가율 계산
            if len(yearly_sum) > 1:
                start_count = yearly_sum["RegisteredCount"].iloc[0]
                end_count = yearly_sum["RegisteredCount"].iloc[-1]
                num_years = len(yearly_sum) - 1
                if start_count > 0 and num_years > 0:
                    cagr = ((end_count / start_count)**(1/num_years) - 1) * 100 if num_years > 0 else 0.0
                else:
                    cagr = 0.0
            else:
                cagr = 0.0
            st.metric(label="연평균 증가율 (CAGR)", value=f"{cagr:.1f}%")

    elif analysis_type == "전체 차량 대비 누적 등록 비율":
        st.subheader(f"'{region}' 지역 '{car_type}' 차량의 전체 차량 대비 누적 등록 비율")

        # Group by year and sum new registrations
        new_reg_by_year = df_new_reg.groupby('Year')['RegisteredCount'].sum().reset_index()
        new_reg_by_year['CumulativeCount'] = new_reg_by_year['RegisteredCount'].cumsum()

        # Group by year and sum total registrations
        total_reg_by_year = df_total_reg.groupby('Year')['TotalRegistered'].sum().reset_index()

        # Merge the two dataframes
        merged_df = pd.merge(new_reg_by_year, total_reg_by_year, on="Year", how="inner")

        if merged_df.empty:
            st.warning("비교할 데이터가 없습니다. 기간이나 지역을 다시 선택해주세요.")
        else:
            # Calculate ratio
            merged_df['Ratio'] = (merged_df['CumulativeCount'] / merged_df['TotalRegistered']) * 100

            st.line_chart(merged_df.set_index("Year")["Ratio"])

            latest_year_data = merged_df.iloc[-1]
            st.metric(
                label=f"{int(latest_year_data['Year'])}년 누적 등록 대수 ({car_type})",
                value=f"{latest_year_data['CumulativeCount']:,.0f} 대"
            )
            st.metric(
                label=f"{int(latest_year_data['Year'])}년 전체 등록 대수",
                value=f"{latest_year_data['TotalRegistered']:,.0f} 대"
            )
            st.metric(
                label=f"{int(latest_year_data['Year'])}년 등록 비율",
                value=f"{latest_year_data['Ratio']:.2f}%"
            )

# ------------------ 충전소 인프라 ------------------
elif menu == "충전소 인프라":
    st.title(" 충전소 인프라 분포도")
    st.markdown("전국 충전소 위치 및 지역별 분포를 확인할 수 있습니다.")

    df_chargers = load_charger_data()
    df_regional_chargers = load_regional_charger_data()

    st.subheader("️ 지역별 충전소 분포 지도")
    if not df_regional_chargers.empty:
        fig = px.scatter_mapbox(
            df_regional_chargers,
            lat="lat",
            lon="lon",
            size="ChargerCount",
            color="ChargerCount",
            hover_name="RegionName",
            hover_data={"ChargerCount": True, "lat": False, "lon": False},
            color_continuous_scale=px.colors.sequential.Viridis,
            size_max=40,
            zoom=5.5,
            center=dict(lat=36.2, lon=127.8),
            mapbox_style="open-street-map",
            title="지역별 충전소 수"
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":40,"l":0,"b":0}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("위도 및 경도 정보가 부족하여 지도를 표시할 수 없습니다.")

    st.subheader(" 지역별 전기/하이브리드차 신규 등록 대수")
    ev_hybrid_df = load_ev_hybrid_new_reg_data()
    if not ev_hybrid_df.empty:
        st.dataframe(ev_hybrid_df)
        fig_ev_hybrid = px.bar(
            ev_hybrid_df,
            x="RegionName",
            y="EVHybridNewReg",
            title="지역별 전기/하이브리드차 신규 등록 대수",
            labels={"RegionName": "지역", "EVHybridNewReg": "신규 등록 대수"},
            color="EVHybridNewReg",
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_ev_hybrid, use_container_width=True)
    else:
        st.info("전기/하이브리드차 신규 등록 대수를 분석할 데이터가 충분하지 않습니다.")



# ------------------ FAQ 검색 ------------------
elif menu == "FAQ 검색":
    st.title("❓ 전기차 FAQ 검색 시스템")
    faq_kor, faq_eng, faq_key = load_faq_data() # DB에서 데이터 로드

    language = st.radio("언어 선택", ["한국어", "English"], horizontal=True)
    faq_df = faq_kor if language == "한국어" else faq_eng
    df_faq_merged = faq_df.merge(faq_key, on="key_num", how="left")

    # DB에서 가져온 key_name을 기반으로 카테고리 선택
    category_options = ["전체"] + sorted(df_faq_merged["key_name"].dropna().unique().tolist())
    selected_category = st.selectbox("카테고리 선택", category_options)
    query = st.text_input("궁금한 내용을 입력하세요:")

    results = df_faq_merged.copy()
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