# TALLI notice bot

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
- 접수 시작일  

**없는 경우 있음**   
- 근무지역  
- 필수사항  
- 우대사항  
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

## 이슈였던 것들 
https://www.saramin.co.kr/zf_user/jobs/relay/view?...  
채용 공고 링크로 들어갔을 때 relay가 있어서 필요 없는 공고가 보여서 delay를 지운 링크로 진행함  

BeautifulSoup로는 로딩이 끝나지 않은 요소들은 가져올 수 없었다.  
EX) 552건 검색 완료라고 나와야 하는데, ...건 검색 완료로 저장됨  

가끔 텍스트가 없고 상세보기 버튼만 있는 경우가 있었음.  
처리 완료!  

가끔 \xao 문자가 들어오는데, non-breaking space(Latin1,chr(160) 인코딩 형)라고 함.  
단순하게 replace('\\xa0', ' ') 방식으로 지울 수 있다.  

내가 크롬 브라우저에서 검색했을 때 나온 결과 수랑 크롤링해서 저장한 결과수가 달라서 뭐가 문제인지 한참을 삽질했다.  
결론은 브라우저에 따라 사람인에서의 검색 결과가 다르다...  
크롬에서는 CRA를 검색했을 때 319개가 나오지만, 사파리에서는 595건이 나온다.  
