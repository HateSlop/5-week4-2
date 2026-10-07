import json
import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 1. DB 초기화
def init_db(db_path="./chroma_db"):
    dbclient = chromadb.PersistentClient(path=db_path)
    # 컬렉션 이름을 지정합니다. (챗봇 스크립트와 동일해야 함)
    collection = dbclient.create_collection(
        name="community_faq", get_or_create=True
    )
    return dbclient, collection


# 2. 임베딩 생성
def get_embedding(text, model="text-embedding-3-large"):
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


# 3. community2_ep8_reactions.json 읽어서 DB 저장
def build_faq_db(json_path="community2_ep8_reactions.json"):
    dbclient, collection = init_db("./chroma_db")

    # 파일 존재 여부 확인 후 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        # 검색 대상 텍스트 구성
        doc_text = f"제목: {item.get('title', '')}\n내용: {item.get('content', '')}"

        # 임베딩 생성
        embedding = get_embedding(doc_text)

        # Chroma DB 저장
        collection.add(
            documents=[doc_text],
            embeddings=[embedding],
            metadatas=[
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "reply_count": str(item.get("reply_count", "")),
                }
            ],
            ids=[str(item.get("id"))],
        )

    print(
        f"총 {len(data)}개의 데이터가 community_faq 컬렉션에 저장되었습니다."
    )


if __name__ == "__main__":
    # 데이터 구축 실행
    build_faq_db("community2_ep8_reactions.json")