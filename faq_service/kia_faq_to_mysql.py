import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
from mysql.connector import Error

# --- 설정 ---
# MySQL 데이터베이스 연결 정보
db_config = {
    'host': 'localhost',
    'user': 'sehee',
    'password': 'sehee',
    'database': 'project1db' 
}

KIA_FAQ_URL = "https://www.kia.com/kr/customer-service/center/faq"
CHROME_DRIVER_PATH = "chromedriver.exe"

def setup_webdriver():
    """웹 드라이버를 설정하고 반환합니다."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    try:
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"사용자 지정 경로로 ChromeDriver 시작 실패: {e}. webdriver_manager를 사용합니다.")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    return driver

def scroll_to_bottom(driver):
    """페이지 끝까지 스크롤합니다."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("페이지 끝까지 스크롤 완료.")

def save_to_mysql(faq_data, db_config):
    """크롤링한 데이터를 MySQL 데이터베이스에 저장합니다."""
    if not faq_data:
        print("저장할 데이터가 없습니다.")
        return
        
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")
            cursor = conn.cursor()

            # 테이블 생성 (없을 경우)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kia_faq (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("'kia_faq' 테이블을 확인하고, 없으면 생성했습니다.")

            # 데이터 삽입
            insert_query = "INSERT INTO kia_faq (title, content) VALUES (%s, %s)"
            data_to_insert = [(item['title'], item['content']) for item in faq_data]
            
            cursor.executemany(insert_query, data_to_insert)
            conn.commit()
            
            print(f"{cursor.rowcount}개의 FAQ 데이터가 데이터베이스에 성공적으로 저장되었습니다.")

    except Error as e:
        print(f"데이터베이스 작업 중 오류 발생: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL 연결이 닫혔습니다.")

def crawl_kia_faq():
    """기아 FAQ 페이지를 크롤링하여 데이터베이스에 저장합니다."""
    driver = None
    faq_data = []
    try:
        driver = setup_webdriver()
        driver.get(KIA_FAQ_URL)
        time.sleep(3)

        # 검색창에 '전기차' 입력 및 엔터
        search_input_xpath = '//*[@id="searchName"]'
        try:
            search_input = driver.find_element(By.XPATH, search_input_xpath)
            search_input.send_keys("전기차")
            search_input.send_keys(Keys.ENTER)
            print("검색어 '전기차' 입력 및 엔터.")
            time.sleep(5)
        except NoSuchElementException:
            print(f"오류: 검색창 '{search_input_xpath}'를 찾을 수 없습니다.")
            return

        # 페이지 끝까지 스크롤하여 모든 FAQ 항목 로드
        scroll_to_bottom(driver)
        time.sleep(3)

        # 모든 질문 제목 찾기 및 데이터 추출
        question_buttons_xpath = '//*[starts-with(@id, "accordion-item-") and contains(@id, "-button")]'
        
        retries = 3
        for attempt in range(retries):
            try:
                question_elements = driver.find_elements(By.XPATH, question_buttons_xpath)
                total_questions = len(question_elements)
                print(f"총 {total_questions}개의 질문 요소를 찾았습니다.")

                if total_questions == 0:
                    print("경고: '전기차' 검색 후 질문 항목을 찾을 수 없습니다.")
                    break

                for i in range(total_questions):
                    # 각 루프마다 요소를 다시 찾아서 StaleElementReferenceException 방지
                    try:
                        button = driver.find_element(By.ID, f"accordion-item-{i}-button")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # ElementClickInterceptedException을 피하기 위해 JavaScript 클릭 사용
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)

                        title = button.text.strip()
                        answer_panel = driver.find_element(By.ID, f"accordion-item-{i}-panel")
                        content = answer_panel.text.strip()

                        faq_data.append({'title': title, 'content': content})
                        print(f"데이터 수집 완료 ({len(faq_data)}/{total_questions}): {title[:30]}...")
                        
                    except StaleElementReferenceException:
                        print(f"경고: {i}번째 질문 버튼이 오래된 요소가 되었습니다. 다시 시도합니다.")
                        # 요소를 다시 찾기 위해 루프를 다시 시작할 수 있지만, 여기서는 다음으로 넘어갑니다.
                        continue
                    except Exception as e:
                        print(f"오류: {i}번째 질문 처리 중 예상치 못한 오류 발생: {e}")
                        continue
                
                break # 성공적으로 모든 항목을 처리했으면 재시도 루프 종료

            except StaleElementReferenceException:
                print(f"경고: 질문 목록 요소가 오래된 참조가 되었습니다. {attempt + 1}/{retries}회 재시도합니다.")
                driver.refresh()
                time.sleep(5)
                # 검색을 다시 수행해야 할 수 있음
                search_input = driver.find_element(By.XPATH, search_input_xpath)
                search_input.send_keys("전기차")
                search_input.send_keys(Keys.ENTER)
                time.sleep(5)
                scroll_to_bottom(driver)
                time.sleep(3)
                if attempt == retries - 1:
                    print(f"오류: {retries}회 재시도 후에도 질문 목록을 가져올 수 없습니다.")
                    return
            except Exception as e:
                print(f"오류: 질문 목록 처리 중 전반적인 오류 발생: {e}")
                return

    except TimeoutException:
        print("오류: 페이지 로딩 시간이 초과되었습니다.")
    except Exception as e:
        print(f"크롤링 중 전반적인 오류 발생: {e}")
    finally:
        if driver:
            driver.quit()
        
        # 크롤링이 끝나면 데이터베이스에 저장
        if faq_data:
            save_to_mysql(faq_data, db_config)

if __name__ == "__main__":
    crawl_kia_faq()
