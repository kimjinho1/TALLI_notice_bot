# TALLI notice bot 

## 사람인 크롤링  
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
- 근무지역  
- 필수사항  
- 우대사항  
- 근무형태  
- 급여  
- 근무일시  
- 접수 시작일  
- 접수 마감일


## URL 파악  
기준 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&&recruitSort=relation&searchword={키워드}&recruitPage={페이지}  
* searchword: 검색할 단어 -> searchword=CRA  
* recruitPageCount: 한 페이지에 보여줄 채용 공고 개수 ->  recruitPageCount=30  
* recruitPage: 페이지 번호 -> recruitPage=1  
* recruitSort: 정렬(관련도) -> recruitSort=relation  


## 이슈였던 것들 
채용 공고 링크로 들어갔을 때 relay 때문에 필요 없는 공고가 보여서 relay를 지운 링크로 진행함   
https://www.saramin.co.kr/zf_user/jobs/relay/view?...   

가끔 텍스트가 없고 상세보기 버튼만 있는 경우가 있었서 추가적인 처리가 필요했음  
가끔 \xao 문자가 들어오는데, non-breaking space(Latin1,chr(160) 인코딩 형)라고 함    
단순하게 replace('\\xa0', ' ') 방식으로 처리    
