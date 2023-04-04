TALLI notice bot

private라 위키가 없어서 여기다 작성할게용ㅎㅎ  
일단 최대한 싹 다 추출하겠습니다.  

# 사람인 크롤링  
**키워드**  
1. CRA  
2. CRC  
3. 연구간호사  
4. 보건관리자  
5. 보험심사  
6. 메디컬라이터  

**수집 항목**   
- URL  
- 기업명  
- 스크랩 수   
- 공고명  
- 경력  
- 학력  
- 근무형태  
- 급여  
- 근무일시  

**없는 경우 있음**   
- 근무지역  
- 필수사항  
- 우대사항  

- 접수 시작일  
  
  
**없는 경우 있음**   
- 접수 마감일

## URL 파악  
처음에 채용 페이지가 [1, 2, 3] 같은 식이 아닌 "더보기"로 되어 있어서   더보기를 실행한 주소를 기준으로 진행함  
기본 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword=CRA&recruitPage=1&recruitSort=relation  
zf_user: 로그인 안 한 상태를 의미하는 것 같음  
search: 검색 쿼리  
* searchword: 검색할 단어 -> searchword=CRA  
* recruitPageCount: 한 페이지에 보여줄 채용 공고 개수 ->  recruitPageCount=40  
* recruitPage: 검색 결과 페이지 번호 -> recruitPage=1  
* recruitSort: 검색 결과 정렬 -> recruitSort=relation  
수집이 목표니까 필요 없어 보임  

기준 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword={키워드}&recruitPage={페이지}  
EX) https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword=CRA&recruitPage=1  

https://www.saramin.co.kr/zf_user/jobs/relay/view?...  
채용 공고 링크로 들어갔을 때 relay가 있어서 필요 없는 공고가 보여서 delay를 지운 링크로 진행함  

## 배운 점 . 
BeautifulSoup로는 로딩이 끝나지 않은 요소들은 가져올 수 없다.  
EX) 552건 검색 완료라고 나와야 하는데, ...건 검색 완료로 저장됨  

<li><span>전공</span>의/약학, 생명과학, 간호학</li>   
같은 경우 li.text의 결과가 "학, 생명과학, 간호학"이 아니라 
"전공의/약학, 생명과학, 간호학"임. 추가로 처리 필요가 필요함  

가끔 \xao 문자가 들어오는데, non-breaking space(Latin1,chr(160) 인코딩 형)라고 한다.  
단순하게 replace('\\xa0', ' ') 방식으로 지울 수 있다.  
