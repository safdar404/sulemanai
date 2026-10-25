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
.fw-word:before,.mg-head h1:before,.rx-hero h1:before{content:"";display:inline-block;width:60px;height:60px;margin-right:14px;vertical-align:middle;background:url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMTIiIGhlaWdodD0iMTEyIiB2aWV3Qm94PSIwIDAgMTEyIDExMiIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsPSJTdWxlbWFuIEFJIGxvZ28iPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZyIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjNDdkMmIzIi8+PHN0b3Agb2Zmc2V0PSIuNDgiIHN0b3AtY29sb3I9IiMzYjgyYTAiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM2YzgyYzEiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iYiIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjMzAzNjVjIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMTExYTMyIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3QgeD0iNSIgeT0iNSIgd2lkdGg9IjEwMiIgaGVpZ2h0PSIxMDIiIHJ4PSIyOSIgZmlsbD0iIzA2MGMyMCIvPjxyZWN0IHg9IjMiIHk9IjIiIHdpZHRoPSIxMDYiIGhlaWdodD0iMTA0IiByeD0iMjkiIGZpbGw9InVybCgjYikiIHN0cm9rZT0idXJsKCNnKSIgc3Ryb2tlLXdpZHRoPSIzIi8+PHBhdGggZD0iTTI1IDEyaDU5IiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIuMTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0iTTI1IDYyVjM1YzEzLTUgMjMtMyAzMSA0IDgtNyAxOC05IDMxLTR2MjdjLTEyLTQtMjItMi0zMSA1LTktNy0xOS05LTMxLTVaIiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48cGF0aCBkPSJNNTYgMzl2MjhNMzMgNDVsMTMgMk02NiA0N2wxMy0yIiBzdHJva2U9IiNiOWVhZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0ibTU2IDE0IDMgOSA5IDMtOSAzLTMgOS0zLTktOS0zIDktM1oiIGZpbGw9IiM5OWYwZDIiLz48L3N2Zz4=') center/contain no-repeat;filter:drop-shadow(0 7px 6px #0006)}
.agent-avatar img{content:url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMTIiIGhlaWdodD0iMTEyIiB2aWV3Qm94PSIwIDAgMTEyIDExMiIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsPSJTdWxlbWFuIEFJIGxvZ28iPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iZyIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjNDdkMmIzIi8+PHN0b3Agb2Zmc2V0PSIuNDgiIHN0b3AtY29sb3I9IiMzYjgyYTAiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM2YzgyYzEiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iYiIgeDI9IjEiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjMzAzNjVjIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMTExYTMyIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3QgeD0iNSIgeT0iNSIgd2lkdGg9IjEwMiIgaGVpZ2h0PSIxMDIiIHJ4PSIyOSIgZmlsbD0iIzA2MGMyMCIvPjxyZWN0IHg9IjMiIHk9IjIiIHdpZHRoPSIxMDYiIGhlaWdodD0iMTA0IiByeD0iMjkiIGZpbGw9InVybCgjYikiIHN0cm9rZT0idXJsKCNnKSIgc3Ryb2tlLXdpZHRoPSIzIi8+PHBhdGggZD0iTTI1IDEyaDU5IiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIuMTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0iTTI1IDYyVjM1YzEzLTUgMjMtMyAzMSA0IDgtNyAxOC05IDMxLTR2MjdjLTEyLTQtMjItMi0zMSA1LTktNy0xOS05LTMxLTVaIiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48cGF0aCBkPSJNNTYgMzl2MjhNMzMgNDVsMTMgMk02NiA0N2wxMy0yIiBzdHJva2U9IiNiOWVhZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0ibTU2IDE0IDMgOSA5IDMtOSAzLTMgOS0zLTktOS0zIDktM1oiIGZpbGw9IiM5OWYwZDIiLz48L3N2Zz4=');border-radius:18px!important}
.agent-avatar{background:transparent!important;box-shadow:none!important}
[data-testid="stSidebar"] .side-brand{display:none!important}
[data-testid="stSidebar"] h2:first-of-type{display:none}
[data-testid="stLogo"]{height:auto!important;max-height:74px!important;width:100%;object-fit:contain;object-position:left}
@media(max-width:600px){.fw-word:before,.mg-head h1:before,.rx-hero h1:before{width:44px;height:44px;margin-right:9px}}
[data-testid="stSidebarLogo"]{width:260px!important;height:52px!important;max-width:100%!important;object-fit:contain;object-position:left}
/* Balanced teal / mint palette and roomier responsive workspace. */
:root{--ink:#edf8f7;--muted:#b4cdce;--line:#385b65;--paper:#0c1b25;--bg:#0c1b25;--surface:#162e39;--accent:#5ee2c1;--accent-ink:#9cf4dc;--accent-soft:#214a48;--grad:linear-gradient(115deg,#47d2b3,#4b83b9);--shadow:0 12px 26px -18px #000, inset 0 1px 0 #ffffff12}
.stApp{background:radial-gradient(ellipse at 0 0,#164f4c66,transparent 48%),radial-gradient(ellipse at 100% 0,#263f6866,transparent 46%),#0c1b25!important;color:#edf8f7!important}
[data-testid="stHeader"]{background:#0c1b25ee!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#122a35,#0e212c)!important;border-color:#385b65!important}
.stApp .block-container{width:100%!important;max-width:1600px!important;padding:2rem clamp(18px,3vw,48px) 3rem!important;min-width:0;box-sizing:border-box}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{color:#f1faf8!important;line-height:1.25!important}
.stApp p,.stApp li{line-height:1.65}
.stApp label,.stApp summary,[data-testid="stCaptionContainer"] p{color:#c5ddde!important}
[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stChatMessage"],.fw-score,.src,.empty,.usage div{background:linear-gradient(145deg,#1c3944,#152c37)!important;border-color:#41636c!important;border-radius:16px!important;box-shadow:0 5px 0 -3px #06121c,0 16px 26px -22px #000,inset 0 1px 0 #ffffff16!important}
[data-testid="stForm"]{padding:clamp(18px,2vw,30px)!important}
[data-testid="stMetric"]{padding:20px!important;min-width:0}
[data-testid="stMetricValue"]{font-size:clamp(24px,2.4vw,38px)!important;overflow-wrap:anywhere}
.fw-head,.mg-head,.brand,.rx-hero{background:linear-gradient(120deg,#16443f,#162f43 68%,#253b59)!important;border-color:#4b746f!important;padding:22px 26px!important;border-radius:18px!important;box-shadow:0 5px 0 -3px #06121c,0 18px 32px -25px #000,inset 0 1px 0 #ffffff1c!important;margin-bottom:24px!important}
.fw-head,.mg-head{grid-template-columns:minmax(0,1.3fr) minmax(280px,1fr)!important;gap:24px!important;align-items:center!important}
.fw-word,.hero-title,.page-title{background:linear-gradient(105deg,#8ff2cf,#81c7ef)!important;background-clip:text!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important}
.fw-head .fw-word,.mg-head h1{font-size:clamp(28px,3vw,40px)!important}
.hero-title{font-size:clamp(30px,3.2vw,44px)!important;line-height:1.2!important}
.rx-hero.big{padding:26px 30px!important}.rx-hero.big h1{font-size:clamp(28px,3vw,40px)!important;margin:10px 0!important}
.rx-hero:before,.rx-hero:after{display:none!important}
.rx-eyebrow{color:#b8f4e2!important;font-size:12px!important;letter-spacing:.12em!important}
.rx-chips{margin-top:14px!important;gap:8px!important}.rx-chips span{padding:6px 11px!important;background:#ffffff09!important;font-size:12px!important}
.fw-word small,.mg-head p,.rx-hero p,.brand-sub,.page-sub,.hero-text,.fw-foot,.mg-foot{color:#c0dadd!important;-webkit-text-fill-color:#c0dadd!important}
.fw-note,.mg-notice{background:#29302e!important;color:#f6dfac!important;border-color:#bd9954!important;font-size:14px!important;line-height:1.6!important}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{background:linear-gradient(145deg,#2a4a54,#1b3641)!important;border-color:#698c93!important;color:#eefafa!important;min-height:44px;font-size:14px!important;padding:8px 16px!important;box-shadow:0 3px 0 #06121c,inset 0 1px 0 #ffffff14!important}
button[kind="primary"],button[kind="primaryFormSubmit"]{background:linear-gradient(110deg,#72e2bc,#58c9cf)!important;color:#092b2c!important;border-color:#a5f4dc!important;font-weight:700!important}
button[kind="primary"] p,button[kind="primaryFormSubmit"] p{color:#092b2c!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input,[data-testid="stChatInput"] textarea{background:#0f2632!important;color:#f1faf8!important;-webkit-text-fill-color:#f1faf8!important;caret-color:#72e2bc!important;font-size:15px!important}
input::placeholder,textarea::placeholder{color:#adc8cd!important;-webkit-text-fill-color:#adc8cd!important}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"],[data-testid="stChatInput"]{background:#0f2632!important;border-color:#527581!important}
[data-testid="stChatInput"]{background:linear-gradient(#0f2632,#0f2632) padding-box,var(--grad) border-box!important;box-shadow:0 10px 22px -17px #5ee2c1!important}
[data-testid="stBottom"]>div,[data-testid="stBottomBlockContainer"]{background:#0c1b25f5!important}
[data-testid="stFileUploaderDropzone"]{background:#1c3944!important;border-color:#6faba8!important;padding:20px!important}
[role="tablist"]{background:#102934!important;border-color:#46666e!important;gap:8px!important;padding:6px!important;max-width:100%!important}
[role="tab"]{min-height:42px!important;padding:8px 18px!important;color:#c7dfe0!important}
[role="tab"][aria-selected="true"]{background:#315c61!important;color:#ecfff9!important}
.fw-src.py,.pill.ok{background:#234b46!important;color:#a7f4dc!important;border-color:#548a7c!important}
.src.cited{background:#1b3b43!important;border-color:#75d7bf!important}.src-id,.src.cited .src-id{background:#335c75!important}
[data-testid="stMarkdownContainer"] code{background:#29454c!important;color:#b4f3e7!important}
.fw-word:before,.mg-head h1:before,.rx-hero h1:before{width:52px!important;height:52px!important;margin-right:12px!important}
[data-testid="stSidebarLogo"]{width:100%!important;max-width:280px!important;height:60px!important}
[data-testid="stHorizontalBlock"]:has(.st-key-connect),[data-testid="stHorizontalBlock"]:has(.st-key-key_form){justify-content:center!important}
[data-testid="stHorizontalBlock"]:has(.st-key-connect)>[data-testid="stColumn"]:not(:has(.st-key-connect)),[data-testid="stHorizontalBlock"]:has(.st-key-key_form)>[data-testid="stColumn"]:not(:has(.st-key-key_form)){display:none!important}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.st-key-connect),[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.st-key-key_form){width:100%!important;flex:1 1 100%!important;max-width:760px!important;min-width:0!important}
:focus-visible{outline-color:#85f0ca!important}
@media(max-width:1100px){.fw-head,.mg-head{grid-template-columns:1fr!important;gap:16px!important}}
@media(max-width:720px){.stApp .block-container{padding:1.25rem 16px 2rem!important}.fw-head,.mg-head,.brand,.rx-hero,.rx-hero.big{padding:20px!important}.fw-head,.mg-head{gap:12px!important}[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:16px!important}[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:0!important;flex:1 1 100%!important;width:100%!important}.fw-word:before,.mg-head h1:before,.rx-hero h1:before{width:42px!important;height:42px!important}.rx-chips span{font-size:12px!important}[role="tablist"]{overflow-x:auto!important}.mg-triage{grid-template-columns:repeat(2,minmax(0,1fr))!important}}

</style>
"""

def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    assets = Path(__file__).resolve().parent / "assets"
    st.logo(str(assets / "wordmark.svg"), icon_image=str(assets / "logo.svg"), size="large")

