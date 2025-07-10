import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
from mysql.connector import Error

# --- MySQL 연결 설정 ---
db_config = {
    'host': 'localhost',
    'user': 'sehee',
    'password': 'sehee',
    'database': 'project1db' 
}

# --- 크롤링 설정 ---
FRONTIER_FORD_FAQ_URL = "https://www.frontierford.com/faq/ford-electric-lineup.htm?srsltid=AfmBOooBqN_a6WwQzWidD_fI7v7RV0FVtLepfbByBUO7VGRhPYe_fvdT"
CHROME_DRIVER_PATH = 'chromedriver.exe'
TOTAL_FAQ_ITEMS = 9 

def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    try:
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        print("사용자 지정 경로로 ChromeDriver를 시작합니다.")
    except Exception as e:
        print(f"사용자 지정 경로로 ChromeDriver 시작 실패: {e}. webdriver_manager를 사용합니다.")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    return driver

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("페이지 끝까지 스크롤 완료.")

def setup_database():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS ford_faq (
            faq_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(512) NOT NULL,
            content TEXT NOT NULL,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"MySQL 데이터베이스 '{db_config['database']}' 연결 및 'ford_faq' 테이블 설정 완료.")
        return conn, cursor
    except Error as err:
        print(f"MySQL 오류 발생: {err}")
        return None, None

def insert_data_to_db(cursor, conn, data):
    insert_query = "INSERT INTO ford_faq (title, content) VALUES (%s, %s)"
    try:
        cursor.execute(insert_query, (data['title'], data['content']))
        conn.commit()
        print(f"DB에 데이터 삽입 완료: {data['title'][:30]}...")
    except Error as err:
        print(f"DB 데이터 삽입 오류 발생: {err}")
        conn.rollback()

def crawl_ford_faq():
    driver = None
    conn = None
    cursor = None

    try:
        driver = setup_webdriver()
        driver.get(FRONTIER_FORD_FAQ_URL)
        time.sleep(5)

        scroll_to_bottom(driver)
        time.sleep(2)

        conn, cursor = setup_database()
        if not conn or not cursor:
            print("데이터베이스 설정 실패로 DB 저장 기능을 건너뜁니다.")

        # XPATH를 활용하여 질문과 답변 추출
        for i in range(1, TOTAL_FAQ_ITEMS + 1):
            question_xpath = ""
            answer_xpath = ""
            
            # FAQ 항목 번호에 따라 다른 XPATH 패턴 적용
            if 1 <= i <= 4:
                question_xpath = f'//*[ @id="page-body"]/div[2]/div[1]/div[2]/div/h2[{i}]'
                answer_xpath = f'//*[ @id="page-body"]/div[2]/div[1]/div[2]/div/p[{i}]'
            elif 5 <= i <= 9:
                relative_index = i - 4 
                question_xpath = f'//*[ @id="page-body"]/div[2]/div[1]/div[4]/div/h2[{relative_index}]'
                answer_xpath = f'//*[ @id="page-body"]/div[2]/div[1]/div[4]/div/p[{relative_index}]'
            else:
                print(f"경고: 예상치 못한 FAQ 항목 번호 {i}. 건너뜁니다.")
                continue

            try:
                question_element = driver.find_element(By.XPATH, question_xpath)
                title = question_element.text.strip()
                
                answer_element = driver.find_element(By.XPATH, answer_xpath)
                content = answer_element.text.strip()

                print(f"데이터 수집 완료 ({i}/{TOTAL_FAQ_ITEMS}): {title[:30]}...")

                if conn and cursor:
                    insert_data_to_db(cursor, conn, {'title': title, 'content': content})

            except NoSuchElementException:
                print(f"경고: {i}번째 질문 또는 답변 요소를 찾을 수 없습니다. (질문 XPATH: {question_xpath}, 답변 XPATH: {answer_xpath}). 다음으로 넘어갑니다.")
                continue
            except Exception as e:
                print(f"오류: {i}번째 FAQ 처리 중 예상치 못한 오류 발생: {e}")
                continue

    except TimeoutException:
        print("오류: 페이지 로딩 시간이 초과되었습니다.")
    except Exception as e:
        print(f"크롤링 중 전반적인 오류 발생: {e}")
    finally:
        if driver:
            driver.quit()
            print("웹 드라이버 종료.")
        
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("MySQL 연결 종료.")

if __name__ == "__main__":
    crawl_ford_faq()