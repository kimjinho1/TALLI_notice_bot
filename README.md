TALLI notice bot

private라 위키가 없어서 여기다 작성할게용ㅎㅎ  

## 사람인 크롤링  
**키워드**  
1. CRA  
2. CRC  
3. 연구간호사  
4. 보건관리자  
5. 보험심사  
6. 메디컬라이터  

### URL 파악  
처음에 채용 페이지가 [1, 2, 3] 같은 식이 아닌 "더보기"로 되어 있어서 더보기를 실행한 주소를 기준으로 진행함  
기본 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword=CRA&recruitPage=1&recruitSort=relation  
zf_user: 로그인 안한 상태를 의미하는 것 같음  
search: 검색 쿼리  
* searchword: 검색할 단어 -> searchword=CRA  
* recruitPageCount: 한 페이지에 보여줄 채용 공고 개수 -> recruitPageCount=40  
* recruitPage: 검색 결과 페이지 번호 -> recruitPage=1  
* recruitSort: 검색 결과 정렬 -> recruitSort=relation  
수집이 목표니까 필요 없어 보임

기준 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword={키워드}&recruitPage={페이지}  
EX) https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword=CRA&recruitPage=1  
