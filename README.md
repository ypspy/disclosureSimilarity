# disclosureSimilarity
기업 연도별 재무제표에 대한 주석 텍스트 유사도 연구. Tf-Idf로 벡터화한 텍스트의 Cosine Similarity로 측정 

### 표본의 입수
1) Direct Parsing (https://github.com/ypspy/dart-scraping): 동일 IP에서 일정 수준(양/속도)이상 요청하는 경우 차단됨. 링크에서 2020년 11월까지 입수된 사업보고서/감사보고서 다운 가능.
2) DART OpenAPI (https://opendart.fss.or.kr/ https://github.com/FinanceData/OpenDartReader#opendartreader): 1일 1만건으로 요청 제한되나, 일반적으로 충분함. XML로 원문 제공되며, 입수 링크의 OpenDartReader로 문서 번호/리스트를 추출한 후 문서에 접근해야 함
