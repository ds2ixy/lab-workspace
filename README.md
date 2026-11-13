# hver-workspace · Workspace Page (공개용)

한국고등직업교육연구소(KCCE HVER) 작업 진행 현황을 공개하는 읽기 전용 페이지입니다.

- 공개 주소: https://lab-workspace-public.pages.dev/ (Cloudflare Pages, 이 저장소에 올리면 자동 배포)
- 같은 페이지: `/kcce/lab-workspace-public`

## 파일
```
index.html                      메인 (공개용 작업 현황)
kcce/lab-workspace-public.html  같은 내용 (kcce 경로용)
_headers                        캐시 끄기 — 갱신 즉시 반영
img/og/og-main.jpg              카톡·SNS 공유 썸네일 (1200×630)
tbp/p0~p6.json                  규정집·학사편람 원문 표 이미지 묶음 (질의응답 화면에서 사용)
files/handbook*.pdf             학사편람 본문·부록 다운로드용 PDF
```

## 갱신 방법
1. 내부용 '연구소 작업공간'(claude.ai, 비공개)에서 진행 상황을 수정
2. Claude에게 "공개용 갱신해줘" 요청
3. Claude가 내부 정보(내부용 링크·메모·담당자·장부 등)를 걸러 이 저장소에 커밋
4. Cloudflare Pages가 1~2분 안에 자동 배포

⚠️ 이 저장소는 공개(Public)입니다. 내부 자료를 올리지 마세요.
