import pymysql
import pandas as pd
from contextlib import contextmanager

# MySQL 데이터베이스 연결 설정
DB_CONFIG = {
    'host': '192.168.127.131',  # Ubuntu MySQL 서버의 IP 주소
    'user': 'alsgyu',           # MySQL 사용자
    'password': 'abC124577!',   # MySQL 비밀번호
    'database': 'my_database',     # MySQL 데이터베이스 이름
    'port': 3306,               # MySQL 기본 포트
    'charset': 'utf8mb4'
}

@contextmanager
def get_db_connection():
    """MySQL 데이터베이스 연결 함수"""
    connection = None
    try:
        connection = pymysql.connect(
            host='192.168.127.131',  # MySQL 서버 IP
            user='alsgyu',           # MySQL 사용자
            password='abC124577!',   # MySQL 비밀번호
            database='my_database',  # 데이터베이스 이름
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # DictCursor 설정
        )
        yield connection
    except Exception as e:
        raise Exception(f"데이터베이스 연결 실패: {e}")
    finally:
        if connection:
            connection.close()


def get_user_info(name: str):
    """DB에서 사용자 정보를 가져오는 함수"""
    query = "SELECT weight, height, age, gender, activity_level FROM user_info WHERE name = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                return result
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None


def get_allergen_risk_level(name, allergen):
    """특정 알레르기 성분의 위험 수준을 반환"""
    query = "SELECT risk_level FROM allergy_info WHERE name = %s AND allergen = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, (name, allergen))
                result = cursor.fetchone()
                return result['risk_level'] if result else None
    except Exception as e:
        print(f"Error fetching allergen risk level: {e}")
        return None


def get_allergens_risk_levels(name, allergens):
    """
    특정 사용자의 여러 알레르기 성분의 위험 수준을 반환
    name: 사용자 이름
    allergens: 알레르기 성분 리스트
    반환값: 딕셔너리 {allergen: risk_level}
    """
    if not allergens:
        return {}

    # 자리 표시자 생성 (알레르기 리스트 길이에 따라)
    placeholders = ', '.join(['%s'] * len(allergens))
    query = f"SELECT allergen, risk_level FROM allergy_info WHERE name = %s AND allergen IN ({placeholders})"

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 매개변수로 사용자 이름과 알레르기 리스트 전달
                cursor.execute(query, (name, *allergens))
                result = cursor.fetchall()
                return {row['allergen']: row['risk_level'] for row in result}
    except Exception as e:
        print(f"Error fetching allergens risk levels: {e}")
        return {}

def insert_user_info(name, weight, height, age, gender, activity_level):
    """사용자 정보를 데이터베이스에 삽입하거나 업데이트하는 함수"""
    check_query = "SELECT id FROM user_info WHERE name = %s"
    insert_query = "INSERT INTO user_info (name, weight, height, age, gender, activity_level) VALUES (%s, %s, %s, %s, %s, %s)"
    update_query = "UPDATE user_info SET weight = %s, height = %s, age = %s, gender = %s, activity_level = %s WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(check_query, (name,))
                existing = cursor.fetchone()
                if existing:
                    # 기존 사용자 정보 업데이트
                    cursor.execute(update_query, (weight, height, age, gender, activity_level, existing['id']))
                else:
                    # 새로운 사용자 정보 삽입
                    cursor.execute(insert_query, (name, weight, height, age, gender, activity_level))
                conn.commit()
    except Exception as e:
        raise Exception(f"사용자 정보 삽입/업데이트 중 오류 발생: {e}")

def insert_allergy_info(name, allergen, risk_level):
    """알레르기 정보를 데이터베이스에 삽입하거나 업데이트하는 함수"""
    check_query = "SELECT id FROM allergy_info WHERE name = %s AND allergen = %s"
    insert_query = "INSERT INTO allergy_info (name, allergen, risk_level) VALUES (%s, %s, %s)"
    update_query = "UPDATE allergy_info SET risk_level = %s WHERE id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(check_query, (name, allergen))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(update_query, (risk_level, existing['id']))
                else:
                    cursor.execute(insert_query, (name, allergen, risk_level))
                conn.commit()
    except Exception as e:
        print(f"Error inserting/updating allergy info: {e}")



def delete_allergy_info(name, allergen):
    """특정 사용자의 특정 알레르기 정보를 데이터베이스에서 삭제"""
    query = "DELETE FROM allergy_info WHERE name = %s AND allergen = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name, allergen))
                conn.commit()  # 커밋 추가
    except Exception as e:
        print(f"Error deleting allergy info: {e}")


def get_allergy_info_grouped(name):
    """특정 사용자의 알레르기 정보를 위험도 그룹별로 분류하여 조회"""
    query = "SELECT allergen, risk_level FROM allergy_info WHERE name = %s ORDER BY risk_level"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name,))
                result = cursor.fetchall()
                if not result:  # result가 None 또는 비어 있을 경우
                    return {
                        "High Risk Group": pd.DataFrame(),
                        "Risk Group": pd.DataFrame(),
                        "Caution Group": pd.DataFrame()
                    }

                df = pd.DataFrame(result)
                grouped = {
                    "High Risk Group": df[df['risk_level'] == 'High Risk Group'],
                    "Risk Group": df[df['risk_level'] == 'Risk Group'],
                    "Caution Group": df[df['risk_level'] == 'Caution Group']
                }
                return grouped
    except Exception as e:
        print(f"Error fetching grouped allergy info: {e}")
        return {
            "High Risk Group": pd.DataFrame(),
            "Risk Group": pd.DataFrame(),
            "Caution Group": pd.DataFrame()
        }

