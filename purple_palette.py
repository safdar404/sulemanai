"""Violet, magenta and sunset-gold presentation palette."""
import streamlit as st

CSS = """<style>
:root{--ink:#fff8ff;--text:#fff8ff;--navy:#fff8ff;--muted:#e1cfe9;--line:#825894;--paper:#35174c;--bg:#35174c;--surface:#48245c;--card:#48245c;--accent:#ffbf62;--accent-ink:#ffe0a5;--accent-soft:#65406b;--teal:#f0a8d5;--deep:#ffd9a0;--violet:#bc8ae8;--grad:linear-gradient(110deg,#e43a9d,#873ec1);--shadow:0 14px 28px -20px #14071e,inset 0 1px 0 #ffffff1a}
.stApp{color:#fff8ff!important;background:radial-gradient(ellipse at 100% 0,#e43a9d55,transparent 45%),radial-gradient(ellipse at 0 100%,#ef7b3840,transparent 48%),linear-gradient(150deg,#51267a,#71348b 55%,#522460)!important;background-attachment:fixed!important}
[data-testid="stHeader"]{background:#38174cdd!important;backdrop-filter:blur(12px)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#351942,#432052)!important;border-right:1px solid #8b5b9b!important}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{color:#fffaff!important}
.stApp label,.stApp summary,[data-testid="stCaptionContainer"] p,.pz-muted{color:#e8d7ee!important}
.fw-head,.mg-head,.brand,.rx-hero,.mm-hero,.pz-hero{background:radial-gradient(ellipse at 100% 0,#df3a9d66,transparent 50%),linear-gradient(115deg,#642b88,#843390 60%,#a32d81)!important;border:1px solid #bb85c3!important;box-shadow:0 5px 0 -3px #271034,0 18px 30px -22px #1a0826,inset 0 1px 0 #ffffff25!important;border-radius:20px!important}
.fw-word,.hero-title,.page-title,.rx-hero h1 span,.mm-hero h1,.pz-hero h1{background:linear-gradient(100deg,#fffaff,#ffe4b0)!important;background-clip:text!important;-webkit-background-clip:text!important;color:#fffaff!important;-webkit-text-fill-color:transparent!important}
.fw-word small,.mg-head p,.rx-hero p,.mm-hero p,.pz-hero p,.brand-sub,.page-sub,.hero-text,.fw-foot,.mg-foot{color:#f0dfef!important;-webkit-text-fill-color:#f0dfef!important}
[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"],[data-testid="stChatMessage"],.fw-score,.src,.empty,.usage div,.pz-answer,.pz-stat{background:linear-gradient(145deg,#512b65,#3e214f)!important;border:1px solid #91669f!important;box-shadow:0 5px 0 -3px #271034,0 16px 28px -23px #190822,inset 0 1px 0 #ffffff18!important;border-radius:16px!important;color:#fff8ff!important}
[data-testid="stMetricValue"],[data-testid="stMetricLabel"],.fw-num b,.pz-answer h3{color:#fff8ff!important}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{background:linear-gradient(145deg,#704681,#4d2b61)!important;color:#fff8ff!important;border:1px solid #bc93c8!important;box-shadow:0 3px 0 #291136,inset 0 1px 0 #ffffff20!important}
button[kind="primary"],button[kind="primaryFormSubmit"]{background:linear-gradient(100deg,#ffac35,#ffda8a)!important;color:#402044!important;border-color:#ffe6b5!important;font-weight:700!important}
button[kind="primary"] p,button[kind="primaryFormSubmit"] p{color:#402044!important}
@media(hover:hover){.stButton>button:not(:disabled):hover,.stDownloadButton>button:not(:disabled):hover{border-color:#ffe3a4!important;box-shadow:0 5px 0 #291136,0 12px 22px -15px #ffad5799!important}}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input,[data-testid="stChatInput"] textarea{background:#311b41!important;color:#fff8ff!important;-webkit-text-fill-color:#fff8ff!important;caret-color:#ffd189!important}
input::placeholder,textarea::placeholder{color:#d6bcdf!important;-webkit-text-fill-color:#d6bcdf!important}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="textarea"]{background:#311b41!important;border-color:#a27bab!important;color:#fff8ff!important}
[data-testid="stChatInput"]{background:linear-gradient(#311b41,#311b41) padding-box,linear-gradient(110deg,#ffb443,#e43a9d,#b48ae4) border-box!important;border-color:transparent!important;box-shadow:0 14px 24px -19px #ffc868!important}
[data-testid="stBottom"]>div,[data-testid="stBottomBlockContainer"]{background:#381c49f5!important}
[data-testid="stFileUploaderDropzone"]{background:#512f65!important;border-color:#c697d1!important}
[role="tablist"]{background:#351d46!important;border-color:#94639e!important}
[role="tab"]{background:transparent!important;color:#eddaef!important;border-color:#94639e!important}
[role="tab"][aria-selected="true"]{background:linear-gradient(110deg,#a83389,#76399b)!important;color:white!important;border-radius:10px!important}
[role="tab"][aria-selected="true"] p{color:#fff!important}
.fw-note,.mg-notice{background:#4c334b!important;color:#ffe3b0!important;border-color:#e4b771!important}.mg-notice b{color:#ffbdc7!important}
.pill,.pill.ok,.pz-chip,.rx-chips span,.mm-chip{background:#563167!important;color:#fff2f7!important;border-color:#b47abe!important}
.fw-src.py{background:#573866!important;color:#ffe0a5!important;border-color:#bb91b9!important}.fw-src.ai{background:#63415e!important;color:#ffe2aa!important}
.src.cited,.cite{background:#563464!important;color:#f9eafa!important;border-color:#dfb3d4!important}.cite b{color:#ffe3aa!important}.cite small{color:#e7d4eb!important}
.src-id,.src.cited .src-id{background:#9b3f95!important;color:#fff!important}
[data-testid="stMarkdownContainer"] code{background:#65406b!important;color:#ffe3ad!important}
.p-high,.b-ok{color:#a8f0c9!important;background:#26483f!important}.p-partial,.b-warn{color:#ffe0a1!important;background:#59432f!important}.p-none,.b-bad{color:#ffc2cf!important;background:#5c2c41!important}.p-flag{color:#eeddf0!important;background:#5d3c6b!important}
.mg-triage div:not(.on){background:#482a59!important;color:#ead7ee!important}
.rx-eyebrow{color:#ffe0ad!important}.rx-stat{background:#ffffff0d!important;border-color:#c99ccf!important}.rx-stat small{color:#eed7ed!important}
.side-brand span,.side-brand b{color:#f9eafa!important}.side-brand b em{color:#ffdba1!important}
[data-testid="stAlert"]{background:#452958!important;border:1px solid #aa7cba!important;color:#fff3fc!important}
[data-testid="stAlert"] p,[data-testid="stAlert"] li,[data-testid="stAlert"] a{color:#fff3fc!important}
mark{background:#80516c!important;color:#fff4d6!important}
:focus-visible{outline:3px solid #ffd58a!important;outline-offset:3px!important}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style>"""

def apply_palette():
    st.markdown(CSS, unsafe_allow_html=True)
