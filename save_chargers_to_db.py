
import requests
import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET
from datetime import datetime

# --- MySQL 데이터베이스 연결 정보 (사용자 직접 입력) ---
# 사용자의 실제 데이터베이스 정보로 이 부분을 수정해주세요.
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

def fetch_charger_data():
    """API로부터 충전소 정보를 가져오는 함수"""
    url = 'http://apis.data.go.kr/B552584/EvCharger/getChargerInfo'
    params ={
        'serviceKey' : '',
        'pageNo' : '1', 
        'numOfRows' : '9999'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("API로부터 데이터를 성공적으로 가져왔습니다.")
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return None

def parse_and_insert_data(xml_data, cursor, conn):
    """XML 데이터를 파싱하여 DB에 저장하는 함수 (날짜 변환 로직 수정)"""
    if not xml_data:
        return

    root = ET.fromstring(xml_data)
    items = root.findall('./body/items/item')
    
    if not items:
        print("API 응답에서 충전소 정보를 찾을 수 없습니다.")
        result_msg = root.find('./header/resultMsg')
        if result_msg is not None:
            print(f"API 메시지: {result_msg.text}")
        return

    # SQL에서 STR_TO_DATE 함수 제거
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
            unique_id = f"{stat_id}-{chger_id}"
            
            output_text = item.findtext('output')
            power_output = int(float(output_text)) if output_text and output_text.replace('.', '', 1).isdigit() else 0

            # 파이썬에서 직접 datetime 객체로 변환
            update_dt_str = item.findtext('statUpdDt')
            update_dt_obj = None
            if update_dt_str:
                try:
                    update_dt_obj = datetime.strptime(update_dt_str, '%Y%m%d%H%M%S')
                except ValueError:
                    print(f"잘못된 날짜 형식 (statId: {stat_id}), NULL로 처리합니다: {update_dt_str}")

            chargers_to_insert.append((
                unique_id,
                stat_id,
                chger_id,
                item.findtext('statNm'),
                item.findtext('chgerType'),
                item.findtext('addr'),
                float(item.findtext('lat')),
                float(item.findtext('lng')),
                item.findtext('useTime'),
                item.findtext('busiNm'),
                item.findtext('stat'),
                power_output,
                item.findtext('parkingFree'),
                update_dt_obj # datetime 객체 또는 None
            ))
        except (TypeError, ValueError) as e:
            print(f"데이터 파싱 오류 (statId: {item.findtext('statId')}), 건너뜁니다: {e}")

    try:
        cursor.executemany(insert_query, chargers_to_insert)
        conn.commit()
        print(f"총 {cursor.rowcount}개의 충전소 정보가 데이터베이스에 저장/업데이트되었습니다.")
    except Error as e:
        print(f"데이터 삽입 중 오류 발생: {e}")
        conn.rollback()
        raise

def main():
    """메인 실행 함수"""
    xml_data = fetch_charger_data()
    if not xml_data:
        return

    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            cursor = conn.cursor()
            create_table_if_not_exists(cursor)
            parse_and_insert_data(xml_data, cursor, conn)
            
    except Error as e:
        print(f"데이터베이스 연결 오류: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL 연결이 종료되었습니다.")

if __name__ == "__main__":
    main()