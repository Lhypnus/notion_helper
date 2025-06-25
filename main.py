import os
from notion_client import Client
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Flask 애플리케이션 생성
app = Flask(__name__)

# .env 파일에서 환경 변수 로드
load_dotenv()

# .env 파일에서 값 가져오기
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

# 데이터베이스 이름과 ID를 매핑하는 딕셔너리 생성
DATABASE_MAPPING = {
    "ileen": os.getenv("NOTION_ILEEN_DATABASE_ID"),
    "charlotte": os.getenv("NOTION_CHARLOTTE_DATABASE_ID"),
    "lucy": os.getenv("NOTION_LUCY_DATABASE_ID"),
    "momoi": os.getenv("NOTION_MOMOI_DATABASE_ID"),
}

# Notion 클라이언트 초기화
notion = Client(auth=NOTION_API_KEY)


def create_notion_pages(db_id, count=1):
    """
    지정된 데이터베이스 ID에 다음 순번을 찾아 지정된 개수(count)만큼 새 페이지를 생성합니다.
    """
    try:
        # '순번' 속성을 기준으로 내림차순 정렬하여 가장 큰 값 1개만 가져옵니다.
        response = notion.databases.query(
            database_id=db_id,
            sorts=[{"property": "순번", "direction": "descending"}],
            page_size=1
        )

        next_number = 1
        if response["results"]:
            highest_number = response["results"][0]["properties"]["순번"]["number"]
            next_number = highest_number + 1

        # 지정된 count 만큼 페이지 생성 반복
        for i in range(count):
            current_page_number = next_number + i
            notion.pages.create(
                parent={"database_id": db_id},
                properties={
                    "구매자": {"title": [{"text": {"content": ""}}]}, # '제목' 속성 이름이 모두 '구매자'라고 가정
                    "순번": {"number": current_page_number}
                }
            )
        
        return {"success": True, "message": f"성공! '순번' 시작 번호 {next_number}부터 {count}개의 새 페이지를 생성했습니다."}

    except Exception as e:
        return {"success": False, "message": f"오류가 발생했습니다: {str(e)}"}


@app.route("/create-page", methods=['GET'])
def trigger_creation():
    """
    웹 요청을 받아 Notion 페이지 생성을 트리거하는 엔드포인트.
    URL 파라미터로 'db'와 'count'를 받아 생성할 DB와 페이지 수를 결정합니다.
    """
    # 1. 대상 데이터베이스 결정
    db_name = request.args.get('db', 'ileen').lower() # 'db' 파라미터가 없으면 'ileen'을 기본값으로 사용
    database_id = DATABASE_MAPPING.get(db_name)

    if not database_id:
        return jsonify({"success": False, "message": f"'{db_name}'에 해당하는 데이터베이스를 찾을 수 없습니다."}), 404

    # 2. 생성할 페이지 수 결정
    try:
        count = int(request.args.get('count', 1))
    except (ValueError, TypeError):
        count = 1
    
    if count > 100:
        return jsonify({"success": False, "message": "한 번에 100개를 초과하여 생성할 수 없습니다."}), 400

    # 3. 페이지 생성 함수 호출
    result = create_notion_pages(database_id, count)

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)