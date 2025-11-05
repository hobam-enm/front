import hmac
import streamlit as st
from streamlit.components.v1 import html as st_html

# =========================
# DIMA 데이터 포털 (단일 파일)
# - 비번 게이트 (secrets)
# - 1행 수평 스크롤 카드
# - 이미지 중앙 크롭(360x220)
# - 이미지/제목 클릭 즉시 이동
# - URL/이미지: 반드시 secrets에서만 관리
# =========================

# ---------- page ----------
st.set_page_config(page_title="DIMA 데이터 포털", page_icon="🧭", layout="wide")

# ---------- auth gate ----------
PW_SECRET = st.secrets.get("auth", {}).get("frontpage_password")
TOKEN_SECRET = st.secrets.get("auth", {}).get("token")

def _qs_key() -> str:
    try:
        return st.query_params.get("key", "")
    except Exception:
        try:
            return st.experimental_get_query_params().get("key", [""])[0]
        except Exception:
            return ""

_qs = _qs_key()
if TOKEN_SECRET and _qs and hmac.compare_digest(str(_qs), str(TOKEN_SECRET)):
    st.session_state["_authed"] = True

if not st.session_state.get("_authed", False):
    st.markdown("### 🔐 DIMA 데이터 포털 접근 권한 필요")
    pw = st.text_input("비밀번호를 입력하세요", type="password", placeholder="••••••••")
    if st.button("입장"):
        if PW_SECRET and hmac.compare_digest(str(pw), str(PW_SECRET)):
            st.session_state["_authed"] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# ---------- meta (타이틀/설명) ----------
APP_META = {
    "dashboard": {"title": "📊 드라마 대시보드", "desc": "드라마 성과데이터 한눈에 비교하기"},
    "ytcc":      {"title": "💬 유튜브 댓글 분석 챗봇", "desc": "드라마 유튜브 반응 AI분석/대화"},
    "insightwiki":  {"title": "📈 인사이트 허브", "desc": "리포트/브리핑/지표 모음"},
    # "toolbox":  {"title": "🧰 마케팅 도구함", "desc": "유틸/변환/자동화"},
}

# 노출 순서 (여기에 키를 추가/정렬)
SITES = [
    "dashboard",
    "ytcc",
    "insightwiki",  
    # "toolbox",    # ← 추가 시 여기 활성화
]

# ---------- helpers ----------
def url_of(k: str) -> str:
    try:
        return st.secrets["apps"].get(k, "").strip()
    except Exception:
        return ""

def img_of(k: str) -> str:
    try:
        u = st.secrets["apps_img"].get(k, "").strip()
        return u if u else "https://images.unsplash.com/photo-1507842217343-583bb7270b66"
    except Exception:
        return "https://images.unsplash.com/photo-1507842217343-583bb7270b66"

# ---------- header (gradient title) ----------
st.markdown(
    """
    <style>
      .grad-title {
        font-weight: 900;
        font-size: clamp(28px, 4vw, 42px);
        line-height: 1.15;
        margin: 4px 0 2px 0;
        background: linear-gradient(90deg, #6757e7 0%, #9B72CB 35%, #ff7bb0 70%, #ff8a4d 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        letter-spacing: 0.2px;
        text-align: center;
      }
      .grad-sub {
        text-align: center;
        opacity: .70;
        margin-top: 2px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("<div class='grad-title'>DIMA 데이터 포털</div>", unsafe_allow_html=True)
st.markdown("<div class='grad-sub'>문의: 미디어)디지털마케팅팀 데이터파트</div>", unsafe_allow_html=True)
st.write("")

# ---------- build cards (URL이 비어 있으면 자동 생략) ----------
def build_cards(keys):
    cards = []
    for k in keys:
        url = url_of(k)
        if not url:  # URL 없으면 렌더링 스킵 (커밍순 영역 없음)
            continue
        meta, img = APP_META.get(k, {"title": k, "desc": ""}), img_of(k)
        cards.append(f"""
        <a class="card-link" href="{url}" target="_blank" rel="noopener noreferrer">
          <div class="card">
            <div class="thumb-wrap"><img class="thumb" src="{img}" alt="{meta['title']}"></div>
            <div class="body">
              <div class="title">{meta['title']}</div>
              <p class="desc">{meta['desc']}</p>
            </div>
          </div>
        </a>
        """)
    return "".join(cards)

cards_html = build_cards(SITES)

# ---------- one-shot render via components.html ----------
st_html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  :root {{
    --card-w: 360px;      /* 카드 폭 */
    --thumb-h: 220px;     /* 이미지 영역 높이 (중앙 크롭) */
  }}
  body {{ margin:0; padding:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; }}
  .zone {{ margin: 8px 0 18px 0; padding: 0 6px; }}
  .zone-title {{ font-weight: 800; opacity:.85; margin: 0 0 8px 6px; }}

  /* 1행 수평 스크롤 컨테이너 */
  .row-scroll {{
    display: flex;
    gap: 24px;
    overflow-x: auto; overflow-y: hidden;
    padding: 8px 4px 18px 4px;
    scroll-snap-type: x mandatory;
  }}
  .row-scroll::-webkit-scrollbar {{ height: 10px; }}
  .row-scroll::-webkit-scrollbar-thumb {{ background: rgba(128,128,128,.35); border-radius: 999px; }}
  .row-scroll::-webkit-scrollbar-track {{ background: transparent; }}

  /* 플로팅 카드 */
  .card {{
    position: relative;
    flex: 0 0 var(--card-w);
    width: var(--card-w);
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.12);
    overflow: hidden;
    scroll-snap-align: start;
    transition: transform .2s ease, box-shadow .2s ease;
    will-change: transform;
  }}
  .card:hover {{ transform: translateY(-4px); }}

  /* 이미지 중앙 크롭 */
  .thumb-wrap {{ width:100%; height: var(--thumb-h); background:#0f1116; }}
  .thumb {{
    width:100%; height:100%;
    object-fit: cover;        /* 중앙 기준 크롭 */
    object-position: center;
    display:block;
  }}

  .body {{ padding: 14px 18px 18px 18px; }}
  .title {{
    font-weight: 800; font-size: 1.05rem; line-height: 1.25rem;
    margin: 8px 0 6px 0; color: inherit;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .desc {{ margin: 0; opacity:.72; font-size:.92rem; }}
  a.card-link {{ text-decoration:none; color:inherit; display:block; }}
</style>
</head>
<body>

<div class="zone">
  <div class="zone-title">서비스</div>
  <div class="row-scroll">
    {cards_html}
  </div>
</div>

</body>
</html>
""", height=420, scrolling=True)

# ---------- footer ----------
st.markdown("<hr style='margin-top:30px; opacity:.2;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:.65;'>© DIMA 데이터 포털</p>", unsafe_allow_html=True)
