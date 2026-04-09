[Render 배포용 간단 안내]

1. 이 app.py는 두 가지 방식으로 동작합니다.
- 로컬에서 DATABASE_URL이 없으면: 기존처럼 dashboard.db(SQLite) 사용
- Render에서 DATABASE_URL이 있으면: Postgres 사용

2. Render에서 해야 할 것
- Web Service 생성
- Environment에 DATABASE_URL 추가 (Render Postgres Internal/External URL)
- EDIT_PASSWORD도 함께 추가 권장
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app

3. GitHub에 올릴 파일
- app.py
- index.html
- requirements.txt

4. 주의
- 이 파일은 기존 SQLite 전용 코드를 SQLAlchemy 기반으로 바꾼 버전입니다.
- 증빙자료 업로드 기능은 기존과 동일하게 비활성 상태입니다.
