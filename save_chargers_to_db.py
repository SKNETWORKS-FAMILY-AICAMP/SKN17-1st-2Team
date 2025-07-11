import requests
import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import unquote

# --- MySQL 데이터베이스 연결 정보
db_config = {
    'host': 'localhost',
    'user': 'sehee',
    'password': 'sehee',
    'database': 'project1db' 
}

def create_table_if_not_exists(cursor):
    """충전소 정보를 저장할 테이블이 없으면 생성하는 함수 (개선된 스키마)"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS chargers (
        unique_id VARCHAR(30) PRIMARY KEY,  -- statId와 chgerId를 조합한 고유 ID
        station_id VARCHAR(20),
        charger_id VARCHAR(10),
        station_name VARCHAR(100),
        charger_type VARCHAR(50),
        address VARCHAR(255),
        lat DECIMAL(10, 8),
        lng DECIMAL(11, 8),
        use_time VARCHAR(100),
        operator_name VARCHAR(100), -- 운영기관명
        status VARCHAR(50),
        power_output INT, -- 충전용량(kW)
        parking_free CHAR(1), -- 주차비 무료 여부 (Y/N)
        last_update_dt DATETIME -- 최종 충전기 상태 변경 시각
    ) CHARSET=utf8mb4
    """
    try:
        cursor.execute(create_table_query)
        print("'chargers' 테이블 확인 및 준비 완료 (스키마 업데이트됨).")
    except Error as e:
        print(f"테이블 생성 중 오류 발생: {e}")
        raise

def fetch_charger_data(page_no):
    """API로부터 특정 페이지의 충전소 정보를 가져오는 함수"""
    url = 'http://apis.data.go.kr/B552584/EvCharger/getChargerInfo'

    service_key_encoded = '' # 키값 입력
    service_key_decoded = unquote(service_key_encoded)
    
    params ={
        'serviceKey' : service_key_decoded,
        'pageNo' : page_no,
        'numOfRows' : '9999' # 한 페이지에 가져올 최대 데이터 수
    }
    
    try:
        print(f"{page_no}페이지 데이터 요청 중...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        print(f"API로부터 {page_no}페이지 데이터를 성공적으로 가져왔습니다.")
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생 (페이지: {page_no}): {e}")
        return None

def parse_and_insert_data(xml_data, cursor, conn):
    """XML 데이터를 파싱하여 DB에 저장하고, 처리된 데이터 수를 반환하는 함수"""
    if not xml_data:
        return 0

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"XML 파싱 오류: {e}")
        return 0
        
    items = root.findall('./body/items/item')
    
    if not items:
        print("API 응답에서 충전소 정보를 찾을 수 없습니다.")
        result_msg = root.find('./header/resultMsg')
        if result_msg is not None:
            print(f"API 메시지: {result_msg.text}")
        return 0

    insert_query = """
    INSERT INTO chargers (unique_id, station_id, charger_id, station_name, charger_type, address, lat, lng, use_time, operator_name, status, power_output, parking_free, last_update_dt)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        station_name=VALUES(station_name), charger_type=VALUES(charger_type), address=VALUES(address), lat=VALUES(lat), lng=VALUES(lng), 
        use_time=VALUES(use_time), operator_name=VALUES(operator_name), status=VALUES(status), power_output=VALUES(power_output), 
        parking_free=VALUES(parking_free), last_update_dt=VALUES(last_update_dt)
    """
    
    chargers_to_insert = []
    for item in items:
        try:
            stat_id = item.findtext('statId')
            chger_id = item.findtext('chgerId')
            if not stat_id or not chger_id:
                print("필수 정보(statId, chgerId)가 없는 항목을 건너뜁니다.")
                continue
            
            unique_id = f"{stat_id}-{chger_id}"
            
            output_text = item.findtext('output')
            power_output = int(float(output_text)) if output_text and output_text.replace('.', '', 1).isdigit() else 0

            update_dt_str = item.findtext('statUpdDt')
            update_dt_obj = None
            if update_dt_str:
                try:
                    update_dt_obj = datetime.strptime(update_dt_str, '%Y%m%d%H%M%S')
                except ValueError:
                    # print(f"잘못된 날짜 형식 (statId: {stat_id}), NULL로 처리합니다: {update_dt_str}")
                    pass

            chargers_to_insert.append((
                unique_id,
                stat_id,
                chger_id,
                item.findtext('statNm'),
                item.findtext('chgerType'),
                item.findtext('addr'),
                float(item.findtext('lat', 0)),
                float(item.findtext('lng', 0)),
                item.findtext('useTime'),
                item.findtext('busiNm'),
                item.findtext('stat'),
                power_output,
                item.findtext('parkingFree'),
                update_dt_obj
            ))
        except (TypeError, ValueError) as e:
            print(f"데이터 파싱 오류 (statId: {item.findtext('statId')}), 건너뜁니다: {e}")

    if not chargers_to_insert:
        return 0

    try:
        cursor.executemany(insert_query, chargers_to_insert)
        conn.commit()
        print(f"{cursor.rowcount}개의 충전소 정보가 데이터베이스에 저장/업데이트되었습니다.")
        return cursor.rowcount
    except Error as e:
        print(f"데이터 삽입 중 오류 발생: {e}")
        conn.rollback()
        raise

def main():
    """메인 실행 함수: 1페이지부터 10페이지까지 데이터를 가져와 처리"""
    conn = None
    total_processed_count = 0
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            cursor = conn.cursor()
            create_table_if_not_exists(cursor)
            
            # 1페이지부터 10페이지까지 반복
            for page_no in range(1, 11):
                print(f"--- 페이지 {page_no} 처리 시작 ---")
                xml_data = fetch_charger_data(page_no)
                if xml_data:
                    processed_count = parse_and_insert_data(xml_data, cursor, conn)
                    total_processed_count += processed_count
                print(f"--- 페이지 {page_no} 처리 완료 ---")

            print(f"총 {total_processed_count}개의 충전소 정보가 최종적으로 데이터베이스에 저장/업데이트되었습니다.")
            
    except Error as e:
        print(f"데이터베이스 작업 중 오류 발생: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()
