import hmac
import streamlit as st
from streamlit.components.v1 import html as st_html

# ---------- page ----------
st.set_page_config(page_title="DIMA 데이터 포털", page_icon="", layout="wide")

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
    st.markdown("### 🔐 DIMA 포털 접근 권한 필요")
    pw = st.text_input("비밀번호를 입력하세요", type="password", placeholder="••••••••")
    if st.button("입장"):
        if PW_SECRET and hmac.compare_digest(str(pw), str(PW_SECRET)):
            st.session_state["_authed"] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# ---------- meta ----------
APP_META = {
    "dashboard": {"title": "📊 드라마 대시보드", "desc": "드라마 주요지표 한눈에 비교분석"},
    "ytcc":      {"title": "💬 유튜브 댓글 분석 챗봇", "desc": "유튜브 댓글 AI요약 분석"},
    "site3":     {"title": "🧩 사이트 3 (준비중)", "desc": "추가 예정 페이지"},
    "site4":     {"title": "🧪 사이트 4 (준비중)", "desc": "추가 예정 페이지"},
}
def url_of(k: str) -> str:
    try: return st.secrets["apps"].get(k, "").strip()
    except Exception: return ""
def img_of(k: str) -> str:
    try:
        u = st.secrets["apps_img"].get(k, "").strip()
        return u if u else "https://images.unsplash.com/photo-1507842217343-583bb7270b66"
    except Exception:
        return "https://images.unsplash.com/photo-1507842217343-583bb7270b66"

# ---------- header ----------
st.markdown("<h1 style='text-align:center;margin-top:-6px;'> DIMA 데이터 포털</h1>", unsafe_allow_html=True)
st.write("")

# ---------- build cards html (1-row horizontal; 360x220 image; click-through) ----------
def build_cards(keys):
    cards = []
    for k in keys:
        meta, url, img = APP_META[k], url_of(k), img_of(k)
        if url:
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
        else:
            cards.append(f"""
            <div class="card disabled">
              <span class="badge-coming">COMING SOON</span>
              <div class="thumb-wrap"><img class="thumb" src="{img}" alt="{meta['title']}"></div>
              <div class="body">
                <div class="title">{meta['title']}</div>
                <p class="desc">{meta['desc']}</p>
              </div>
            </div>
            """)
    return "".join(cards)

html_major = build_cards(["dashboard", "ytcc"])
html_pending = build_cards(["site3", "site4"])

# ---------- one-shot render via components.html (no escaping issues) ----------
st_html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  :root {{
    --card-w: 360px;         /* 카드 고정 폭 */
    --thumb-h: 220px;        /* 이미지 영역 높이 (중앙 크롭) */
  }}
  body {{ margin:0; padding:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; }}
  .zone {{ margin: 8px 0 18px 0; padding: 0 6px; }}
  .zone-title {{ font-weight: 800; opacity:.85; margin: 0 0 8px 6px; }}

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
  .disabled {{ opacity:.55; pointer-events:none; }}
  .badge-coming {{
    position:absolute; top:10px; left:10px;
    background: rgba(0,0,0,.65); color:#fff; font-size:.78rem; font-weight:700;
    padding: 4px 8px; border-radius: 999px;
  }}

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
  <div class="zone-title">주요 서비스</div>
  <div class="row-scroll">
    {html_major}
  </div>
</div>

<div class="zone">
  <div class="zone-title">준비 중</div>
  <div class="row-scroll">
    {html_pending}
  </div>
</div>

</body>
</html>
""", height=640, scrolling=True)

# ---------- footer ----------
st.markdown("<hr style='margin-top:30px; opacity:.2;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:.65;'>© DIMA 포털 · Horizontal Floating Cards</p>", unsafe_allow_html=True)
