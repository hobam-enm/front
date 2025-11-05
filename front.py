# -*- coding: utf-8 -*-
# =========================================================
# DIMA 포털 — Horizontal Floating Cards (1-row)
# =========================================================
# 기능:
# - 비밀번호 게이트(Secrets)
# - 4개 고정 카드: 사이트1/사이트2/사이트3/사이트4
# - 이미지 중앙 기준 크롭(object-fit: cover)
# - 이미지 or 제목 클릭 시 바로 이동 (버튼 없음)
# - 가로 1행 수평 스크롤, 카드 겹침 방지
#
# 🔐 Secrets (TOML 예시)
# [apps]
# dashboard = "https://dima-ytchatbot.streamlit.app/"
# ytcc      = "https://dima-ytchatbot.streamlit.app/"
# site3     = ""  # (준비중) 나중에 URL 넣으면 자동 활성화
# site4     = ""  # (준비중) 나중에 URL 넣으면 자동 활성화
#
# [apps_img]
# dashboard = "https://images.unsplash.com/photo-1518779578993-ec3579fee39f"
# ytcc      = "https://images.unsplash.com/photo-1528360983277-13d401cdc186"
# site3     = "https://images.unsplash.com/photo-1607746882042-944635dfe10e"
# site4     = "https://images.unsplash.com/photo-1612831662375-295c1003d3a8"
#
# [auth]
# frontpage_password = "네_비번"
# # token = "선택_직접링크토큰"  # ?key=<token>으로 바로 입장
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

def _qs_token() -> str:
    try:
        return st.query_params.get("key", "")
    except Exception:
        try:
            return st.experimental_get_query_params().get("key", [""])[0]
        except Exception:
            return ""

_qs = _qs_token()
if TOKEN_SECRET and _qs and hmac.compare_digest(str(_qs), str(TOKEN_SECRET)):
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
# 메타 (표시 문구)
# -------------------------
APP_META = {
    "dashboard": {"title": "📊 드라마 대시보드", "desc": "TV/티빙/디지털 통합 성과"},
    "ytcc":      {"title": "💬 유튜브 댓글 분석 챗봇", "desc": "수집·요약·감성·키워드 시각화"},
    "site3":     {"title": "🧩 사이트 3 (준비중)", "desc": "추가 예정 페이지"},
    "site4":     {"title": "🧪 사이트 4 (준비중)", "desc": "추가 예정 페이지"},
}

def url_of(k: str) -> str:
    try: return st.secrets["apps"].get(k, "").strip()
    except: return ""

def img_of(k: str) -> str:
    try:
        u = st.secrets["apps_img"].get(k, "").strip()
        return u if u else "https://images.unsplash.com/photo-1507842217343-583bb7270b66"
    except:
        return "https://images.unsplash.com/photo-1507842217343-583bb7270b66"

# -------------------------
# 헤더
# -------------------------
st.markdown("<h1 style='text-align:center;margin-top:-6px;'>🧭 DIMA 포털</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;opacity:0.7;'>디지털마케팅팀 통합 진입점</p>", unsafe_allow_html=True)
st.write("")

# -------------------------
# 스타일 (1행 · 수평 스크롤 · 플로팅 카드)
# -------------------------
st.markdown("""
<style>
  /* 행 전체: 가로 스크롤 */
  .row-scroll {
    display: flex;
    gap: 24px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 8px 4px 18px 4px;
    scroll-snap-type: x mandatory;
  }
  .row-scroll::-webkit-scrollbar { height: 10px; }
  .row-scroll::-webkit-scrollbar-thumb {
    background: rgba(128,128,128,.35); border-radius: 999px;
  }
  .row-scroll::-webkit-scrollbar-track { background: transparent; }

  /* 카드: 고정 폭 + 플로팅 */
  .card {
    flex: 0 0 360px;          /* 고정 너비로 1행 정렬 */
    width: 360px;
    background: rgba(255,255,255,0.9);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.12);
    overflow: hidden;
    scroll-snap-align: start;
    transition: transform .2s ease, box-shadow .2s ease;
    will-change: transform;
  }
  [data-theme="dark"] .card {
    background: rgba(17,19,25,0.85);
    border: 1px solid #2a2f3a;
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
  }
  .card:hover { transform: translateY(-4px); }

  /* 썸네일: 중앙 기준 크롭 */
  .thumb-wrap { width:100%; height: 220px; background:#0f1116; }
  .thumb {
    width: 100%; height: 100%;
    object-fit: cover;        /* 비율 안맞으면 중앙 기준 잘라냄 */
    object-position: center;
    display:block;
  }

  /* 본문영역 */
  .body { padding: 14px 18px 18px 18px; }
  .title {
    font-weight: 800; font-size: 1.05rem; line-height: 1.25rem;
    margin: 8px 0 6px 0; color: inherit; /* 테마 상속 → 이모지+텍스트 모두 보이게 */
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .desc  {
    margin: 0; opacity: .7; font-size: .92rem;
  }

  /* 링크 전체 클릭 */
  a.card-link { text-decoration: none; color: inherit; display:block; }

  /* 준비중 카드 비활성 */
  .disabled { opacity: .55; pointer-events: none; }
  .badge-coming {
    position:absolute; top:10px; left:10px;
    background: rgba(0,0,0,.65); color:#fff; font-size:.78rem; font-weight:700;
    padding: 4px 8px; border-radius: 999px;
  }

  /* 카드 그룹(시각적 구역 분리) */
  .zone {
    margin: 8px 0 18px 0; padding: 6px 2px;
  }
  .zone-title {
    font-weight: 800; opacity:.85; margin: 0 0 6px 6px;
  }
</style>
""", unsafe_allow_html=True)

# -------------------------
# 렌더링
# -------------------------
# 구역 1 — 사이트 1/2
st.markdown('<div class="zone">', unsafe_allow_html=True)
st.markdown('<div class="zone-title">주요 서비스</div>', unsafe_allow_html=True)
st.markdown('<div class="row-scroll">', unsafe_allow_html=True)

for key in ["dashboard", "ytcc"]:
    meta, url, img = APP_META[key], url_of(key), img_of(key)
    html = f"""
    <a class="card-link" href="{url}" target="_blank">
      <div class="card">
        <div class="thumb-wrap"><img class="thumb" src="{img}" alt="{meta['title']}"></div>
        <div class="body">
          <div class="title">{meta['title']}</div>
          <p class="desc">{meta['desc']}</p>
        </div>
      </div>
    </a>
    """
    st.markdown(html, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# 구역 2 — 사이트 3/4 (더미, 나중에 URL 넣으면 자동 활성화)
st.markdown('<div class="zone">', unsafe_allow_html=True)
st.markdown('<div class="zone-title">준비 중</div>', unsafe_allow_html=True)
st.markdown('<div class="row-scroll">', unsafe_allow_html=True)

for key in ["site3", "site4"]:
    meta, url, img = APP_META[key], url_of(key), img_of(key)
    if url:
        html = f"""
        <a class="card-link" href="{url}" target="_blank">
          <div class="card">
            <div class="thumb-wrap"><img class="thumb" src="{img}" alt="{meta['title']}"></div>
            <div class="body">
              <div class="title">{meta['title']}</div>
              <p class="desc">{meta['desc']}</p>
            </div>
          </div>
        </a>
        """
    else:
        html = f"""
        <div class="card disabled" style="position:relative;">
          <span class="badge-coming">COMING SOON</span>
          <div class="thumb-wrap"><img class="thumb" src="{img}" alt="{meta['title']}"></div>
          <div class="body">
            <div class="title">{meta['title']}</div>
            <p class="desc">{meta['desc']}</p>
          </div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# 푸터
st.markdown("<hr style='margin-top:30px; opacity:.2;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:.65;'>© DIMA 포털 · Horizontal Floating Cards</p>", unsafe_allow_html=True)
