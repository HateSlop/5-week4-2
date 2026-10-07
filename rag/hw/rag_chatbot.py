import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. 저장된 DB 및 컬렉션 로드
dbclient = chromadb.PersistentClient(path="./chroma_db")
collection = dbclient.get_collection("community_faq")


def get_embedding(text, model="text-embedding-3-large"):
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


# 2. 유사 문서 검색
def retrieve(query, top_k=3):
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding], n_results=top_k
    )
    return results


# 3. Context 주입 및 FAQ 응답 생성
def generate_faq_answer(user_query):
    results = retrieve(user_query, top_k=3)
    found_docs = results["documents"][0]
    found_metadatas = results["metadatas"][0]

    # 검색 결과가 없는 경우 처리
    if not found_docs:
        return "확실치 않음: 관련된 원천 데이터를 찾지 못했습니다."

    context_elements = []
    for doc, meta in zip(found_docs, found_metadatas):
        context_elements.append(
            f"[출처: {meta.get('title')} | 링크: {meta.get('link')}]\n{doc}"
        )
    context_str = "\n\n".join(context_elements)

    system_prompt = """
    당신은 수집된 디시인사이드 게시글 데이터를 바탕으로 답변하는 FAQ 어시스턴트입니다.
    다음 원칙을 반드시 지키세요:
    1. 제공된 문서에 명시된 정보만 바탕으로 답변을 작성하세요.
    2. 문서 내용으로 판단할 수 없거나 불확실한 경우, "확실치 않음"이라고 명확히 밝히세요.
    3. 답변 끝에는 인용된 출처(게시글 제목과 링크)를 정리하여 제시해 주세요.
    """

    user_prompt = f"참고자료:\n{context_str}\n\n질문: {user_query}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # 테스트 실행
    query = "8화 리뷰 게스트로 누구 부를 것 같아?"
    print("=== FAQ 챗봇 응답 ===")
    print(generate_faq_answer(query))