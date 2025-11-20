import hmac
import streamlit as st
from streamlit.components.v1 import html as st_html


# ---------- page ----------
st.set_page_config(page_title="드라마 데이터 포털", page_icon="🧭", layout="wide")

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
    st.markdown("### 🔐 드라마 데이터 포털 접근 권한 필요")
    pw = st.text_input("비밀번호를 입력하세요", type="password", placeholder="••••••••")
    if st.button("입장"):
        if PW_SECRET and hmac.compare_digest(str(pw), str(PW_SECRET)):
            st.session_state["_authed"] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# ---------- meta ----------
# ===== 서비스 메타데이터 설정 =====
APP_META = {
    "dashboard":   {"title": "📊 드라마 대시보드",      "desc": "드라마 성과데이터 한눈에 비교하기"},
    "ytcb":        {"title": "💬 유튜브 댓글 분석 AI챗봇", "desc": "드라마 유튜브 반응 AI분석/대화"},
    "ytcc":        {"title": "🔎 유튜브 댓글 수집기",    "desc": "유튜브 댓글 수집 및 정량 시각화"},
    "insightwiki": {"title": "💡 인사이트위키",          "desc": "주제별 드라마 인사이트 분석"},
    "actorwiki":   {"title": "💡 배우위키",              "desc": "주요 배우 프로필 및 반응분석"},
    "ytif":        {"title": "🔭 유튜브 인사이트파인더",  "desc": "준비 중 (Coming Soon)"},
    "weekly_brief":{"title": "📝 주간 시청자 브리핑",    "desc": "IP별 주간 시청자반응 브리핑"},  
}

# ===== 카드 배치 구성 (1행에 신규 카드 추가) =====
ROW1_KEYS = ["dashboard", "weekly_brief", "actorwiki", "insightwiki"]
ROW2_KEYS = ["ytcb", "ytcc", "ytif"]

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

# ---------- header ----------
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
      .grad-sub { text-align: center; opacity: .70; margin-top: 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("<div class='grad-title'>드라마 데이터 포털</div>", unsafe_allow_html=True)
st.markdown("<div class='grad-sub'>문의: 미디어)디지털마케팅팀 데이터파트</div>", unsafe_allow_html=True)
st.write("")

# ---------- build cards ----------
def build_cards(keys):
    cards = []
    for k in keys:
        url = url_of(k)
        # 'ytif'와 'weekly_brief'는 준비중이므로 URL이 없어도 카드를 렌더링 (임시 링크 #)
        if (k == "ytif") and not url:
            url = "#"
        
        if not url:
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

# ===== 행별 HTML 생성 =====
cards_html_row1 = build_cards(ROW1_KEYS)
cards_html_row2 = build_cards(ROW2_KEYS)

# ---------- one-shot render (with hover arrows) ----------
st_html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  :root {{
    --card-w: 360px;
    --thumb-h: 220px;
  }}
  body {{ margin:0; padding:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; }}
  
  /* zone 간격 조정 */
  .zone {{ margin: 8px 0 32px 0; padding: 0 6px; }}
  .zone-title {{ font-weight: 800; opacity:.85; margin: 0 0 12px 6px; font-size: 1.1rem; }}

  /* 컨테이너(오버레이 화살표 포함) */
  .scroll-wrap {{
    position: relative;
  }}

  /* 1행 수평 스크롤 영역 */
  .row-scroll {{
    display: flex;
    gap: 24px;
    overflow-x: auto; overflow-y: hidden;
    padding: 8px 4px 18px 4px;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;           /* Firefox */
  }}
  .row-scroll::-webkit-scrollbar {{ display: none; }} /* WebKit */

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
    object-fit: cover; object-position: center; display:block;
  }}

  .body {{ padding: 14px 18px 18px 18px; }}
  .title {{
    font-weight: 800; font-size: 1.05rem; line-height: 1.25rem;
    margin: 8px 0 6px 0; color: inherit;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .desc {{ margin: 0; opacity:.72; font-size:.92rem; }}
  a.card-link {{ text-decoration:none; color:inherit; display:block; }}

  /* 좌/우 오버레이 화살표 */
  .arrow {{
    position: absolute; top: 0; bottom: 0;
    width: 56px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(to var(--side), rgba(255,255,255,0.12), rgba(255,255,255,0));
    pointer-events: auto;
    opacity: 0; transition: opacity .2s ease;
    cursor: pointer;
  }}
  .scroll-wrap:hover .arrow {{ opacity: 1; }}

  .arrow-left  {{ left: 0;  --side: right;  border-top-left-radius: 14px; border-bottom-left-radius: 14px; }}
  .arrow-right {{ right: 0; --side: left;   border-top-right-radius:14px; border-bottom-right-radius:14px; }}

  .arrow > .chev {{
    width: 28px; height: 28px; border-radius: 999px;
    display:flex; align-items:center; justify-content:center;
    background: rgba(0,0,0,0.38); color: white; font-weight: 900;
    box-shadow: 0 2px 8px rgba(0,0,0,.25);
    user-select: none;
  }}
  .arrow:hover > .chev {{ background: rgba(0,0,0,0.55); }}
</style>
</head>
<body>

<div class="zone">
  <div class="zone-title">대시보드&인사이트</div>
  <div class="scroll-wrap">
    <div class="row-scroll">
      {cards_html_row1}
    </div>
    <div class="arrow arrow-left"  title="왼쪽으로"><div class="chev">◀</div></div>
    <div class="arrow arrow-right" title="오른쪽으로"><div class="chev">▶</div></div>
  </div>
</div>

<div class="zone">
  <div class="zone-title">데이터 분석도구</div>
  <div class="scroll-wrap">
    <div class="row-scroll">
      {cards_html_row2}
    </div>
    <div class="arrow arrow-left"  title="왼쪽으로"><div class="chev">◀</div></div>
    <div class="arrow arrow-right" title="오른쪽으로"><div class="chev">▶</div></div>
  </div>
</div>

<script>
(function() {{
  // 모든 row-scroll 요소에 대해 개별적으로 동작 바인딩
  const rows = document.querySelectorAll('.row-scroll');
  
  rows.forEach(row => {{
    const wrap = row.parentElement;
    const left = wrap.querySelector('.arrow-left');
    const right = wrap.querySelector('.arrow-right');

    // hover 자동 스크롤
    let hoverTimer = null;
    function startHover(dir) {{
      stopHover();
      hoverTimer = setInterval(() => {{
        row.scrollBy({{ left: dir * 12, behavior: 'smooth' }});
      }}, 16);
    }}
    function stopHover() {{
      if (hoverTimer) {{ clearInterval(hoverTimer); hoverTimer = null; }}
    }}

    if (left && right) {{
        left.addEventListener('mouseenter', () => startHover(-1));
        right.addEventListener('mouseenter', () => startHover(1));
        left.addEventListener('mouseleave', stopHover);
        right.addEventListener('mouseleave', stopHover);

        // 클릭 점프
        left.addEventListener('click',  () => row.scrollBy({{ left: -320, behavior: 'smooth' }}));
        right.addEventListener('click', () => row.scrollBy({{ left:  320, behavior: 'smooth' }}));
    }}

    // 화살표 상태 업데이트
    function updateArrows() {{
      const atStart = row.scrollLeft <= 0;
      const atEnd = row.scrollLeft + row.clientWidth >= row.scrollWidth - 1;
      
      if (left) {{
        left.style.pointerEvents  = atStart ? 'none' : 'auto';
        left.style.opacity        = atStart ? '0.25' : '';
      }}
      if (right) {{
        right.style.pointerEvents = atEnd   ? 'none' : 'auto';
        right.style.opacity       = atEnd   ? '0.25' : '';
      }}
    }}
    
    row.addEventListener('scroll', updateArrows);
    // 초기화 시 한 번 실행
    updateArrows();
  }});

  window.addEventListener('resize', () => {{
    rows.forEach(row => row.dispatchEvent(new Event('scroll')));
  }});
}})();
</script>

</body>
</html>
""", height=900, scrolling=False)

# ---------- footer ----------
st.markdown("<hr style='margin-top:30px; opacity:.2;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:.65;'>© 드라마 데이터 포털</p>", unsafe_allow_html=True)