import requests
from bs4 import BeautifulSoup
import time

# 검색 키워드 목록
keywords = ["보훈", "피해 장병", "군대", "복지", "군 병원", "군 사건사고"]

# 결과를 저장할 파일
output_file = "crawling.txt"

# 기본 URL
base_url = "https://search.naver.com/search.naver?where=news&query="

def fetch_news(keyword, page):
    url = f"{base_url}{keyword}&start={(page - 1) * 10 + 1}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_news(html):
    soup = BeautifulSoup(html, 'html.parser')
    news_list = []
    news_items = soup.select('ul.list_news._infinite_list > li.bx')

    for item in news_items:
        title_tag = item.select_one('div.news_wrap.api_ani_send div.news_area div.news_contents a.news_tit')
        if title_tag:
            title = title_tag.get('title')
            link = title_tag.get('href')
            press_tag = item.select_one('div.info_group > a')
            press = press_tag.text.strip() if press_tag else None
            if title and link and press:
                # 큰 따옴표와 작은 따옴표 제거
                title = title.replace('"', '').replace("'", "")

                # ...뉴스사 "선정" 삭제
                press = press.replace(" 선정", "")
                news_list.append((title, link, press))
    return news_list

def save_to_file(news_items, keyword, page):
    # 파일 비우기 및 저장
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"{keyword} / {page}페이지\n\n")
        for title, link, press in news_items:
            f.write(f"제목 : {title}\n링크 : {link}\n언론사 : {press}\n\n")
        f.write("------------------------------------------------------\n\n")
def main():
    # 크롤링하기 전에 파일을 비우기
    open(output_file, 'w').close()  # 파일 비우기

    for keyword in keywords:
        print(f"Fetching news for keyword: {keyword}")
        for page in range(1, 3):                    # (n, m)일 때, 최대 m-1페이지
            all_news = []
            html = fetch_news(keyword, page)        # 뉴스 검색
            news_items = parse_news(html)           # 크롤링
            all_news.extend(news_items)             # 크롤링 결과 리스트로 저장
            save_to_file(all_news, keyword, page)   # txt 파일로 저장
            time.sleep(1)


    print(f"\n크롤링 결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()
