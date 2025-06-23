import os
from notion_client import Client
from dotenv import load_dotenv
from flask import Flask, jsonify

# Flask 애플리케이션 생성
app = Flask(__name__)

# .env 파일에서 환경 변수 로드
load_dotenv()

# .env 파일에서 값 가져오기
notion_api_key = os.getenv("NOTION_API_KEY")
database_id = os.getenv("NOTION_ILEEN_DATABASE_ID")

# Notion 클라이언트 초기화
notion = Client(auth=notion_api_key)


def create_notion_page(db_id, title_property_name):
    """
    Notion 데이터베이스에서 다음 순번을 찾아 새 페이지를 생성합니다.
    """
    try:
        # '순번' 속성을 기준으로 내림차순 정렬하여 가장 큰 값 1개만 가져옵니다.
        response = notion.databases.query(
            database_id=db_id,
            sorts=[
                {
                    "property": "순번",
                    "direction": "descending",
                }
            ],
            page_size=1
        )

        next_number = 1
        if response["results"]:
            highest_number = response["results"][0]["properties"]["순번"]["number"]
            next_number = highest_number + 1

        # 새 페이지 생성
        new_page_properties = {
            title_property_name: {"title": [{"text": {"content": ""}}]},
            "순번": {"number": next_number}
        }
        notion.pages.create(
            parent={"database_id": db_id},
            properties=new_page_properties
        )
        return {"success": True, "message": f"성공! '순번'이 {next_number}인 새 페이지를 생성했습니다.", "next_number": next_number}

    except Exception as e:
        return {"success": False, "message": f"오류가 발생했습니다: {str(e)}"}


@app.route("/create-page", methods=['GET'])
def trigger_creation():
    """
    웹 요청을 받아 Notion 페이지 생성을 트리거하는 엔드포인트.
    """
    if not notion_api_key or not database_id:
        return jsonify({"success": False, "message": "서버에 API 키 또는 DB ID가 설정되지 않았습니다."}), 500

    result = create_notion_page(database_id, "구매자")

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True) 