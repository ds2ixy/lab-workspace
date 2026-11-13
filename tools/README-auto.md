# 자동 갱신 (평일 17:00 KST)
1. 내부용(연구소 작업공간)과 중식비 현황 원본 index.html을 artifact read_file(paths)로 받는다.
2. `python3 -I tools/build_public.py <내부용> <중식비현황> .`
3. `python3 -I tools/changed.py <이전 index.html> index.html` → SAME이면 아무것도 게시하지 않고 종료.
4. CHANGED이면 claude.ai 공개용 재게시 + git push (+ 중식비 화면이 바뀌었으면 internal-synced.html로 내부용 재게시).
