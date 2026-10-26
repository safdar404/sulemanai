"""Vibrant rainbow / AI-glow theme for Suleman AI. Presentation only, no app state."""
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent / "assets"

RAINBOW = "linear-gradient(100deg,#ff3d6e,#ff9f1c 20%,#ffe14d 40%,#2ee59d 60%,#2bb8ff 80%,#a64dff)"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');
:root{
  color-scheme:dark;
  --bg:#0a0918; --bg2:#121030; --card:#16143a; --card2:#1d1a48; --line:#2f2b66;
  --ink:#f5f3ff; --muted:#b9b4e6;
  --red:#ff3d6e; --orange:#ff9f1c; --yellow:#ffe14d; --green:#2ee59d; --blue:#2bb8ff; --violet:#a64dff;
  --rainbow:__RAINBOW__;
  --glow:0 0 0 1px #ffffff10, 0 10px 30px -14px #a64dff99;
}
html,body,.stApp,input,textarea,button,select{font-family:'Plus Jakarta Sans',system-ui,sans-serif!important}
code,pre{font-family:'JetBrains Mono',monospace!important}

/* ---------- canvas ---------- */
.stApp{
  color:var(--ink)!important;
  background:
    radial-gradient(900px 500px at 0% 0%,#ff3d6e22,transparent 60%),
    radial-gradient(900px 500px at 100% 0%,#2bb8ff22,transparent 60%),
    radial-gradient(900px 600px at 50% 110%,#a64dff2e,transparent 60%),
    var(--bg)!important;
  background-attachment:fixed!important;
}
.stApp:before{ /* rainbow hairline at the very top */
  content:"";position:fixed;inset:0 0 auto 0;height:3px;z-index:1000;background:var(--rainbow);
  background-size:200% 100%;animation:rb-slide 6s linear infinite;
}
@keyframes rb-slide{to{background-position:200% 0}}
[data-testid="stHeader"]{background:#0a0918cc!important;backdrop-filter:blur(12px)}
.stApp .block-container{max-width:1180px!important;padding:3.6rem clamp(14px,2.5vw,36px) 2.5rem!important}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{color:#fff!important;letter-spacing:-.02em;line-height:1.25!important}
.stApp p,.stApp li{line-height:1.6}
.stApp label,.stApp summary,[data-testid="stCaptionContainer"] p{color:var(--muted)!important}
[data-testid="stMarkdownContainer"] p{color:#e9e6ff}
div[data-testid="stVerticalBlock"]{gap:.7rem}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#120f2e,#0b0a1c)!important;border-right:1px solid var(--line)!important}
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]{gap:.45rem}
[data-testid="stSidebar"] [role="radiogroup"] label{
  padding:6px 10px;border-radius:10px;margin:1px 0;transition:background .15s;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#ffffff0d}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,#a64dff33,#2bb8ff22);box-shadow:inset 3px 0 0 var(--violet)}
[data-testid="stSidebarLogo"],[data-testid="stLogo"]{height:40px!important;max-width:220px!important;object-fit:contain;object-position:left}
.side-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:4px 0}
.side-stats div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px 4px;text-align:center}
.side-stats b{display:block;font-size:16px;color:var(--yellow)}.side-stats div:nth-child(2) b{color:var(--green)}.side-stats div:nth-child(3) b{color:var(--blue)}
.side-stats small{font-size:10.5px;color:var(--muted)}

/* ---------- cards / containers ---------- */
[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stChatMessage"]{
  background:linear-gradient(160deg,var(--card2),var(--card))!important;
  border:1px solid var(--line)!important;border-radius:16px!important;box-shadow:var(--glow)!important;
}
[data-testid="stMetric"]{padding:12px 14px!important;position:relative;overflow:hidden}
[data-testid="stMetric"]:before{content:"";position:absolute;inset:0 0 auto 0;height:3px;background:var(--rainbow)}
[data-testid="stMetricLabel"] p{color:var(--muted)!important;font-size:12.5px!important}
[data-testid="stMetricValue"]{color:#fff!important;font-size:clamp(20px,2vw,28px)!important}
[data-testid="stExpander"] summary{padding:.55rem .8rem!important}

/* ---------- chat ---------- */
[data-testid="stChatMessage"]{padding:10px 14px!important;margin-bottom:8px!important;gap:10px}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]){
  background:linear-gradient(160deg,#2a1d55,#1f1745)!important;border-color:#5b3fa6!important;
}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li{color:#f1eeff}
[data-testid="stChatMessage"] img{border-radius:12px}
[data-testid="stChatMessageAvatarCustom"] img,[data-testid="stChatMessage"] img[alt="assistant avatar"]{border-radius:12px!important}
[data-testid="stBottom"]>div,[data-testid="stBottomBlockContainer"]{background:#0a0918f0!important}
[data-testid="stChatInput"]{
  border:2px solid transparent!important;border-radius:16px!important;
  background:linear-gradient(#141233,#141233) padding-box,var(--rainbow) border-box!important;
  box-shadow:0 8px 28px -12px #a64dffaa!important;
}
[data-testid="stChatInput"]>div{background:transparent!important}
[data-testid="stChatInput"] textarea{color:#fff!important;-webkit-text-fill-color:#fff!important;caret-color:var(--yellow)!important;font-size:15px!important}
[data-testid="stChatInputSubmitButton"]{background:var(--rainbow)!important;color:#0a0918!important;border-radius:10px!important}
.thinking{color:var(--muted);font-style:italic}
.thinking span{animation:blink 1.4s infinite;font-weight:800;color:var(--yellow)}
.thinking span:nth-child(2){animation-delay:.2s;color:var(--green)}
.thinking span:nth-child(3){animation-delay:.4s;color:var(--blue)}
@keyframes blink{0%,80%,100%{opacity:.2}40%{opacity:1}}
.msg-meta{font-size:11.5px;color:#8d88c2;margin-top:2px}

/* ---------- inputs ---------- */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input{
  background:#100e2a!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border-radius:10px!important;caret-color:var(--yellow)!important}
input::placeholder,textarea::placeholder{color:#8f8ac4!important;-webkit-text-fill-color:#8f8ac4!important}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]{background:#100e2a!important;border-color:var(--line)!important;border-radius:10px!important}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{border-color:var(--blue)!important;box-shadow:0 0 0 3px #2bb8ff33!important}
[data-testid="stFileUploaderDropzone"]{background:#141233!important;border:1px dashed #6a5fc4!important;border-radius:14px!important}
[data-testid="stSlider"] [role="slider"]{background:var(--yellow)!important;box-shadow:0 0 0 4px #ffe14d33!important}

/* ---------- buttons ---------- */
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button,[data-testid="stPopover"] button{
  background:linear-gradient(160deg,#25215a,#1a1744)!important;color:#f5f3ff!important;
  border:1px solid #3e3884!important;border-radius:11px!important;min-height:38px;padding:6px 14px!important;
  font-weight:600!important;width:100%;transition:transform .15s,box-shadow .15s,border-color .15s!important}
@media(hover:hover){
  .stButton>button:not(:disabled):hover,.stDownloadButton>button:not(:disabled):hover,.stFormSubmitButton>button:not(:disabled):hover{
    transform:translateY(-1px);border-color:var(--blue)!important;box-shadow:0 8px 20px -10px #2bb8ffaa!important}
}
button[kind="primary"],button[kind="primaryFormSubmit"],.stFormSubmitButton>button{
  background:var(--rainbow)!important;background-size:160% 100%!important;color:#120c26!important;border:none!important;font-weight:800!important}
button[kind="primary"] p,button[kind="primaryFormSubmit"] p,.stFormSubmitButton>button p{color:#120c26!important}
button[kind="primary"]:hover{background-position:100% 0!important}
button:disabled{opacity:.45!important;transform:none!important}

[data-testid="stSidebar"] .stButton,[data-testid="stSidebar"] .stButton>button,.st-key-starters .stButton,.st-key-starters .stButton>button,[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.stButton){width:100%!important}
.st-key-starters [data-testid="stElementContainer"]:has(.stButton){width:100%!important}
[data-testid="stSidebar"] [data-testid="stRadioOption"]>div>div:first-child:not([data-testid]){display:none}
[data-testid="stSidebar"] [data-testid="stRadioOption"]{width:100%}
[data-testid="stChatInput"] textarea:focus-visible{outline:none!important}
.emo{-webkit-text-fill-color:initial!important;background:none!important;margin-right:6px}

/* history list */
.st-key-history .stButton>button{background:transparent!important;border:1px solid transparent!important;box-shadow:none!important;
  justify-content:flex-start;text-align:left;min-height:0;padding:4px 10px!important;font-weight:500!important;color:#d6d2fb!important}
.st-key-history .stButton>button p{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left;font-size:13.5px}
.st-key-history .stButton>button:hover{background:#ffffff0d!important;transform:none}
.st-key-history button[kind="primary"]{background:linear-gradient(90deg,#a64dff40,#2bb8ff25)!important;border-color:#a64dff88!important;color:#fff!important}
.st-key-history button[kind="primary"] p{color:#fff!important}
.group-label{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#8079c4;margin:10px 0 2px 4px}

/* starter chips */
.st-key-starters .stButton>button{min-height:52px;font-weight:500!important;text-align:left;justify-content:flex-start;
  background:linear-gradient(#17143c,#17143c) padding-box,linear-gradient(120deg,#ff3d6e66,#2bb8ff66,#a64dff66) border-box!important;
  border:1px solid transparent!important}
.st-key-starters .stButton>button:hover{background:linear-gradient(#1f1b4d,#1f1b4d) padding-box,var(--rainbow) border-box!important}

/* ---------- tabs ---------- */
[role="tablist"]{gap:4px!important;background:#100e2a!important;border:1px solid var(--line)!important;border-radius:12px!important;padding:4px!important;overflow-x:auto}
[role="tab"]{min-height:34px!important;padding:4px 12px!important;border-radius:9px!important;color:#c9c4f5!important}
[role="tab"] p{font-weight:600!important;font-size:13.5px!important}
[role="tab"][aria-selected="true"]{background:linear-gradient(100deg,#a64dff,#2bb8ff)!important}
[role="tab"][aria-selected="true"] p{color:#fff!important}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none!important}

/* ---------- alerts / misc ---------- */
[data-testid="stAlert"]{background:#17143c!important;border:1px solid var(--line)!important;border-radius:12px!important}
[data-testid="stAlert"] p{color:#efeaff!important}
[data-testid="stMarkdownContainer"] code{background:#231f52!important;color:#ffe14d!important;border-radius:6px}
mark{background:#a64dff55!important;color:#fff!important}
hr{border-color:var(--line)!important;margin:.6rem 0!important}
:focus-visible{outline:2px solid var(--yellow)!important;outline-offset:2px!important}

/* ---------- brand header ---------- */
.brand{display:flex;align-items:center;gap:14px;padding:12px 16px;margin-bottom:12px;border-radius:18px;position:relative;
  background:linear-gradient(#14113a,#14113a) padding-box,var(--rainbow) border-box;border:1.5px solid transparent;
  box-shadow:0 14px 40px -22px #a64dffcc}
.brand-name{font-size:20px;font-weight:800;color:#fff;line-height:1.1}
.brand-name em{font-style:normal;background:var(--rainbow);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.brand-sub{font-size:12.5px;color:var(--muted)}
.brand-right{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.chip{font-size:11.5px;font-weight:600;padding:3px 9px;border-radius:999px;background:#ffffff0d;border:1px solid #ffffff1f;color:#e6e2ff;white-space:nowrap}
.agent-status{display:inline-flex;align-items:center;gap:6px;margin-top:4px;font-size:11.5px;font-weight:700;color:#7dffc4;
  background:#2ee59d1a;border:1px solid #2ee59d55;padding:2px 9px;border-radius:999px}
.agent-status .live{width:7px;height:7px;border-radius:50%;background:var(--green);animation:live-pulse 1.8s ease-out infinite}
@keyframes live-pulse{0%{box-shadow:0 0 0 0 #2ee59db3}100%{box-shadow:0 0 0 8px #2ee59d00}}

/* agent avatar with spinning rainbow ring */
@property --ring{syntax:'<angle>';inherits:false;initial-value:0deg}
@keyframes ring-spin{to{--ring:360deg}}
.agent-avatar{position:relative;flex-shrink:0;border-radius:22px;padding:2.5px;
  background:conic-gradient(from var(--ring),#ff3d6e,#ff9f1c,#ffe14d,#2ee59d,#2bb8ff,#a64dff,#ff3d6e);
  animation:ring-spin 5s linear infinite;box-shadow:0 0 24px -4px #a64dffaa}
.agent-avatar img{width:100%;height:100%;display:block;border-radius:20px;background:#0e0c26}
.agent-dot{position:absolute;right:-2px;bottom:-2px;width:14px;height:14px;border-radius:50%;background:var(--green);
  border:2px solid var(--bg);animation:live-pulse 1.8s ease-out infinite}
.side-brand{display:flex;align-items:center;gap:10px;margin:-6px 0 6px}
.side-brand span{font-weight:800;font-size:17px;color:#fff}

/* page titles */
.hero-title,.page-title{font-weight:800;line-height:1.15;background:var(--rainbow);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:rb-slide 8s linear infinite}
.hero-title{font-size:clamp(26px,3.2vw,36px);margin:14px 0 6px}
.page-title{font-size:clamp(22px,2.6vw,30px);margin:6px 0 2px}
.hero-text,.page-sub{color:var(--muted);font-size:15px;margin-bottom:12px}
.chat-title{font-size:20px;font-weight:800;color:#fff;margin:4px 0 0}
.feature-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:8px;margin:10px 0 14px}
.feature-grid div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:9px 11px;font-size:13px;color:#e4e0ff}
.feature-grid b{display:block;font-size:13.5px;color:#fff}

@media(max-width:720px){
  .stApp .block-container{padding:3.4rem 12px 2rem!important}
  .brand{padding:10px 12px}.brand-right{display:none}
  [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:10px!important}
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:calc(50% - 10px)!important}
}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style>
""".replace("__RAINBOW__", RAINBOW)


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    st.logo(str(ASSETS / "wordmark.svg"), icon_image=str(ASSETS / "logo.svg"), size="large")
