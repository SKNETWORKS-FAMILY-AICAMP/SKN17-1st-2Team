import time 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.chrome.service import Service 
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException 
from webdriver_manager.chrome import ChromeDriverManager 
import mysql.connector 
from mysql.connector import Error 

# MySQL 연결 설정 
db_config = { 
    'host': 'localhost', 
    'user': 'sehee', 
    'password': 'sehee', 
    'database': 'project1db'  
} 

# --- 설정 --- 
KIA_FAQ_URL = "https://www.kia.com/kr/customer-service/center/faq" 

def setup_webdriver(): 
    options = webdriver.ChromeOptions() 
    options.add_argument("--start-maximized") 
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) 

    try: 
        service = Service(ChromeDriverManager().install()) 
        driver = webdriver.Chrome(service=service, options=options) 
        print("ChromeDriver를 시작했습니다.")
    except Exception as e: 
        print(f"오류: ChromeDriver 시작 실패: {e}")
        raise # 드라이버 시작 실패 시 예외 발생

    return driver 

def scroll_to_bottom(driver): 
    last_height = driver.execute_script("return document.body.scrollHeight") 
    while True: 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
        time.sleep(2) 
        new_height = driver.execute_script("return document.body.scrollHeight") 
        if new_height == last_height: 
            break 
        last_height = new_height 
    print("페이지 끝까지 스크롤 완료.") 

def insert_faq_to_db(keyword, title, content):
    """
    FAQ 데이터를 MySQL 데이터베이스에 삽입합니다. 중복을 확인합니다.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 데이터 중복 방지 (keyword, title, content가 동일한 경우)
            select_query = "SELECT COUNT(*) FROM kia_faq WHERE keyword = %s AND title = %s AND content = %s"
            cursor.execute(select_query, (keyword, title, content))
            if cursor.fetchone()[0] > 0:
                print(f"데이터베이스에 이미 존재하는 FAQ: {keyword} - {title[:30]}...")
                return

            insert_query = "INSERT INTO kia_faq (keyword, title, content) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (keyword, title, content))
            connection.commit()
            print(f"데이터베이스에 FAQ 저장 완료 (검색어: {keyword}, 제목: {title[:30]}...)")
    except Error as e:
        print(f"MySQL 데이터베이스에 데이터 삽입 중 오류 발생: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

def crawl_kia_faq_for_keyword(keyword, driver): 
    print(f"\n--- 검색어 '{keyword}' FAQ 크롤링 시작 ---")
    driver.get(KIA_FAQ_URL) 
    time.sleep(3) 

    search_input_xpath = '//*[@id="searchName"]' 
    try: 
        search_input = driver.find_element(By.XPATH, search_input_xpath) 
        search_input.clear() # 이전 검색어 지우기
        search_input.send_keys(keyword) 
        search_input.send_keys(Keys.ENTER) 
        print(f"검색어 '{keyword}' 입력 및 엔터.") 
        time.sleep(5) 
    except NoSuchElementException: 
        print(f"오류: 검색창 '{search_input_xpath}'를 찾을 수 없습니다. 키워드: {keyword}") 
        return 

    scroll_to_bottom(driver) 
    time.sleep(3) 

    question_buttons_xpath = '//*[starts-with(@id, "accordion-item-") and contains(@id, "-button")]' 
    
    retries = 3 
    for attempt in range(retries): 
        try: 
            question_elements = driver.find_elements(By.XPATH, question_buttons_xpath) 
            total_questions = len(question_elements) 
            print(f"총 {total_questions}개의 질문 요소를 찾았습니다 (검색어: {keyword}).") 

            if total_questions == 0: 
                print(f"경고: '{keyword}' 검색 후 질문 항목을 찾을 수 없습니다.") 
                break 

            for i in range(total_questions): 
                current_button_id = f"accordion-item-{i}-button" 
                current_panel_id = f"accordion-item-{i}-panel" 
                
                try: 
                    question_button = driver.find_element(By.ID, current_button_id) 
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", question_button) 
                    time.sleep(0.5) 
                    
                    if question_button.get_attribute("aria-expanded") == "false":
                        question_button.click() 
                        time.sleep(1) 

                    title = question_button.text.strip() 
                    answer_panel = driver.find_element(By.ID, current_panel_id) 
                    content = answer_panel.text.strip() 

                    insert_faq_to_db(keyword, title, content)
                    
                except NoSuchElementException: 
                    print(f"경고: {i}번째 질문 또는 답변 요소를 찾을 수 없습니다 (ID: {current_button_id}).") 
                    continue 
                except StaleElementReferenceException: 
                    print(f"경고: {i}번째 질문 버튼이 오래된 요소가 되었습니다. 재시도 또는 건너뜁니다.") 
                    continue 
                except Exception as e: 
                    print(f"오류: {i}번째 질문 처리 중 예상치 못한 오류 발생: {e}") 
                    continue 
            
            break 

        except StaleElementReferenceException: 
            print(f"경고: 질문 목록 요소가 오래된 참조가 되었습니다. {attempt + 1}/{retries}회 재시도합니다.") 
            driver.refresh() 
            time.sleep(5) 
            scroll_to_bottom(driver) 
            time.sleep(3) 
            if attempt == retries - 1: 
                print(f"오류: {retries}회 재시도 후에도 질문 목록을 가져올 수 없습니다.") 
                return 
        except NoSuchElementException: 
            print(f"오류: 질문 제목 XPATH '{question_buttons_xpath}'에 해당하는 요소를 찾을 수 없습니다. 키워드: {keyword}") 
            return 
        except Exception as e: 
            print(f"오류: 질문 목록 처리 중 전반적인 오류 발생: {e}") 
            return 

def main_crawler():
    driver = None
    search_keywords = ["전기차", "하이브리드"] 

    try:
        driver = setup_webdriver()
        
        for keyword in search_keywords:
            crawl_kia_faq_for_keyword(keyword, driver)

    except TimeoutException: 
        print("오류: 페이지 로딩 시간이 초과되었습니다.") 
    except Exception as e: 
        print(f"크롤링 중 전반적인 오류 발생: {e}") 
    finally: 
        if driver: 
            driver.quit() 
        print("\n모든 크롤링 작업 완료.")

if __name__ == "__main__": 
    main_crawler()
