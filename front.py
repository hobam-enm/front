# -*- coding: utf-8 -*-

from typing import Dict, List
import hmac
import streamlit as st

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="DIMA 포털",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# 비밀번호 게이트
# -------------------------
def _get_query_param_key() -> str:
    # Streamlit 1.30+ : st.query_params / 구버전 호환
    try:
        return st.query_params.get("key", "")
    except Exception:
        try:
            return st.experimental_get_query_params().get("key", [""])[0]
        except Exception:
            return ""

PW_SECRET = st.secrets.get("auth", {}).get("frontpage_password")
TOKEN_SECRET = st.secrets.get("auth", {}).get("token")

# 토큰 링크로 바로 입장 (옵션)
_qs_key = _get_query_param_key()
if TOKEN_SECRET and _qs_key and hmac.compare_digest(str(_qs_key), str(TOKEN_SECRET)):
    st.session_state["_authed"] = True

if not st.session_state.get("_authed", False):
    st.markdown("### 🔐 Access Required")
    pw = st.text_input("비밀번호를 입력하세요", type="password", placeholder="••••••••")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("입장"):
            if PW_SECRET and hmac.compare_digest(str(pw), str(PW_SECRET)):
                st.session_state["_authed"] = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    with col_b:
        st.caption("이 페이지는 DIMA 내부 포털입니다.")
    st.stop()

# -------------------------
# 스타일 (색상 등)
# -------------------------
PRIMARY = "#0057E7"

# -------------------------
# 카드 메타 (표시 문구)
# - URL/이미지는 반드시 Secrets에서 주입
# -------------------------
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

# -------------------------
# 유틸
# -------------------------
def get_app_url(key: str) -> str:
    """반드시 st.secrets['apps'][key]만 사용. 없으면 공백."""
    try:
        return st.secrets.get("apps", {}).get(key, "").strip()
    except Exception:
        return ""

def get_app_image(key: str) -> str:
    """시크릿의 apps_img[key] → 없으면 간단한 placeholder."""
    try:
        u = st.secrets.get("apps_img", {}).get(key, "").strip()
    except Exception:
        u = ""
    if u:
        return u
    # 기본 placeholder
    return "https://images.unsplash.com/photo-1507842217343-583bb7270b66"

def open_link_button(label: str, url: str, key: str):
    """외부 링크 버튼(새 탭) — URL 없으면 비활성"""
    if not url:
        st.button(label, key=key, disabled=True)
        return
    st.markdown(
        """
        <a href="{url}" target="_blank" rel="noopener noreferrer">
            <button style="padding:10px 16px;border:none;border-radius:12px;
                           background:{primary};color:white;font-weight:700;
                           cursor:pointer;">
                {label}
            </button>
        </a>
        """.format(url=url, primary=PRIMARY, label=label),
        unsafe_allow_html=True,
    )

# -------------------------
# 헤더
# -------------------------
left, right = st.columns([5, 1])
with left:
    st.markdown("## 🧭 DIMA 포털")
    st.caption("디지털마케팅팀 통합 진입점")
with right:
    if st.button("로그아웃"):
        st.session_state.pop("_authed", None)
        st.rerun()

# -------------------------
# 카드 레이아웃 CSS
# -------------------------
st.markdown(
    """
    <style>
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 16px;
      }
      .card {
        background: #111319;
        border: 1px solid #2a2f3a;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(0,0,0,0.25);
        transition: transform .15s ease, box-shadow .15s ease;
      }
      .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 28px rgba(0,0,0,0.32);
      }
      .thumb {
        width: 100%; height: 168px; object-fit: cover; display:block; background:#0f1116;
      }
      .body { padding: 14px 16px; }
      .title { font-weight:700; font-size:1.05rem; margin:0 0 6px 0; }
      .desc  { color:#C8CDD7; margin:0 0 12px 0; font-size:.92rem; }
      .row   { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# 카드 렌더링
# -------------------------
apps_to_show: List[str] = list(APP_META.keys())

st.markdown('<div class="grid">', unsafe_allow_html=True)
for key in apps_to_show:
    meta = APP_META[key]
    url = get_app_url(key)
    if not url:
        # URL 미설정 → 카드 숨김 (원하면 안내 카드로 바꿀 수 있음)
        continue
    img = get_app_image(key)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<img class="thumb" src="{img}" alt="{meta["title"]}">', unsafe_allow_html=True)
    st.markdown('<div class="body">', unsafe_allow_html=True)
    st.markdown(f'<div class="title">{meta["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="desc">{meta["desc"]}</div>', unsafe_allow_html=True)

    cols = st.columns([1])
    with cols[0]:
        open_link_button("열기", url, key=f"open_{key}")

    st.markdown('</div>', unsafe_allow_html=True)   # .body
    st.markdown('</div>', unsafe_allow_html=True)   # .card
st.markdown('</div>', unsafe_allow_html=True)       # .grid

# -------------------------
# 푸터
# -------------------------
st.markdown("\n")
st.markdown("---")
st.caption("DIMA 포털 · 이미지 카드 레이아웃 · 다크모드 최적화")
