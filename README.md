# TALLI notice bot(사람인 크롤링)

<!-- ## 기능
- 매일 22:00시에 사람인에서 임상 관련 직군 채용 공고 정보를 수집하고 bigquery에 저장합니다.
- 마감되었거나 중복인 채용 공고는 삭제하고 수정된 공고는 업데이트합니다. -->

## 기술 스택

<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/beautifulSoup-3178C6?style=for-the-badge"> <img src="https://img.shields.io/badge/slack sdk-4A154B?style=for-the-badge&logo=slack&logoColor=white"> <img src="https://img.shields.io/badge/github actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"> <img src="https://img.shields.io/badge/google cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white"> <img src="https://img.shields.io/badge/bigquery-669DF6?style=for-the-badge&logo=googlebigquery&logoColor=white">

## 사용 방법

bigquery key.json 루트 경로에 위치해야함

### python 가상환경

```
git clone https://github.com/Team-Salvador/TALLI_notice_bot.git
cd TALLI_notice_bot
echo 'SLACK_BOT_TOKEN = "슬랙봇 토큰"' >> .env
echo 'SLACK_CHANNEL_ID = "슬랙 체널 아이디"' >> .env
python3 -m venv TALLI_notice_bot
source TALLI_notice_bot/bin/activate
pip install -r requirements.txt
python3 src/main.py
```

### 도커

`docker-compose up --build`

### makefile

`make` or `make docker`

### 키워드

1. CRA
2. CRC
3. 연구간호사
4. 보건관리자
5. 보험심사
6. 메디컬라이터

### 수집 항목

- URL
- 기업명
- 스크랩 수
- 공고명
- 경력
- 학력
- 근무지역
- 필수사항
- 우대사항
- 연락처
- 근무형태
- 급여
- 근무일시
- 접수 시작일
- 접수 마감일

### URL 파악

기준 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&&recruitSort=relation&searchword={키워드}&recruitPage={페이지}

- searchword: 검색할 단어 -> searchword=CRA
- recruitPageCount: 한 페이지에 보여줄 채용 공고 개수 -> recruitPageCount=30
- recruitPage: 페이지 번호 -> recruitPage=1
- recruitSort: 정렬(관련도) -> recruitSort=relation

### 이슈였던 것들

채용 공고 링크로 들어갔을 때 relay 때문에 필요 없는 공고가 보여서 relay를 지운 링크로 진행함  
https://www.saramin.co.kr/zf_user/jobs/relay/view?...

가끔 텍스트가 없고 상세보기 버튼만 있는 경우가 있었서 추가적인 처리가 필요했음  
가끔 \xao 문자가 들어오는데, non-breaking space(Latin1,chr(160) 인코딩 형)라고 함  
단순하게 replace('\\xa0', ' ') 방식으로 처리
