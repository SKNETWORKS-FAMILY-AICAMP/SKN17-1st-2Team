**SK네트웍스 Family AI 캠프 17기 1차 프로젝트**

---

# 1. 팀소개

👥 팀 멤버 (개인 GitHub)

| 이름  | GitHub 계정                                    |
| ----- | ---------------------------------------------- |
| 김주서 | [@kimjuseo71](https://github.com/kimjuseo71)   |
| 성기혁 | [@venus241004](https://github.com/venus241004) |
| 이가은 | [@Leegaeune](https://github.com/Leegaeune)     |
| 임산별 | [@ImMountainStar](https://github.com/ImMountainStar) |
| 조세희 | [@SEHEE-8546](https://github.com/SEHEE-8546)   |

---

# 2. 프로젝트개요

## 💡 프로젝트 명

### 전국 친환경차 등록현황 조회시스템 및  FAQ구현 

## 🌟 프로젝트 소개

 지역별 친환경차(전기차, 하이브리드차)와 전기차차 충천소(인프라) 의 등록현황을 조회할 수 있다. 
과거 5개년치의 등록 데이터를 통해 친환경차와 인프라의 등록 추이를 확인할 수 있다. 
기아자동차와 포드 자동차의 친환경차 관련 FAQ를 확인할 수 있다.

## 🚀 프로젝트 필요성(배경)

 정부의 탄소중립 정책과 기후위기 대응에 따라 친환경차, 특히 전기차와 하이브리드차 시장이 성장하고 있다. 
하지만 현재 제공되는 차량 등록 통계는 대부분 일반 차량 기준이며, 친환경차 중에서도 전기차와 하이브리드차로 세분화된 정보는 제한적이다.
또한 친환경차 데이터와 충전소 데이터가 분산되어 있어, 지역별 친환경차 등록 현황과 인프라 분포를 통합적으로 파악하기 어렵다. 
해당 서비스를 통해 전기차·하이브리드차 등록 현황과 충전 인프라를 통합하여 시각화함으로써, 이해관계자의 전략적 의사결정을 지원한다.


## ✅ 기대효과

1. 지역기반의 전기차,하이브리드차 등록현황과 충전 인프라를 통합 제공하여, 시장세분화 및 지역별 전략 수립에 활용할 수 있다.  지역별 시장 분석 및 세분화 전략에 활용할 수 있다. 

2.  친환경 자동차 시장의 차량 종류별 등록현황 추이를 제공함으로써 급변하는 친환경차 시장의 변화를 파악할 수 있다. 

3.  소비자들이 자주 묻는 질문(FAQ)를 전기차, 하이브리드차, 내연기관차로 분류 및 조회할 수 있어 소비자의 니즈를 파악할 수 있다. 


---

## 📦 데이터 출처 목록

| 데이터 이름                           | 파일 형식 / 수집 방법 | 출처 URL |
|--------------------------------------|------------------------|----------|
| 전국 전기차 충전소 표준데이터         | API / XML              | [바로가기](https://www.data.go.kr/data/15013115/standard.do) |
| 지역별, 월별 전기차 현황정보 (통계)   | 직접 다운로드 / CSV    | [바로가기](https://www.data.go.kr/data/15039554/fileData.do) |
| 지역, 월별 차량 등록 현황 (통계)      | 직접 다운로드 / CSV    | [바로가기](https://stat.molit.go.kr/portal/cate/statView.do?hRsId=58&hFormId=5498&hSelectId=1244&hPoint=00&hAppr=1&hDivEng=&oFileName=&rFileName=&midpath=&sFormId=5498&sStyleNum=562&settingRadio=xlsx) |
| 현대자동차 홈페이지 FAQ               | Selenium 라이브러리     | [바로가기](https://www.hyundai.co.kr/main/mainRecommend) |
| 포드자동차 홈페이지 FAQ              | Selenium 라이브러리     | [바로가기](https://www.frontierford.com/faq/ford-electric-lineup.htm?srsltid=AfmBOooBqN_a6WwQzWidD_fI7v7RV0FVtLepfbByBUO7VGRhPYe_fvdT) |
| 자동차 종합정보 신규등록정보 (2024)   | API 수집                | [바로가기](https://www.stgdata.co.kr/data/15059401/openapi.do?recommendDataYn=Y) |

---

# 3. 기술스택
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white">
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white">
  <img src="https://img.shields.io/badge/Matplotlib-CB3B27?style=for-the-badge&logo=matplotlib&logoColor=white">
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/Jupyter_Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white">
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white">
</p>



---

# 4. WBS
![WBS 시각화 이미지](image/wbs_cocon.png)

---

# 5. 요구사항명세서

![WBS 시각화 이미지](image/req_cocon.png)


---


# 6. ERD

![ERD 시각화 이미지](image/erd_cocon.png)

---

# 7. 수행결과(시연 페이지)
![수행결과 이미지](image/stm1.png)
![수행결과 이미지](image/stm2.png)
![수행결과 이미지](image/stm3.png)
![수행결과 이미지](image/stm4.png)
![수행결과 이미지](image/stm5.png)
![수행결과 이미지](image/stm6.png)
![수행결과 이미지](image/stm7.png)
![수행결과 이미지](image/stm8.png)
![수행결과 이미지](image/stm9.png)
![수행결과 이미지](image/stm10.png)
![수행결과 이미지](image/stm11.png)



---

# 8. 한 줄 회고

김주서:
친환경차 등록 현황의 지역별 불균형을 분석하며 세분화된 인사이트의 중요성을 깨달았고, 시각화를 통해 복잡한 데이터 속 숨겨진 정보를 직관적으로 전달할 수 있음을 확인했습니다.

성기혁:
방대한 자동차 등록 데이터와 충전소 인프라 데이터를 정제하고 결합하는 과정이 쉽지않았지만, 각 데이터의 특성을 이해하고 처리하는 것이 결국 모델의 정확성을 좌우한다는 것을 체감했습니다. 

이가은:
다양한 친환경차 관련 FAQ를 수집하며 비정형 텍스트 데이터를 구조화하고 탐색하는 방법을 고민하면서, 사용자가 원하는 정보를 빠르게 제공하기 위한 실용적인 데이터 활용 능력을 키울 수 있었습니다.

임산별:
데이터 흐름과 시스템 아키텍처를 설계하며, 수집부터 시각화까지 모든 과정의 유기적 연결성과 효율적인 데이터베이스 설계가 최적의 성능을 좌우한다는 것을 깊이 깨달았습니다.

조세희:
충전소 인프라와 친환경차 등록 현황의 연관성 분석을 통해, 지역의 작은 데이터 변화가 전체 시장에 큰 영향을 미치며, 이러한 미묘한 특성을 반영한 분석 방식 조정이 모델의 예측력을 크게 높인다는 것을 실감했습니다.



