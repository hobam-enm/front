## 목적
이 문서는 이 리포지토리에서 AI 기반 코드 에이전트(예: Copilot, 내부 자동화)가 빠르게 생산적으로 작업할 수 있도록 프로젝트의 핵심 구조, 관례, 실행/디버깅 방법, 민감한 설정 포인트를 요약합니다.

## 한줄 요약
- 단일 파일 Streamlit 대시보드 앱: `front.py`가 엔트리 포인트입니다.
- 비밀(secrets) 기반으로 외부 링크/이미지와 접근 제어를 처리합니다 (`st.secrets['apps']`, `st.secrets['apps_img']`, `st.secrets['auth']`).

## 아키텍처(빅픽처)
- UI: Streamlit으로 구성된 단일 페이지 앱(`front.py`) — HTML/CSS/JS를 인라인으로 렌더링 (`streamlit.components.v1.html`).
- 데이터/서비스 연결: 외부 서비스의 링크는 Streamlit secrets에 `apps` 딕셔너리로 보관. 앱 카드 구성은 `APP_META`, `ROW1_KEYS`, `ROW2_KEYS`로 결정.
- 인증: `st.secrets['auth']`의 `frontpage_password`와 `token` 값을 사용해 접근 제어(패스워드 입력 또는 쿼리 파라미터 `key`)를 수행. HMAC 비교(`hmac.compare_digest`)로 안전 비교.

## 핵심 파일/심볼
- `front.py` — 전체 애플리케이션 코드
  - `APP_META` — 카드의 타이틀/설명 정의
  - `ROW1_KEYS`, `ROW2_KEYS` — 각 행에 렌더링할 카드 키 목록
  - `url_of(k)` / `img_of(k)` — `st.secrets`에서 url/img를 조회
  - `_qs_key()` / `PW_SECRET` / `TOKEN_SECRET` — 인증 관련 로직
  - `build_cards(keys)` — 카드 HTML을 생성하고 `st_html(...)`으로 한 번에 렌더링
- `requirements.txt` — 필요한 런타임 패키지 (`streamlit`, `requests`) — 로컬 실행 시 참조

## 프로젝트별 규칙 / 패턴
- 카드 추가: 새 서비스는 1) `APP_META`에 메타 추가, 2) 적절한 `ROW*_KEYS`에 키 추가, 3) 비밀에 `apps.<key>`에 URL, 선택적으로 `apps_img.<key>`에 이미지 URL을 추가하면 즉시 반영됩니다.
- 준비중 항목: 키가 `ytif` 또는 `weekly_brief`이면 URL이 없어도 임시 링크(`#`)로 렌더링.
- 세부 스타일/스크립트는 인라인 HTML/CSS/JS로 관리 — 외부 템플릿 파일 없음.
- 인증 상태는 `st.session_state['_authed']`로 표현됩니다. 이 키를 보존하세요.

## 실행 / 디버깅 (로컬)
1. 가상환경 생성 및 패키지 설치
   - PowerShell 예시:
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```
2. 비밀 구성(권장): 로컬에서 `streamlit` secrets 사용
   - 파일: `.streamlit/secrets.toml` (git에 커밋 금지)
```
[auth]
frontpage_password = "your-password"
token = "your-token"

[apps]
dashboard = "https://example.com/dashboard"

[apps_img]
dashboard = "https://.../image.jpg"
```
3. 앱 실행 (PowerShell)
```
streamlit run front.py --server.port 8501
```
4. 디버깅 팁
  - `st.experimental_get_query_params()`와 `st.query_params` 둘 다 코드에서 예외 처리를 위해 사용되므로, 쿼리 파라미터 테스트 시 둘 다 점검하세요.
  - `st.session_state['_authed']`를 직접 설정하면 인증 단계를 생략할 수 있습니다(로컬 개발용).

## 보안/운영 유의사항
- 민감한 값은 반드시 `st.secrets` 또는 환경변수로 관리하세요. 코드에 하드코딩 금지.
- 인증 비교는 `hmac.compare_digest`를 사용 — 변경하지 마세요.

## 예시: 새 카드 추가 절차
1. `APP_META['myapp'] = {'title':'제목','desc':'설명'}` 추가
2. `ROW1_KEYS.append('myapp')` (또는 ROW2)
3. `.streamlit/secrets.toml`에 `apps.myapp = "https://..."` 및 선택적 `apps_img.myapp = "https://..."` 추가
4. 앱 재실행 또는 Streamlit이 자동 리로드하면 반영

## 외부 연동 및 의존성
- 의존성: `streamlit`(UI), `requests`(추가 HTTP 통신 가능)
- 외부 서비스는 단순 링크 형태로 연결 — 이 레포는 프록시/백엔드 역할을 하지 않습니다.

## 작업 시 주의할 점 (에이전트용 요약)
- 절대 secrets 값을 로그/출력하지 마세요.
- UI는 인라인 HTML/CSS/JS에 의존하므로 포맷 변경 시 전체 문자열 보간 방식을 유지하세요(현재 f-string 사용).
- 인증 플로우와 `st.session_state['_authed']`의 존재를 파괴하지 마세요.

## 문의 / 미확인 항목
- CI, 배포 방식(예: Streamlit Cloud, Docker, 사내 서버)에 대한 정보가 없습니다. 배포 관련 세부정보가 필요하면 알려주세요.

---
피드백: 이 문서가 충분히 실무에 도움이 되나요? 추가로 CI, 배포, 또는 연동 서비스(예: OAuth, 내부 API) 정보가 있으면 알려주시면 반영하겠습니다.
