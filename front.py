# -*- coding: utf-8 -*-
# 🚀 Streamlit 브릿지/프론트 페이지 (App Launcher)
# - 네가 만든 대시보드/웹앱들의 허브 페이지
# - 카드형 UI, 상태 뱃지, 링크 버튼, 헬스체크, 시크릿스 기반 URL 관리 지원

#region [ 1. 라이브러리 임포트 ]
# =====================================================
import time
from datetime import datetime
from typing import Dict, List

import requests
import streamlit as st
#endregion

#region [ 2. 페이지 설정 & 공통 상수 ]
# =====================================================
st.set_page_config(
    page_title="앱 런처 | Front Page",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

#region [ 2.1 보안: 간단 비밀번호 게이트 ]
# =====================================================
import os, hmac

# 시크릿 키: auth.frontpage_password (필수), auth.token (선택: 링크 토큰)
PW_SECRET = (
    st.secrets.get("auth", {}).get("frontpage_password")
    if hasattr(st, "secrets") else None
)
TOKEN_SECRET = (
    st.secrets.get("auth", {}).get("token")
    if hasattr(st, "secrets") else None
)

# ?key=<token> 으로 접근 허용(선택)
try:
    qs_key = st.query_params.get("key", "") if hasattr(st, "query_params") else ""
except Exception:
    qs_key = ""
if TOKEN_SECRET and qs_key and hmac.compare_digest(str(qs_key), str(TOKEN_SECRET)):
    st.session_state["_authed"] = True

# 비밀번호 폼
if not st.session_state.get("_authed", False):
    st.markdown("### 🔐 Access Required")
    pw = st.text_input("비밀번호를 입력하세요", type="password", placeholder="••••••••")
    c1, c2 = st.columns([1,3])
    with c1:
        if st.button("입장"):
            if PW_SECRET and hmac.compare_digest(str(pw), str(PW_SECRET)):
                st.session_state["_authed"] = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    with c2:
        st.caption("시크릿에 `auth.frontpage_password`를 설정하세요. (선택) `auth.token`으로 링크 토큰 허용")
    st.stop()
#endregion

# ---- 기본 색상/스타일 (필요시 조정) ----
PRIMARY = "#0057E7"
ACCENT  = "#9B72CB"
OK      = "#15B097"
WARN    = "#FFA500"
ERR     = "#E84545"

# ---- 앱 URL 기본값(시크릿스 없을 때 Fallback) ----
DEFAULT_APP_URLS: Dict[str, str] = {
    # ⚠️ 아래를 너의 실제 URL로 바꿔도 되고, st.secrets["apps"][key]로 관리해도 됨
    "dashboard": "https://your-streamlit-cloud.app/overview",     # 📊 IP 성과 대시보드
    "ytcc": "https://your-streamlit-cloud.app/ytcc_chatbot",      # 💬 유튜브 댓글 분석 챗봇
    "gas": "https://script.google.com/macros/s/xxxxxxxx/exec",    # 🧰 Apps Script 취합/관리 웹앱(선택)
}

# ---- 사이드바 네비 표시명 ----
APP_META: Dict[str, Dict[str, str]] = {
    "dashboard": {
        "title": "📊 IP 성과 대시보드",
        "desc": "TV/TVING/디지털/화제성 통합 KPI & 차트",
    },
    "ytcc": {
        "title": "💬 유튜브 댓글 분석 챗봇",
        "desc": "수집·요약·감성·키워드 시각화(트리맵/버블)",
    },
    "gas": {
        "title": "🧰 Apps Script 취합/관리",
        "desc": "RAW_원본 취합, 소스 시트 관리, 로그 확인",
    },
}

# ---- 시크릿스 활용 가이드 ----
SECRETS_TEMPLATE = {
    "apps": {
        "dashboard": "https://your-streamlit-cloud.app/overview",
        "ytcc": "https://your-streamlit-cloud.app/ytcc_chatbot",
        "gas": "https://script.google.com/macros/s/xxxxxxxx/exec"
    }
}
#endregion

#region [ 3. 유틸 함수 ]
# =====================================================

def get_app_url(key: str) -> str:
    """st.secrets.apps[key] 우선 사용, 없으면 DEFAULT_APP_URLS.
    빈 문자열이면 비활성화로 간주."""
    try:
        url = st.secrets.get("apps", {}).get(key, "").strip()
    except Exception:
        url = ""
    if not url:
        url = DEFAULT_APP_URLS.get(key, "").strip()
    return url


def check_health(url: str, timeout: float = 3.0) -> Dict[str, str]:
    """간단한 헬스체크: HEAD→GET 순으로 시도. 상태/지연/메시지 반환."""
    if not url:
        return {"status": "disabled", "latency": "-", "msg": "URL 미설정"}
    t0 = time.perf_counter()
    try:
        try:
            r = requests.head(url, timeout=timeout, allow_redirects=True)
        except Exception:
            r = requests.get(url, timeout=timeout, allow_redirects=True)
        elapsed = (time.perf_counter() - t0) * 1000
        code = r.status_code
        if 200 <= code < 400:
            return {"status": "ok", "latency": f"{elapsed:.0f} ms", "msg": f"HTTP {code}"}
        return {"status": "warn", "latency": f"{elapsed:.0f} ms", "msg": f"HTTP {code}"}
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return {"status": "down", "latency": f"{elapsed:.0f} ms", "msg": str(e).split("\n")[0][:120]}


def badge(status: str, text: str) -> str:
    """상태 텍스트 뱃지(HTML)."""
    color = {
        "ok": OK,
        "warn": WARN,
        "down": ERR,
        "disabled": "#8A8A8A",
    }.get(status, WARN)
    return f"""
    <span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600;background:{color}20;color:{color};border:1px solid {color}55;">
      {text}
    </span>
    """


def open_link_button(label: str, url: str, key: str):
    """외부 링크 버튼(새 탭). Streamlit 기본 버튼은 새탭 제어가 어려워 HTML 사용."""
    if not url:
        st.button(label, key=key, disabled=True)
        return
    st.markdown(
        f"""
        <a href="{url}" target="_blank" rel="noopener noreferrer">
            <button style="padding:8px 14px;border:none;border-radius:12px;background:{PRIMARY};color:white;font-weight:600;cursor:pointer;">{label}</button>
        </a>
        """,
        unsafe_allow_html=True,
    )

#endregion

#region [ 4. 상단 헤더 & 사이드 정보 ]
# =====================================================
left, right = st.columns([3, 2])
with left:
    st.markdown("## 🧭 Front Page — 앱 런처")
    st.caption("대시보드/댓글분석/도구 웹앱으로 이동하는 허브 페이지")

with right:
    st.markdown("#### 환경 상태")
    # 시크릿스 감지
    has_secrets = bool(getattr(st, "secrets", {}))
    st.markdown("- Secrets 구성: " + ("✅ 감지됨" if has_secrets else "⚠️ 없음"))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"- 서버 시각: {now}")
    if st.button("로그아웃"):
        st.session_state.pop("_authed", None)
        st.rerun()

# 편의 토글: 편집 모드
with st.expander("⚙️ 링크 편집/설정 가이드", expanded=False):
    st.write("앱 URL은 `st.secrets['apps']` 또는 코드 상단 `DEFAULT_APP_URLS`로 관리합니다.")
    st.code(SECRETS_TEMPLATE, language="json")
    st.info("Streamlit Cloud에서는 Settings → Secrets에 위 구조로 저장하면 런타임에서 바로 반영됩니다.")

#endregion

#region [ 5. 카드 그리드 스타일 ]
# =====================================================
st.markdown(
    f"""
    <style>
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
        gap: 14px;
      }}
      .card {{
        background: #111319;
        border: 1px solid #2a2f3a;
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
      }}
      .card h3 {{
        margin: 0 0 8px 0;
      }}
      .card p {{
        margin: 6px 0 14px 0;
        color: #C8CDD7;
      }}
      .row {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
      .row.space {{ justify-content: space-between; }}
      .divider {{ height:1px; background:#262b34; margin:10px 0 14px 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)
#endregion

#region [ 6. 앱 카드 렌더링 ]
# =====================================================

apps_to_show: List[str] = list(APP_META.keys())  # 필요시 순서 조정

st.markdown('<div class="grid">', unsafe_allow_html=True)
for key in apps_to_show:
    meta = APP_META[key]
    url = get_app_url(key)
    health = check_health(url)
    status_html = badge(health["status"], health["msg"]) + "&nbsp;" + badge(health["status"], health["latency"]) if url else badge("disabled", "미설정")

    # 카드 내용
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h3>{meta['title']}</h3>", unsafe_allow_html=True)
    st.write(meta["desc"])  # 설명

    st.markdown('<div class="row space">', unsafe_allow_html=True)
    st.markdown(status_html, unsafe_allow_html=True)
    open_link_button("열기", url, key=f"open_{key}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # 추가 버튼들 (옵션)
    cols = st.columns([1,1,1])
    with cols[0]:
        open_link_button("헬스체크 다시", url, key=f"re_{key}")
    with cols[1]:
        st.button("URL 복사", key=f"copy_{key}", on_click=lambda u=url: st.session_state.update({f"copied_{key}": u}))
        if st.session_state.get(f"copied_{key}"):
            st.caption(st.session_state[f"copied_{key}"])
    with cols[2]:
        st.caption("관리: st.secrets['apps'][\"%s\"]" % key)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

#endregion

#region [ 7. 푸터 ]
# =====================================================
st.markdown("\n")
st.markdown("---")
st.caption("문의 : 디지털마케팅팀 데이터파트 · Front Page v1 · Theme optimized for dark mode")
#endregion
