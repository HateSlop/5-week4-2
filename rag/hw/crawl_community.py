import time
import json
import requests
from bs4 import BeautifulSoup

# 디시인사이드 더 커뮤니티2 마이너 갤러리 검색 URL (키워드: 8화)
url = "https://gall.dcinside.com/mgallery/board/lists/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

params = {
    "id": "community2",
    "s_type": "search_subject_memo",  # 제목+내용 검색
    "s_keyword": "8화",
    "page": 1
}

documents = []

print("=== [디시인사이드] 더 커뮤니티 시즌2 '8화' 반응 크롤링 시작 ===")

for page in range(1, 4):  # 1~3페이지 수집
    params["page"] = page
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 게시글 목록 추출
    rows = soup.select("tr.ub-content.us-post")
    
    for row in rows:
        try:
            # 공지글 및 일반글 구분
            title_tag = row.select_one("td.gall_tit > a:nth-child(1)")
            reply_tag = row.select_one("span.reply_num")  # 댓글 수
            
            if title_tag:
                title = title_tag.text.strip()
                link = "https://gall.dcinside.com" + title_tag["href"]
                reply_count = reply_tag.text.strip() if reply_tag else "[0]"
                
                # 8화 관련 글만 2차 정제
                if "8화" in title or "8" in title:
                    documents.append({
                        "id": f"dc_8ep_{len(documents) + 1}",
                        "title": title,
                        "reply_count": reply_count,
                        "link": link,
                        "content": f"제목: {title} (댓글: {reply_count})"
                    })
        except AttributeError:
            continue
            
    print(f"[{page}페이지 완료] 누적 {len(documents)}건 수집됨")
    time.sleep(0.8)  # 디시 차단 방지 간격 설정

# 수집 데이터 JSON 저장
with open("community2_ep8_reactions.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)

print("\n🎉 community2_ep8_reactions.json 저장 완료!")