import requests
import base64
from datetime import datetime
from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent

# GitHub 설정
try:
    with open(BASE_DIR / 'secrets.json') as f:
        secret_data = json.load(f)
except FileNotFoundError:
    secret_data = {}
change = True

def read_txt_file():
    with open(secret_data.get('TEXT_FILE_PATH'), 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def read_html_template():
    with open(secret_data.get('TEXT_FILE_PATH'), 'r', encoding='utf-8') as f:
        template = f.read()
    return template


def update_html_file(template, content):
    # 크롤링한 텍스트 내용을 JSON 형식으로 변환
    news_items = []
    lines = content.strip().split('\n\n')
    for line in lines:
        parts = line.split('\n')
        if len(parts) >= 3:
            title = parts[0].replace("제목 : ", "").strip()
            link = parts[1].replace("링크 : ", "").strip()
            press = parts[2].replace("언론사 : ", "").strip()
            news_items.append({'title': title, 'link': link, 'press': press})

    # JSON 형식으로 변환하여 JavaScript 배열로 생성
    json_data = str(news_items).replace("'", '"')

    # 현재 날짜 및 시간 추가
    with open("timetable.txt", "r", encoding="utf-8") as f:
        latest_datetime = f.readline()

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_template = template.replace('const newsData = [];', f'const newsData = {json_data};')
    updated_template = updated_template.replace('<div class="timestamp" id="timestamp-now"></div',
                                                f'<div class="timestamp" id="timestamp-now">최신화 확인 : {current_datetime}</div>')

    if (change == True):
        updated_template = updated_template.replace('<div class="timestamp" id="timestamp"></div>',
                                                    f'<div class="timestamp" id="timestamp">최신화 : {current_datetime}</div>')
        with open("timetable.txt", "w", encoding="utf-8") as f:
            f.write(current_datetime)
    else:
        updated_template = updated_template.replace('<div class="timestamp" id="timestamp"></div>',
                                                    f'<div class="timestamp" id="timestamp">최신화 : {latest_datetime}</div>')

    return updated_template


def update_github_file(content):
    url = f"https://api.github.com/repos/{secret_data.get('REPO_OWNER')}/{secret_data.get('REPO_NAME')}/contents/{secret_data.get('HTML_FILE_PATH')}"

    # 현재 파일의 SHA 가져오기
    response = requests.get(url, headers={'Authorization': f'token {secret_data.get("GITHUB_TOKEN")}'})
    response.raise_for_status()
    sha = response.json().get('sha')

    # 파일 업데이트
    data = {
        "message": "뉴스 데이터 최신화를 위해 HTML 코드를 수정 합니다.",
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "sha": sha,
        "branch": secret_data.get("BRANCH_NAME")
    }
    response = requests.put(url, headers={'Authorization': f'token {secret_data.get("GITHUB_TOKEN")}'}, json=data)
    response.raise_for_status()
    print("HTML 파일이 GitHub에 업데이트되었습니다.")


def main():
    global change
    
    # 텍스트 파일 읽기
    content = read_txt_file()

    # HTML 템플릿 읽기
    template = read_html_template()

    #크롤링 데이터 중 추가/삭제된 부분이 있는가?
    isChange = input("Change is True(Y/N) : ")
    if (isChange.upper() == "N"):
        change = not change
        
    # HTML 파일 내용 생성
    html_content = update_html_file(template, content)

    # GitHub에 업데이트
    update_github_file(html_content)


if __name__ == "__main__":
    main()
