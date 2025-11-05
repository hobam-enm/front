# -*- coding: utf-8 -*-
# =========================================================
# DIMA 포털 — 리디자인 버전 (4-Grid Floating Layout)
# =========================================================
# 기능 요약:
# - 비밀번호 게이트 (Secrets)
# - 4개 고정 카드 (사이트 3,4는 더미로 주석 포함)
# - 이미지 중앙 기준 crop-fit
# - 이미지·제목 클릭 시 바로 이동
# - 플로팅 글래스 카드 UI
#
# 🔐 Secrets (TOML)
# [apps]
# dashboard = "https://dima-ytchatbot.streamlit.app/"
# ytcc      = "https://dima-ytchatbot.streamlit.app/"
# site3     = ""  # 나중에 추가 가능
# site4     = ""  # 나중에 추가 가능
#
# [apps_img]
# dashboard = "https://images.unsplash.com/photo-1518779578993-ec3579fee39f"
# ytcc      = "https://images.unsplash.com/photo-1528360983277-13d401cdc186"
# site3     = "https://images.unsplash.com/photo-1607746882042-944635dfe10e"
# site4     = "https://images.unsplash.com/photo-1612831662375-295c1003d3a8"
#
# [auth]
# frontpage_password = "네_비번"
# =========================================================

import hmac
import streamlit as st

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(page_title="DIMA 포털", page_icon="🧭", layout="wide")

# -------------------------
# 비밀번호 게이트
# -------------------------
PW_SECRET = st.secrets.get("auth", {}).get("frontpage_password")
TOKEN_SECRET = st.secrets.get("auth", {}).get("token")

try:
    qs_key = st.query_params.get("key", "")
except Exception:
    try:
        qs_key = st.experimental_get_query_params().get("key", [""])[0]
    except Exception:
        qs_key = ""

if TOKEN_SECRET and qs_key and hmac.compare_digest(str(qs_key), str(TOKEN_SECRET)):
    st.session_state["_authed"] = True

if not st.session_state.get("_authed", False):
    st.markdown("### 🔐 DIMA 포털 접근 권한 필요")
    pw = st.text_input("비밀번호를 입력하세요", type="password", placeholder="••••••••")
    if st.button("입장"):
        if PW_SECRET and hmac.compare_digest(str(pw), str(PW_SECRET)):
            st.session_state["_authed"] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# -------------------------
# 메타정보 (4개 고정)
# -------------------------
APP_META = {
    "dashboard": {
        "title": "📊 드라마 대시보드",
        "desc": "TV/티빙/디지털 통합 성과",
    },
    "ytcc": {
        "title": "💬 유튜브 댓글 분석 챗봇",
        "desc": "수집·요약·감성·키워드 시각화",
    },
    "site3": {
        "title": "🧩 사이트 3 (준비중)",
        "desc": "추가 예정 페이지",
    },
    "site4": {
        "title": "🧪 사이트 4 (준비중)",
        "desc": "추가 예정 페이지",
    },
}

def get_url(k): 
    try: return st.secrets["apps"].get(k, "")
    except: return ""

def get_img(k):
    try: 
        return st.secrets["apps_img"].get(k, "")
    except: 
        return "https://images.unsplash.com/photo-1507842217343-583bb7270b66"

# -------------------------
# 헤더
# -------------------------
st.markdown("<h1 style='text-align:center;margin-top:-10px;'>🧭 DIMA 포털</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#AAA;'>디지털마케팅팀 통합 진입점</p>", unsafe_allow_html=True)
st.write("")

# -------------------------
# 스타일 (플로팅 카드)
# -------------------------
st.markdown("""
<style>
  .app-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(300px, 1fr));
    gap: 32px;
    justify-items: center;
    margin-top: 30px;
  }
  .card {
    width: 100%;
    max-width: 500px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    backdrop-filter: blur(8px);
    transition: transform .25s ease, box-shadow .25s ease;
  }
  .card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
  }
  .thumb {
    width: 100%;
    height: 220px;
    object-fit: cover;
    object-position: center;
    display: block;
  }
  .body {
    padding: 16px 20px 22px 20px;
  }
  .title {
    font-weight: 700;
    font-size: 1.1rem;
    margin: 6px 0;
    color: white;
  }
  .desc {
    color: #C8CDD7;
    font-size: 0.93rem;
  }
  a.card-link {
    text-decoration: none;
    color: inherit;
  }
</style>
""", unsafe_allow_html=True)

# -------------------------
# 카드 렌더링 (2x2 고정)
# -------------------------
st.markdown('<div class="app-grid">', unsafe_allow_html=True)

for key in ["dashboard", "ytcc", "site3", "site4"]:
    meta = APP_META[key]
    url = get_url(key)
    img = get_img(key)

    # 링크 감싸기 (없으면 disabled 카드)
    if url:
        st.markdown(
            f"""
            <a href="{url}" target="_blank" class="card-link">
              <div class="card">
                <img class="thumb" src="{img}" alt="{meta['title']}">
                <div class="body">
                  <div class="title">{meta['title']}</div>
                  <div class="desc">{meta['desc']}</div>
                </div>
              </div>
            </a>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="card" style="opacity:0.5;pointer-events:none;">
              <img class="thumb" src="{img}" alt="{meta['title']}">
              <div class="body">
                <div class="title">{meta['title']}</div>
                <div class="desc">{meta['desc']}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# 푸터
# -------------------------
st.markdown("<hr style='margin-top:50px;opacity:0.2;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#999;'>© DIMA 포털 · 다크모드 플로팅 UI</p>", unsafe_allow_html=True)
