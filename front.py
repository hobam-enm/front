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

# ---- 앱 URL은 반드시 Secrets에서 관리 (Fallback 없음) ----
DEFAULT_APP_URLS: Dict[str, str] = {}

# ---- 사이드바 네비 표시명 ----
APP_META: Dict[str, Dict[str, str]] = {
    "dashboard": {
        "title": "📊 드라마 대시보드",
        "desc": "TV/티빙/디지털 통합 성과",
    },
    "ytcc": {
        "title": "💬 유튜브 댓글 분석 챗봇",
        "desc": "수집·요약·감성·키워드 시각화",
    },
}

# ---- 시크릿스 활용 가이드 ----
SECRETS_TEMPLATE = {
    "apps": {
        "dashboard": "https://dima-ytchatbot.streamlit.app/",
        "ytcc": "https://dima-ytchatbot.streamlit.app/"
    },
    "apps_img": {  # 카드 썸네일(선택)
        "dashboard": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f",
        "ytcc": "https://images.unsplash.com/photo-1528360983277-13d401cdc186"
    },
    "auth": {
        "frontpage_password": "비밀번호",
        "token": "선택_직접링크토큰"
    }
}
#endregion

#region [ 3. 유틸 함수 ]
# =====================================================

def get_app_url(key: str) -> str:
    """반드시 st.secrets['apps'][key]만 사용. 없으면 빈 문자열(비활성)."""
    try:
        url = st.secrets.get("apps", {}).get(key, "").strip()
    except Exception:
        url = ""
    return url


def get_app_image(key: str) -> str:
    """시크릿의 apps_img[key] → 없으면 기본 이미지."""
    try:
        u = st.secrets.get("apps_img", {}).get(key, "").strip()
    except Exception:
        u = ""
    if not u:
        # 아주 얕은 그라디언트 placeholder (data URI는 생략)
        u = "https://images.unsplash.com/photo-1507842217343-583bb7270b66"
    return u


def open_link_button(label: str, url: str, key: str):
    if not url:
        st.button(label, key=key, disabled=True)
        return
    st.markdown(
        f"""
        <a href="{url}" target="_blank" rel="noopener noreferrer">
            <button style=\"padding:8px 14px;border:none;border-radius:12px;background:{PRIMARY};color:white;font-weight:600;cursor:pointer;\">{label}</button>
        </a>
        """,
        unsafe_allow_html=True,
    )

#endregion

#region [ 4. 상단 헤더 ]
# =====================================================
header_l, header_r = st.columns([5,1])
with header_l:
    st.markdown("## 🧭 Front Page — App Launcher")
    st.caption("원하는 앱을 선택하세요")
with header_r:
    if st.button("로그아웃"):
        st.session_state.pop("_authed", None)
        st.rerun()
#endregion

#region [ 5. 카드 그리드 스타일 ]
# =====================================================
st.markdown(
    f"""
    <style>
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 16px;
      }}
      .card {{
        background: #111319;
        border: 1px solid #2a2f3a;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(0,0,0,0.25);
        transition: transform .15s ease, box-shadow .15s ease;
      }}
      .card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 14px 28px rgba(0,0,0,0.32);
      }}
      .thumb {{
        width: 100%; height: 168px; object-fit: cover; display:block;
        background:#0f1116;
      }}
      .body {{ padding: 14px 16px; }}
      .title {{ font-weight:700; font-size:1.05rem; margin:0 0 6px 0; }}
      .desc {{ color:#C8CDD7; margin:0 0 12px 0; font-size:.92rem; }}
      .row {{ display:flex; align-items:center; justify-content:space-between; gap:10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)
#endregion

#region [ 6. 앱 카드 렌더링 ]
# =====================================================
apps_to_show: List[str] = list(APP_META.keys())

st.markdown('<div class="grid">', unsafe_allow_html=True)
for key in apps_to_show:
    meta = APP_META[key]
    url = get_app_url(key)
    img = get_app_image(key)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<img class="thumb" src="{img}" alt="{meta["title"]}">', unsafe_allow_html=True)
    st.markdown('<div class="body">', unsafe_allow_html=True)
    st.markdown(f'<div class="title">{meta["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="desc">{meta["desc"]}</div>', unsafe_allow_html=True)

    cols = st.columns([1,1])
    with cols[0]:
        open_link_button("열기", url, key=f"open_{key}")
    with cols[1]:
        st.caption(url)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
#endregion

#region [ 7. 푸터 ]
# =====================================================
st.markdown("
")
st.markdown("---")
st.caption("Front Page v1.1 · 이미지 카드 레이아웃 · 다크모드 최적화")
#endregion
