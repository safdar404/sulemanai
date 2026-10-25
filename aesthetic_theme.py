"""Shared midnight aurora theme; presentation only, no application state."""
import streamlit as st
from pathlib import Path

CSS = """
<style>
:root{color-scheme:dark;--ink:#eef2ff;--muted:#b7c1df;--line:#394263;--paper:#0b1026;--bg:#0b1026;--surface:#171f3b;--accent:#00d4ff;--accent-ink:#91eaff;--accent-soft:#20314d;--saffron:#f5cc76;--saffron-soft:#302b36;--grow:#68d5a0;--caution:#ff929f;--grad:linear-gradient(115deg,#00bddd,#7c3aed 55%,#d81b76);--shadow:0 16px 32px -18px #000, inset 0 1px 0 #ffffff16}
.stApp{color:var(--ink)!important;background:radial-gradient(ellipse at 8% 0%,#36205d99,transparent 44%),radial-gradient(ellipse at 100% 12%,#65204466,transparent 45%),radial-gradient(ellipse at 50% 100%,#003c5366,transparent 55%),#0b1026!important;background-attachment:fixed!important}
[data-testid="stHeader"]{background:#0b1026d9!important;backdrop-filter:blur(14px)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#141a38,#0d132c)!important;border-right:1px solid #394263!important}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{color:#f4f6ff!important;letter-spacing:-.025em}
.stApp label,[data-testid="stCaptionContainer"],.stApp summary{color:#c8d1ed!important}
.block-container{padding-top:2.8rem;padding-bottom:3rem;min-width:0}
[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stChatMessage"],.fw-score,.src,.empty,.usage div{background:linear-gradient(145deg,#222b48,#151c35)!important;border:1px solid #414b70!important;border-radius:18px!important;box-shadow:0 7px 0 -4px #070c1d,0 22px 35px -24px #000,inset 0 1px 0 #ffffff1c!important}
[data-testid="stMetric"]{padding:18px!important;transition:transform .2s,box-shadow .2s}
[data-testid="stMetricValue"],[data-testid="stMetricLabel"],.fw-num b{color:#edf5ff!important}
.fw-head,.mg-head,.brand,.rx-hero{background:linear-gradient(125deg,#251a4d,#10192f 60%,#38203d)!important;border:1px solid #555181!important;border-radius:22px!important;padding:26px!important;box-shadow:0 9px 0 -5px #080d22,0 26px 44px -25px #000,inset 0 1px 0 #ffffff24!important}
.rx-hero:before{animation:none!important;opacity:.3}.rx-hero:after{opacity:.06}
.rx-hero.big{padding:34px!important}.rx-hero.big h1{font-size:clamp(28px,4vw,42px)!important}
.fw-word,.hero-title,.page-title{color:#c5d8ff!important;background:linear-gradient(100deg,#00d4ff,#a895ff,#f08ac7)!important;background-clip:text!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important}
.fw-word small,.mg-head p,.rx-hero p,.brand-sub,.page-sub,.hero-text,.fw-foot,.mg-foot,.src-tag,.src .loc{color:#bdc9e8!important;-webkit-text-fill-color:#bdc9e8!important}
.fw-note,.mg-notice{background:#221f36!important;color:#f4ddb0!important;border-color:#ba8c50!important;border-radius:12px!important}
.mg-notice b{color:#ffb7be!important}.mg-triage div:not(.on){background:#17213c!important;color:#cad3ec!important}
.fw-src.py,.pill,.pill.ok{background:#183149!important;color:#9defff!important;border-color:#34718b!important}
.fw-src.ai{color:#f3d38f!important;background:#302b36!important}
.fw-mark.ai em{color:#f3d38f!important}.fw-mark:not(.ai){background:#d8edff!important}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{background:linear-gradient(145deg,#2d3552,#1b233c)!important;color:#eef2ff!important;border:1px solid #626b90!important;border-radius:12px!important;box-shadow:0 4px 0 #070c1d, inset 0 1px 0 #ffffff20!important;transition:transform .18s,box-shadow .18s!important}
button[kind="primary"],button[kind="primaryFormSubmit"]{background:linear-gradient(110deg,#6931cd,#b81d83)!important;color:white!important;border-color:#b489ed!important}
button:disabled{opacity:.5!important;transform:none!important;box-shadow:none!important}
@media(hover:hover) and (pointer:fine){.stButton>button:not(:disabled):hover,.stDownloadButton>button:not(:disabled):hover{transform:translateY(-2px)!important;border-color:#00d4ff!important;box-shadow:0 6px 0 #070c1d,0 10px 24px -12px #00d4ff80!important}[data-testid="stMetric"]:hover{transform:translateY(-3px)}}
.stButton>button:active,.stFormSubmitButton>button:active{transform:translateY(2px)!important;box-shadow:0 1px 0 #070c1d!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input,[data-testid="stChatInput"] textarea{background:#111a32!important;color:#f0f4ff!important;-webkit-text-fill-color:#f0f4ff!important;border-radius:10px!important;caret-color:#00d4ff!important}
input::placeholder,textarea::placeholder{color:#a8b6d7!important;-webkit-text-fill-color:#a8b6d7!important}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"],[data-testid="stChatInput"]{background:#111a32!important;color:#eef2ff!important;border-color:#576487!important}
[data-testid="stChatInput"]{background:linear-gradient(#111a32,#111a32) padding-box,var(--grad) border-box!important;border:2px solid transparent!important;box-shadow:0 12px 28px -17px #00d4ff!important;border-radius:18px!important}
[data-testid="stBottom"]>div,[data-testid="stBottomBlockContainer"]{background:#0b1026ee!important}
[data-testid="stFileUploaderDropzone"]{background:#172540!important;border:1px dashed #6e82bb!important;border-radius:16px!important}
[role="tablist"]{background:#121b33!important;border-color:#424d71!important;border-radius:14px!important}
[role="tab"]{color:#c3cdec!important}[role="tab"][aria-selected="true"]{background:#4f2c87!important;border-radius:10px!important;color:white!important}
[role="tab"][aria-selected="true"] p{color:white!important}
[data-testid="stMarkdownContainer"] code{background:#263350!important;color:#a7efff!important}
.src-id,.src.cited .src-id{background:#57368b!important;color:#fff!important}
.src.cited{background:#1b2944!important;border-color:#5ed7ed!important}
.empty{color:#c8d4ef!important}.empty h3,.side-brand b{color:#f3f5ff!important}.side-brand span,.rx-stat small{color:#bfcbe7!important}
.rx-stat{background:#ffffff09!important;border-color:#777ca4!important;box-shadow:inset 0 1px 0 #ffffff15}
mark{background:#4a3973!important;color:#fff!important}
:focus-visible{outline:3px solid #00d4ff!important;outline-offset:3px!important}
@media(max-width:768px){.block-container{padding-top:1.5rem}.fw-head,.mg-head,.brand,.rx-hero{padding:20px!important}.mg-head{grid-template-columns:1fr!important}.rx-hero.big{padding:24px!important}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.stButton>button:hover,[data-testid="stMetric"]:hover{transform:none!important}}
/* Readability and compact header refinements after live review. */
[data-testid="stCaptionContainer"] p{color:#b7c6e6!important}
[data-testid="stAlert"] p,[data-testid="stAlert"] li{color:#eef2ff!important}
.fw-head{display:grid!important;grid-template-columns:minmax(0,1.2fr) minmax(260px,1fr);align-items:center!important;gap:24px!important}
.fw-head .fw-word{font-size:clamp(30px,3.5vw,44px)!important;line-height:1.15!important;padding:0!important;margin:0!important}
.fw-head .fw-word small{line-height:1.5!important;font-size:15px!important}
.fw-note{max-width:none!important}
@media(max-width:1000px){.fw-head{grid-template-columns:1fr!important;gap:16px!important}}

/* App-specific identity */
.fw-word:before,.mg-head h1:before,.rx-hero h1:before{content:"";display:inline-block;width:60px;height:60px;margin-right:14px;vertical-align:middle;background:url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMTIiIGhlaWdodD0iMTEyIiB2aWV3Qm94PSIwIDAgMTEyIDExMiIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsPSJTdWxlbWFuIEFJIGxvZ28iPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZyIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjMDBiZGRkIi8+PHN0b3Agb2Zmc2V0PSIuNDgiIHN0b3AtY29sb3I9IiM3NDM5ZGYiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNkYjI4N2YiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iYiIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjMzAzNjVjIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMTExYTMyIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3QgeD0iNSIgeT0iNSIgd2lkdGg9IjEwMiIgaGVpZ2h0PSIxMDIiIHJ4PSIyOSIgZmlsbD0iIzA2MGMyMCIvPjxyZWN0IHg9IjMiIHk9IjIiIHdpZHRoPSIxMDYiIGhlaWdodD0iMTA0IiByeD0iMjkiIGZpbGw9InVybCgjYikiIHN0cm9rZT0idXJsKCNnKSIgc3Ryb2tlLXdpZHRoPSIzIi8+PHBhdGggZD0iTTI1IDEyaDU5IiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIuMTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0iTTI1IDYyVjM1YzEzLTUgMjMtMyAzMSA0IDgtNyAxOC05IDMxLTR2MjdjLTEyLTQtMjItMi0zMSA1LTktNy0xOS05LTMxLTVaIiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48cGF0aCBkPSJNNTYgMzl2MjhNMzMgNDVsMTMgMk02NiA0N2wxMy0yIiBzdHJva2U9IiNiOWVhZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0ibTU2IDE0IDMgOSA5IDMtOSAzLTMgOS0zLTktOS0zIDktM1oiIGZpbGw9IiM4YWYwZmYiLz48L3N2Zz4=') center/contain no-repeat;filter:drop-shadow(0 7px 6px #0006)}
.agent-avatar img{content:url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMTIiIGhlaWdodD0iMTEyIiB2aWV3Qm94PSIwIDAgMTEyIDExMiIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsPSJTdWxlbWFuIEFJIGxvZ28iPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZyIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjMDBiZGRkIi8+PHN0b3Agb2Zmc2V0PSIuNDgiIHN0b3AtY29sb3I9IiM3NDM5ZGYiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNkYjI4N2YiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iYiIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjMzAzNjVjIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMTExYTMyIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3QgeD0iNSIgeT0iNSIgd2lkdGg9IjEwMiIgaGVpZ2h0PSIxMDIiIHJ4PSIyOSIgZmlsbD0iIzA2MGMyMCIvPjxyZWN0IHg9IjMiIHk9IjIiIHdpZHRoPSIxMDYiIGhlaWdodD0iMTA0IiByeD0iMjkiIGZpbGw9InVybCgjYikiIHN0cm9rZT0idXJsKCNnKSIgc3Ryb2tlLXdpZHRoPSIzIi8+PHBhdGggZD0iTTI1IDEyaDU5IiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIuMTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0iTTI1IDYyVjM1YzEzLTUgMjMtMyAzMSA0IDgtNyAxOC05IDMxLTR2MjdjLTEyLTQtMjItMi0zMSA1LTktNy0xOS05LTMxLTVaIiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48cGF0aCBkPSJNNTYgMzl2MjhNMzMgNDVsMTMgMk02NiA0N2wxMy0yIiBzdHJva2U9IiNiOWVhZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0ibTU2IDE0IDMgOSA5IDMtOSAzLTMgOS0zLTktOS0zIDktM1oiIGZpbGw9IiM4YWYwZmYiLz48L3N2Zz4=');border-radius:18px!important}
.agent-avatar{background:transparent!important;box-shadow:none!important}
[data-testid="stSidebar"] .side-brand{display:none!important}
[data-testid="stSidebar"] h2:first-of-type{display:none}
[data-testid="stLogo"]{height:auto!important;max-height:74px!important;width:100%;object-fit:contain;object-position:left}
@media(max-width:600px){.fw-word:before,.mg-head h1:before,.rx-hero h1:before{width:44px;height:44px;margin-right:9px}}
[data-testid="stSidebarLogo"]{width:260px!important;height:52px!important;max-width:100%!important;object-fit:contain;object-position:left}
</style>
"""

def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    assets = Path(__file__).resolve().parent / "assets"
    st.logo(str(assets / "wordmark.svg"), icon_image=str(assets / "logo.svg"), size="large")
