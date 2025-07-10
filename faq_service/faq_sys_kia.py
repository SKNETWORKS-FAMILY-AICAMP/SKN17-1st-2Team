import time 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.chrome.service import Service 
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException 
from webdriver_manager.chrome import ChromeDriverManager 
import json 
import mysql.connector 
from mysql.connector import Error 


db_config = { 
    'host': 'localhost', 
    'user': 'sehee', 
    'password': 'sehee', 
    'database': 'project1db'  
} 


# --- 설정 --- 
KIA_FAQ_URL = "https://www.kia.com/kr/customer-service/center/faq" 
CHROME_DRIVER_PATH = "chromedriver.exe" 

def setup_webdriver(): 
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
    last_height = driver.execute_script("return document.body.scrollHeight") 
    while True: 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
        time.sleep(2) 
        new_height = driver.execute_script("return document.body.scrollHeight") 
        if new_height == last_height: 
            break 
        last_height = new_height 
    print("페이지 끝까지 스크롤 완료.") 

def save_to_json_file(data, filename):
    try: 
        with open(filename, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=4) 
        print(f"크롤링 데이터가 '{filename}' 파일에 저장되었습니다.") 
    except Exception as e: 
        print(f"JSON 파일 저장 중 오류 발생: {e}") 

def crawl_kia_faq_for_keyword(keyword, driver): 
    faq_data = [] 
    
    print(f"\n--- 검색어 '{keyword}' FAQ 크롤링 시작 ---")
    driver.get(KIA_FAQ_URL) 
    time.sleep(3) 

   
    search_input_xpath = '//*[@id="searchName"]' 
    try: 
        search_input = driver.find_element(By.XPATH, search_input_xpath) 
        search_input.clear() 
        search_input.send_keys(keyword) 
        search_input.send_keys(Keys.ENTER) 
        print(f"검색어 '{keyword}' 입력 및 엔터.") 
        time.sleep(5) 
    except NoSuchElementException: 
        print(f"오류: 검색창 '{search_input_xpath}'를 찾을 수 없습니다.") 
        return [] 

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

                    faq_data.append({'title': title, 'content': content}) 
                    print(f"데이터 수집 완료 ({len(faq_data)}/{total_questions}): {title[:30]}...") 
                    
                except NoSuchElementException: 
                    print(f"경고: {i}번째 질문 또는 답변 요소를 찾을 수 없습니다 (ID: {current_button_id}).") 
                    continue 
                except StaleElementReferenceException: 
                    print(f"경고: {i}번째 질문 버튼이 오래된 요소가 되었습니다. 다음으로 넘어갑니다.") 
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
                return [] 
        except NoSuchElementException: 
            print(f"오류: 질문 제목 XPATH '{question_buttons_xpath}'에 해당하는 요소를 찾을 수 없습니다.") 
            return [] 
        except Exception as e: 
            print(f"오류: 질문 목록 처리 중 전반적인 오류 발생: {e}") 
            return [] 
    
    return faq_data

def main_crawler():
    driver = None
    all_faq_data = {} 
    search_keywords = ["전기차", "하이브리드"] 

    try:
        driver = setup_webdriver()
        
        for keyword in search_keywords:
            data = crawl_kia_faq_for_keyword(keyword, driver)
            if data:
                all_faq_data[keyword] = data
               
                save_to_json_file(data, f"kia_faq_data_{keyword}.json")
            else:
                print(f"검색어 '{keyword}'에 대한 데이터를 찾지 못했습니다.")

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
