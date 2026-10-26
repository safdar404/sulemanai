import base64
import html
import hashlib
import io
import json
import math
import mimetypes
import re
import time
import urllib.request
import uuid
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from openai import (OpenAI, AuthenticationError, NotFoundError, RateLimitError, APIConnectionError,
                    BadRequestError, PermissionDeniedError)
from plotly.subplots import make_subplots
from PIL import Image, ImageDraw

# ---------- App name ----------
APP_NAME = "Suleman AI"

# ---------- Page setup ----------
BASE_DIR = Path(__file__).parent

# ---------- Logo: rainbow AI-agent robot (assets/logo.svg + PNG copy for avatars) ----------
ASSETS_DIR = BASE_DIR / "assets"
LOGO_FILE = ASSETS_DIR / "agent_logo.png"
LOGO_B64 = base64.b64encode(LOGO_FILE.read_bytes()).decode() if LOGO_FILE.exists() else ""
ASSISTANT_AVATAR = str(LOGO_FILE) if LOGO_FILE.exists() else "🤖"

st.set_page_config(page_title=APP_NAME, page_icon=str(LOGO_FILE) if LOGO_B64 else "🤖",
                   layout="wide", initial_sidebar_state="expanded")

# Each API key gets its own private workspace folder (chats + media), so visitors of the
# hosted app never see each other's history. Paths are set once the key is entered.
DATA_ROOT = BASE_DIR / "user_data"
HISTORY_FILE = IMAGES_DIR = MEDIA_DIR = MEDIA_INDEX = None


def set_workspace(api_key):
    global HISTORY_FILE, IMAGES_DIR, MEDIA_DIR, MEDIA_INDEX
    # A configured server key may serve many visitors; never share their history.
    if api_key == _secret_key():
        if "workspace_id" not in st.session_state:
            st.session_state.workspace_id = uuid.uuid4().hex
        workspace_id = st.session_state.workspace_id
    else:
        workspace_id = hashlib.sha256(api_key.encode()).hexdigest()
    ws = DATA_ROOT / workspace_id
    HISTORY_FILE = ws / "chat_history.json"
    IMAGES_DIR = ws / "chat_images"
    MEDIA_DIR = ws / "media"
    MEDIA_INDEX = MEDIA_DIR / "index.json"
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_MODELS = ["gpt-image-2", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst", "gpt-image-1.5", "gpt-image-1-mini"]
VIDEO_MODEL = "gemini-omni-1.1-flash"

IMAGE_STYLES = {
    "None": "",
    "Photorealistic": ", photorealistic, natural lighting, highly detailed",
    "Digital art": ", vibrant digital art, clean shapes, rich colours",
    "3D render": ", 3D render, soft studio lighting, glossy materials",
    "Watercolour": ", soft watercolour painting, paper texture",
    "Cartoon": ", cheerful cartoon illustration, bold outlines",
    "Cinematic": ", cinematic still, dramatic lighting, shallow depth of field",
}
VIDEO_STYLES = {
    "None": "",
    "Cinematic": " Cinematic look, smooth camera movement, dramatic lighting.",
    "Animated / cartoon": " Bright 3D animated cartoon style.",
    "Documentary": " Realistic documentary footage, natural light.",
    "Dreamy": " Soft, dreamy, pastel colours, slow motion.",
}

PAGES = ["💬 Chat", "🧰 AI Toolkit", "🎨 Media Studio", "📊 Data Studio", "📐 Trigonometry", "🎬 Animations"]
COLORS = ["#ff3d6e", "#ff9f1c", "#ffe14d", "#2ee59d", "#2bb8ff", "#a64dff"]
NONE = "(none)"

STARTERS = [
    ("💡 Explain a topic", "Explain how the internet works in simple words."),
    ("✉️ Write an email", "Help me write a polite email asking my manager for a day off."),
    ("🧠 Brainstorm ideas", "Give me 10 creative weekend project ideas I can finish in 2 days."),
    ("🎨 Create an image", "Generate an image of a cute yellow duckling astronaut floating among colourful planets, vibrant digital art"),
    ("💻 Debug code", "Explain this Python error and how to fix it: TypeError: 'NoneType' object is not subscriptable"),
    ("🗺️ Plan a trip", "Plan a 3-day budget trip to Lahore with food spots and a day-by-day schedule."),
]

# 🎭 Personas: quick presets for the assistant's personality
PERSONAS = {
    "🤖 Helpful assistant": "You are a helpful assistant. Give clear, practical answers.",
    "🧑‍🏫 Patient tutor": "You are a patient tutor. Explain step by step with simple examples, then check understanding with one short question.",
    "💻 Senior coder": "You are a senior software engineer. Give correct, idiomatic code with brief explanations and point out edge cases.",
    "✍️ Creative writer": "You are a creative writer. Write vivid, original and engaging text with a strong voice.",
    "📈 Business analyst": "You are a sharp business analyst. Be structured, data-driven and concise; use headings and bullet points.",
    "😄 Fun buddy": "You are a cheerful, witty friend. Keep answers short, friendly and sprinkle in fitting emojis.",
    "🛠️ Custom…": None,
}

# 🧰 One-click AI tools (AI Toolkit page)
TOOLS = {
    "📝 Summarize": ("Summarize the text below in 5 short bullet points, then a one-line TL;DR.", "Paste an article, notes or a long message…"),
    "🌍 Translate": ("Translate the text below into {lang}. Keep the meaning and tone; output only the translation.", "Text to translate…"),
    "✨ Rewrite tone": ("Rewrite the text below in a {tone} tone. Keep it about the same length.", "Text to rewrite…"),
    "✅ Fix grammar": ("Correct the grammar, spelling and punctuation of the text below. Output the corrected text, then list the main fixes.", "Text to proofread…"),
    "🧒 Explain like I'm 5": ("Explain the topic below so a 5-year-old would understand, using a fun analogy.", "e.g. black holes, inflation, blockchain…"),
    "❓ Make a quiz": ("Create a 5-question multiple-choice quiz (A–D) about the topic or text below. Put the answer key at the end.", "Topic or text for the quiz…"),
    "#️⃣ Social post": ("Write 3 catchy social media post options (with hashtags and emojis) about the text below.", "What is the post about?"),
    "💻 Explain code": ("Explain what the code below does, step by step, and suggest one improvement.", "Paste code…"),
}
LANGUAGES = ["Urdu", "English", "Arabic", "Spanish", "French", "German", "Chinese", "Hindi", "Turkish", "Punjabi"]
TONES = ["professional", "friendly", "persuasive", "funny", "formal", "simple and clear", "poetic"]

# Added to the assistant instructions so the chat model never says "I can't create images".
APP_CAPABILITIES = (
    f"\n\nYou are {APP_NAME}. This app has built-in image and video generation: when the user asks "
    "for a picture, image, drawing, logo or video, the app creates it automatically. Never say you "
    "cannot create or display images. If an image request still reaches you, tell the user to type "
    "`/image` followed by a description (or `/video` for a video)."
)



# ---------- Logo ----------
def logo(size=56, uid="a", status=False):
    """Agent avatar (robot logo) inside a spinning rainbow ring."""
    dot = '<span class="agent-dot"></span>' if status else ""
    img = (f'<img src="data:image/png;base64,{LOGO_B64}" alt="{APP_NAME} agent"/>' if LOGO_B64
           else f'<span style="font-size:{size // 2}px;line-height:{size}px;display:block;text-align:center">🤖</span>')
    return f'<div class="agent-avatar" style="width:{size}px;height:{size}px">{img}{dot}</div>'


# ---------- Theme ----------
from rainbow_theme import apply_theme
apply_theme()



def brand_header(chips=True):
    right = ""
    if chips:
        right = ('<div class="brand-right"><span class="chip">💬 Chat</span><span class="chip">🎨 Images</span>'
                 '<span class="chip">🎬 Video</span><span class="chip">📊 Data</span><span class="chip">🧰 Tools</span></div>')
    st.markdown(
        f'<div class="brand">{logo(52, "h", status=True)}'
        f'<div><div class="brand-name">Suleman <em>AI</em></div>'
        '<div class="brand-sub">Your rainbow AI agent studio</div>'
        f'<div class="agent-status"><span class="live"></span>Agent online</div></div>{right}</div>',
        unsafe_allow_html=True,
    )


def page_heading(title, subtitle):
    emoji, _, text = title.partition(" ")  # keep the emoji outside the gradient text
    st.markdown(f'<div class="page-title"><span class="emo">{emoji}</span>{text}</div>'
                f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)


# ---------- Chart styling ----------
def style(fig, height=480):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e8ecff"),
        colorway=COLORS,
        height=height,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.35)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.35)")
    return fig


def style_3d(fig, height=600):
    style(fig, height)
    axis = dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="rgba(255,255,255,0.3)")
    fig.update_scenes(xaxis=axis, yaxis=axis, zaxis=axis)
    return fig


def play_menu(duration=50, redraw=False):
    return [dict(
        type="buttons", showactive=False, direction="left",
        x=0, y=1.14, xanchor="left", yanchor="top",
        bgcolor="#7c3aed", bordercolor="#a78bfa", font=dict(color="#ffffff"),
        buttons=[
            dict(label="▶ Play", method="animate",
                 args=[None, dict(frame=dict(duration=duration, redraw=redraw),
                                  fromcurrent=True, transition=dict(duration=0), mode="immediate")]),
            dict(label="⏸ Pause", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False),
                                    transition=dict(duration=0), mode="immediate")]),
        ],
    )]


# ---------- Storage ----------
def load_store():
    if not HISTORY_FILE.exists():
        return {"conversations": {}}
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"conversations": {}}
    if isinstance(data, list):  # old single-chat format
        store = {"conversations": {}}
        if data:
            now = datetime.now().isoformat()
            store["conversations"][uuid.uuid4().hex[:8]] = {
                "title": "Earlier chat", "created": now, "updated": now, "messages": data,
            }
        return store
    return data


def save_store():
    HISTORY_FILE.write_text(
        json.dumps(st.session_state.store, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def delete_images(messages):
    for m in messages:
        for name in m.get("images", []) + m.get("videos", []):
            (IMAGES_DIR / name).unlink(missing_ok=True)


def now_label():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def make_title(text):
    text = " ".join(text.split())
    return text[:40] + ("…" if len(text) > 40 else "")


def group_label(iso_time):
    days = (date.today() - datetime.fromisoformat(iso_time).date()).days
    if days <= 0:
        return "Today"
    if days == 1:
        return "Yesterday"
    if days <= 7:
        return "Previous 7 days"
    return "Older"


def to_markdown(conv):
    lines = [f"# {conv['title']}", ""]
    for m in conv["messages"]:
        who = "You" if m["role"] == "user" else APP_NAME
        lines += [f"**{who}:**", ""]
        if m.get("images"):
            lines += [f"*[{len(m['images'])} image(s) attached]*", ""]
        lines += [m["content"], ""]
    return "\n".join(lines)


# ---------- Screen 1: API key ----------
def check_key(key):
    """Quick, free call to confirm the key works before opening the studio."""
    try:
        OpenAI(api_key=key, timeout=20.0).models.list()
        return None
    except AuthenticationError:
        return "🔒 That key was not accepted by OpenAI. Check it and try again."
    except APIConnectionError:
        return "🌐 Could not reach OpenAI. Check your connection and try again."
    except Exception:
        return None  # other errors (e.g. restricted key) — let the user in and show errors per request


def _secret_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""


if "api_key" not in st.session_state and _secret_key():
    st.session_state.api_key = _secret_key()

if "api_key" not in st.session_state:
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        brand_header(chips=False)
        st.markdown(
            '<div class="hero-title">Connect to start chatting <span class="emo">✨</span></div>'
            '<div class="hero-text">Enter your OpenAI API key to wake up your AI agent.</div>'
            '<div class="feature-grid">'
            '<div><b>💬 Smart chat</b>Personas, vision & streaming</div>'
            '<div><b>🎨 Media studio</b>Images & videos from text</div>'
            '<div><b>🧰 AI toolkit</b>Summarize, translate, quiz…</div>'
            '<div><b>📊 Data studio</b>Charts + AI insights</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.form("key_form"):
            key = st.text_input("🔑 OpenAI API key", type="password", placeholder="sk-...")
            start = st.form_submit_button("🚀 Open studio", type="primary")
        if start:
            key = key.strip()
            if not key:
                st.warning("Enter your API key to continue.")
            else:
                with st.spinner("Checking your key…"):
                    problem = check_key(key)
                if problem:
                    st.error(problem)
                else:
                    st.session_state.api_key = key
                    st.rerun()
        st.caption("🔐 Your key is held in server session memory. Chat and media files are stored on this "
                   "app server and may be lost when it restarts. Use your own key; do not share it.")
    st.stop()

set_workspace(st.session_state.api_key)

# ---------- Session state ----------
if "store" not in st.session_state:
    st.session_state.store = load_store()
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "page" not in st.session_state:
    st.session_state.page = PAGES[0]

convs = st.session_state.store["conversations"]
if st.session_state.current_id not in convs:
    st.session_state.current_id = None


# ---------- Callbacks ----------
def open_chat(cid):
    st.session_state.current_id = cid
    st.session_state.page = PAGES[0]


def new_chat():
    st.session_state.current_id = None
    st.session_state.page = PAGES[0]


def queue_prompt(text):
    st.session_state.queued = text


def regenerate():
    conv = convs[st.session_state.current_id]
    if conv["messages"] and conv["messages"][-1]["role"] == "assistant":
        delete_images([conv["messages"].pop()])
        st.session_state.regen = True


def rename_chat():
    # FIX: one rename box per chat, so switching chats shows the right title
    box_key = f"rename_box_{st.session_state.current_id}"
    new_title = st.session_state.get(box_key, "").strip()
    if new_title:
        convs[st.session_state.current_id]["title"] = new_title
        save_store()


def toggle_pin():
    conv = convs[st.session_state.current_id]
    conv["pinned"] = not conv.get("pinned", False)
    save_store()


def delete_chat():
    conv = convs.pop(st.session_state.current_id, None)
    if conv:
        delete_images(conv["messages"])
    st.session_state.current_id = None
    save_store()


def clear_all():
    for conv in convs.values():
        delete_images(conv["messages"])
    convs.clear()
    st.session_state.current_id = None
    save_store()


# ---------- Sidebar ----------
def change_key():
    # Clear queued prompts, uploads, toolkit results and credentials together.
    st.session_state.clear()


with st.sidebar:
    st.radio("Workspace", PAGES, key="page", label_visibility="collapsed")
    st.button("✨ New chat", on_click=new_chat, type="primary")

    n_msgs = sum(len(c["messages"]) for c in convs.values())
    n_media = len(json.loads(MEDIA_INDEX.read_text(encoding="utf-8"))) if MEDIA_INDEX.exists() else 0
    st.markdown(f'<div class="side-stats"><div><b>{len(convs)}</b><small>💬 chats</small></div>'
                f'<div><b>{n_msgs}</b><small>✉️ messages</small></div>'
                f'<div><b>{n_media}</b><small>🖼️ media</small></div></div>', unsafe_allow_html=True)

    search = st.text_input("Search", placeholder="🔍 Search chats",
                           label_visibility="collapsed").strip().lower()

    items = sorted(convs.items(), key=lambda kv: (kv[1].get("pinned", False), kv[1]["updated"]), reverse=True)
    if search:
        items = [
            (cid, c) for cid, c in items
            if search in c["title"].lower()
            or any(search in m["content"].lower() for m in c["messages"])
        ]

    with st.container(key="history"):
        if not items:
            st.caption("No chats found." if search else "Your chats will appear here.")
        last_group = None
        for cid, c in items:
            group = "📌 Pinned" if c.get("pinned") else group_label(c["updated"])
            if group != last_group:
                st.markdown(f'<div class="group-label">{group}</div>', unsafe_allow_html=True)
                last_group = group
            st.button(
                f"{'📌' if c.get('pinned') else '💬'} {c['title']}", key=f"open_{cid}",
                on_click=open_chat, args=(cid,),
                type="primary" if cid == st.session_state.current_id else "secondary",
            )

    st.divider()

    with st.expander("🎭 Persona & model", expanded=False):
        persona = st.selectbox("Persona", list(PERSONAS), key="persona")
        if PERSONAS[persona] is None:
            instructions = st.text_area("Custom instructions", key="custom_instructions",
                                        value="You are a helpful assistant. Give clear, practical answers.")
        else:
            instructions = PERSONAS[persona]
            st.caption(f"🗒️ {instructions}")
        model = st.selectbox("Chat model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1", "Other…"],
                             key="model_pick", help="Use a vision model (e.g. gpt-4o-mini) to chat about images.")
        if model == "Other…":
            model = st.text_input("Model name", value="gpt-4o-mini", key="model_custom").strip()
        temperature = st.slider("🌡️ Creativity", 0.0, 2.0, 1.0, 0.1,
                                help="Lower = focused, higher = creative. Some models only accept 1.0.")
        reply_len = st.select_slider("📏 Reply length", ["Short", "Normal", "Detailed"], value="Normal")
        if reply_len == "Short":
            instructions += " Keep answers brief: at most a few sentences."
        elif reply_len == "Detailed":
            instructions += " Give thorough, detailed answers with examples."
        language = st.selectbox("🌐 Reply language", ["Auto", "English", "Urdu", "Roman Urdu", "Arabic", "Hindi"])
        if language != "Auto":
            instructions += f" Always reply in {language}."

    with st.expander("⚙️ Settings"):
        st.selectbox("Image model for chat", IMAGE_MODELS, key="chat_img_model",
                     help="Used when you ask for a picture in Chat (e.g. “generate an egg image”).")
        st.text_input("Google Gemini API key (for videos)", type="password", key="gemini_key",
                      help="Videos are made with Google's Gemini Omni Flash. "
                           "Get a free key at aistudio.google.com/apikey")
        st.button("🔑 Change API key", on_click=change_key)

    with st.expander("🗑️ Clear all chats"):
        confirm_all = st.checkbox("Yes, delete every saved chat")
        st.button("Delete all", disabled=not confirm_all, on_click=clear_all)

    st.caption("🔐 Private workspace for this API key")


# ---------- AI helpers ----------
def friendly_error(e, model_name=None):
    name = model_name or model
    if type(e).__module__.startswith("google"):
        return f"Google API error: {getattr(e, 'message', None) or e}"
    if isinstance(e, (RuntimeError, TimeoutError)):
        return str(e)
    if isinstance(e, AuthenticationError):
        return "Your API key was not accepted. Use “Change API key” in Settings."
    if isinstance(e, PermissionDeniedError):
        return (f"Your OpenAI account can't use “{name}” yet. Image models may need "
                "organization verification at platform.openai.com.")
    if isinstance(e, BadRequestError):
        return f"The request was rejected (it may break a content rule): {getattr(e, 'message', e)}"
    if isinstance(e, NotFoundError):
        return f"The model “{name}” is not available on your account. Try another one."
    if isinstance(e, RateLimitError):
        return "Rate limit or quota reached. Check your OpenAI billing, then try again."
    if isinstance(e, APIConnectionError):
        return "Could not reach OpenAI. Check your internet connection."
    return f"No reply received: {e}"


def stream_answer(messages):
    """Yield text pieces from OpenAI as they arrive."""
    client = OpenAI(api_key=st.session_state.api_key, timeout=90.0)
    params = dict(
        model=model,
        # FIX: the model is told the app can make images, so it stops saying "I can't create images"
        messages=[{"role": "system", "content": instructions + APP_CAPABILITIES}] + messages,
        stream=True,
    )
    if temperature != 1.0:
        params["temperature"] = temperature
    for chunk in client.chat.completions.create(**params):
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def api_messages(conv):
    """Convert saved messages to the OpenAI format, including any images."""
    out = []
    for m in conv["messages"]:
        paths = [IMAGES_DIR / n for n in m.get("images", []) if (IMAGES_DIR / n).exists()]
        if m["role"] == "user" and paths:
            parts = [{"type": "text", "text": m["content"]}]
            for p in paths:
                mime = mimetypes.guess_type(p.name)[0] or "image/png"
                b64 = base64.b64encode(p.read_bytes()).decode()
                parts.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
            out.append({"role": "user", "content": parts})
        else:
            out.append({"role": m["role"], "content": m["content"]})
    return out


def with_thinking(pieces, placeholder):
    """Show the thinking dots until the first piece of the answer arrives."""
    first = True
    for piece in pieces:
        if first:
            placeholder.empty()
            first = False
        yield piece


def generate_reply(conv):
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        thinking = st.empty()
        thinking.markdown(f'<div class="thinking">{APP_NAME} is thinking'
                          '<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
        try:
            answer = st.write_stream(with_thinking(stream_answer(api_messages(conv)), thinking))
            if not answer or not str(answer).strip():
                raise ValueError("The model returned an empty answer.")
        except Exception as e:
            thinking.empty()
            st.error(friendly_error(e))
            return False
    conv["messages"].append({"role": "assistant", "content": answer, "time": now_label()})
    conv["updated"] = datetime.now().isoformat()
    save_store()
    return True


def show_message(msg):
    avatar = "🙂" if msg["role"] == "user" else ASSISTANT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        for name in msg.get("images", []):
            path = IMAGES_DIR / name
            if path.exists():
                st.image(str(path), width=320 if msg["role"] == "user" else 460)
        for name in msg.get("videos", []):
            path = IMAGES_DIR / name
            if path.exists():
                st.video(str(path))
        st.markdown(msg["content"])
        if msg.get("time"):
            st.markdown(f'<div class="msg-meta">🕒 {msg["time"]}</div>', unsafe_allow_html=True)



# =====================================================================
#  MEDIA ENGINE: text→image (OpenAI), text/image→video (Google Gemini Omni Flash)
# =====================================================================
def load_media():
    if MEDIA_INDEX.exists():
        try:
            return json.loads(MEDIA_INDEX.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_media(items):
    MEDIA_INDEX.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def add_media(kind, data, ext, prompt, model_name):
    name = f"{kind}_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}.{ext}"
    (MEDIA_DIR / name).write_bytes(data)
    items = load_media()
    items.insert(0, {"kind": kind, "file": name, "prompt": prompt, "model": model_name,
                     "created": datetime.now().isoformat()})
    save_media(items)
    return name


def delete_media(name):
    (MEDIA_DIR / name).unlink(missing_ok=True)
    save_media([m for m in load_media() if m["file"] != name])


def generate_images(prompt, img_model="gpt-image-2", size="auto", quality="auto", n=1):
    client = OpenAI(api_key=st.session_state.api_key, timeout=300.0)
    params = dict(model=img_model, prompt=prompt, n=n)
    if size != "auto":
        params["size"] = size
    if quality != "auto":
        params["quality"] = quality
    result = client.images.generate(**params)
    images = []
    for item in result.data or []:
        if getattr(item, "b64_json", None):
            images.append(base64.b64decode(item.b64_json))
        elif getattr(item, "url", None):
            images.append(urllib.request.urlopen(item.url, timeout=60).read())
    if not images:
        raise RuntimeError("No image came back. Try rewording the description.")
    return images


def prepare_image(raw, max_side=2048):
    """Shrink large photos and convert to JPEG so uploads stay small."""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"


def generate_video(prompt, images=None, aspect="16:9", resolution="720p", task=None, video_model=VIDEO_MODEL):
    try:
        from google import genai as google_genai
    except ImportError:
        raise RuntimeError("Video needs Google's package. Run: python -m pip install -U google-genai")

    key = (st.session_state.get("gemini_key") or "").strip()
    if not key:
        raise RuntimeError("Add your Google Gemini API key in ⚙️ Settings (sidebar) to create videos.")

    client = google_genai.Client(api_key=key)
    if not hasattr(client, "interactions"):
        raise RuntimeError("Your google-genai package is too old. Run: python -m pip install -U google-genai")

    if images:
        content = [{"type": "image", "data": b64, "mime_type": mime} for b64, mime in images]
        content.append({"type": "text", "text": prompt})
    else:
        content = prompt

    fmt = {"type": "video", "aspect_ratio": aspect, "resolution": resolution}
    if resolution in ("1080p", "4k"):
        fmt["delivery"] = "uri"  # large files come back as a download link
    kwargs = dict(model=video_model, input=content, response_format=fmt)
    if task:
        kwargs["generation_config"] = {"video_config": {"task": task}}

    interaction = client.interactions.create(**kwargs)
    out = getattr(interaction, "output_video", None)
    if out is None:
        raise RuntimeError("No video came back. The prompt or image may have been blocked by safety filters.")
    if getattr(out, "data", None):
        return base64.b64decode(out.data)

    uri = getattr(out, "uri", None)
    if not uri:
        raise RuntimeError("The video response was empty. Please try again.")
    file_id = uri.split("/files/")[-1].split(":")[0].split("?")[0]
    deadline = time.time() + 600
    while True:
        info = client.files.get(name=f"files/{file_id}")
        state = str(getattr(info.state, "name", info.state))
        if "ACTIVE" in state:
            break
        if "FAILED" in state:
            raise RuntimeError("Google could not finish processing the video.")
        if time.time() > deadline:
            raise TimeoutError("The video took too long to process. Please try again.")
        time.sleep(5)
    data = client.files.download(file=info)
    if not data:
        tmp = MEDIA_DIR / f"_download_{uuid.uuid4().hex[:6]}.mp4"
        client.files.download(file=uri, destination=str(tmp))
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
    return data


# =====================================================================
#  INTENT DETECTION  (FIX: plain-English image / video requests)
#  Before, only "/image ..." made a picture. Now "generate an egg image",
#  "generate the CAT picture", "draw a tiger", "make a logo for my bakery",
#  "picture of a sunset", "make another one" … all go to the image model.
# =====================================================================
GENERIC_IMG_NOUNS = r"(?:images?|pictures?|pics?|photos?|photographs?|imgs?|snaps?)"
OTHER_IMG_NOUNS = (
    r"(?:drawings?|illustrations?|paintings?|artworks?|wallpapers?|logos?|posters?|portraits?|"
    r"sketch(?:es)?|renders?|icons?|avatars?|cartoons?|clip ?art|(?:digital|pixel|ai|fan|concept|line) art)"
)
IMG_NOUNS = rf"(?:{GENERIC_IMG_NOUNS}|{OTHER_IMG_NOUNS})"
VID_NOUNS = r"(?:videos?|animations?|clips?|movies?|animated (?:images?|pictures?))"
CREATE_VERBS = (
    r"(?:generate|create|make|draw|paint|design|render|produce|show|give|send|sketch|"
    r"illustrate|imagine|visuali[sz]e|craft|build|get)"
)
SOLO_VERBS = r"(?:draw|paint|sketch|illustrate|imagine|visuali[sz]e)"
NOT_MEDIA_HINTS = re.compile(
    r"\b(how (?:do|can|to|would|should)|python|code|script|function|library|api key|program|"
    r"explain|what is|what's|why|difference|tutorial|steps to|ways to|conclusions?|attention|"
    r"in this (?:image|picture|photo)|this (?:image|picture|photo)|the attached|describe)\b",
    re.I,
)
PRONOUN_SUBJECTS = {
    "", "it", "this", "that", "one", "them", "same", "the same", "another", "another one",
    "one more", "again", "it again", "more", "new one", "a new one", "same thing", "a", "an", "the",
}
FOLLOW_UP = re.compile(
    r"^\s*(?:please\s+)?(?:make|generate|create|draw|do|give me|show me|try)?\s*"
    r"(?:another(?: one)?|one more|it again|again|a new one|more|a different one)\b", re.I)
_LEAD = re.compile(
    r"^\s*(?:hey|hi|hello|ok|okay|please|pls|plz|kindly|now|so|also|and|then|can you|could you|"
    r"would you|will you|can u|could u|i want you to|i want|i need|i would like|i'd like|"
    r"let's|lets|go ahead and|just|quickly)\b[\s,!.:]*",
    re.I,
)


def extract_subject(text, kind):
    """'generate an egg image' -> 'an egg';  'generate the CAT picture' -> 'cat'."""
    t = text.strip()
    prev = None
    while prev != t:
        prev = t
        t = _LEAD.sub("", t)
    t = re.sub(rf"\b{CREATE_VERBS}\b", " ", t, count=1, flags=re.I)
    t = re.sub(r"^\s*(?:me|us)\b", " ", t, flags=re.I)
    nouns = GENERIC_IMG_NOUNS if kind == "image" else rf"(?:{VID_NOUNS}|{GENERIC_IMG_NOUNS})"
    t = re.sub(
        rf"\b(?:an?|the|some|one|another|\d+)?\s*{nouns}\s+(?:of|for|showing|that shows|depicting|with|about|on)\b",
        " ", t, count=1, flags=re.I,
    )
    t = re.sub(rf"\b{nouns}\b", " ", t, flags=re.I)
    t = re.sub(r"\b(?:please|pls|plz|for me|now|thanks|thank you)\b", " ", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" .,!?:;-\"'")
    t = re.sub(r"^(?:the|of|for)(?:\s+|$)", "", t, flags=re.I).strip()
    if t.isupper():
        t = t.lower()
    return "" if t.lower() in PRONOUN_SUBJECTS else t


def detect_intent(text):
    """Return ("image" | "video" | "chat", subject)."""
    t = (text or "").strip()
    m = re.match(r"^/(?:image|img|draw|pic|picture|imagine)\b\s*(.*)$", t, re.I | re.S)
    if m:
        return "image", m.group(1).strip()
    m = re.match(r"^/(?:video|animate)\b\s*(.*)$", t, re.I | re.S)
    if m:
        return "video", m.group(1).strip()
    if not t or len(t) > 400:
        return "chat", ""
    low = t.lower()
    if NOT_MEDIA_HINTS.search(low):
        return "chat", ""
    if re.search(rf"\b{CREATE_VERBS}\b(?:\W+[\w'-]+){{0,10}}?\W+{VID_NOUNS}\b", low) or re.match(
            rf"^(?:an?\s+)?{VID_NOUNS}\s+of\b", low):
        return "video", extract_subject(t, "video")
    if (re.search(rf"\b{CREATE_VERBS}\b(?:\W+[\w'-]+){{0,10}}?\W+{IMG_NOUNS}\b", low)
            or re.match(rf"^(?:an?\s+)?{IMG_NOUNS}\s+of\b", low)
            or re.match(rf"^(?:please\s+|can you\s+|could you\s+)?{SOLO_VERBS}\b", low)):
        return "image", extract_subject(t, "image")
    return "chat", ""


def _prompt_of(msg):
    """Prompt used for an earlier generated image/video (also works for older saved chats)."""
    if msg.get("prompt"):
        return msg["prompt"]
    if msg["role"] == "assistant" and (msg.get("images") or msg.get("videos")):
        m = re.search(r"for: \*(.+)\*\s*$", msg.get("content", ""), re.S)
        if m:
            return m.group(1).strip()
    return None


def last_media(conv):
    """(kind, prompt) of the most recent generated image/video in this chat."""
    for m in reversed(conv["messages"][:-1]):
        p = _prompt_of(m)
        if p:
            return ("video" if m.get("videos") else "image"), p
    return None, None


def resolve_prompt(conv, subject):
    """Fill in 'it' / 'another one' / 'the picture' from earlier messages."""
    if subject:
        return subject
    _, p = last_media(conv)
    if p:
        return p
    for m in reversed(conv["messages"][:-1]):
        if m["role"] == "user" and m.get("content"):
            kind, subj = detect_intent(m["content"])
            if kind == "chat":
                return m["content"][:200]
            if subj:
                return subj
    return None


# ---------- Chat: images and videos ----------
def chat_media_reply(conv, kind, prompt):
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        try:
            if kind == "image":
                img_model = (st.session_state.get("chat_img_model")
                             or st.session_state.get("t2i_model") or IMAGE_MODELS[0])
                with st.spinner("🎨 Creating your image…"):
                    data, ext = generate_images(prompt, img_model)[0], "png"
            else:
                img_model = VIDEO_MODEL
                with st.spinner("🎬 Creating your video… this can take a minute or two"):
                    data, ext = generate_video(prompt), "mp4"
        except Exception as e:
            st.error(friendly_error(e, img_model))
            return False

    name = f"{uuid.uuid4().hex[:12]}.{ext}"
    (IMAGES_DIR / name).write_bytes(data)
    add_media(kind, data, ext, prompt, img_model)  # also keep a copy in the gallery
    icon = "🎨 Here's your image" if kind == "image" else "🎬 Here's your video"
    conv["messages"].append({"role": "assistant", "content": f"{icon} for: *{prompt}*",
                             "prompt": prompt,  # remembered for "make another one"
                             "images" if kind == "image" else "videos": [name]})
    conv["updated"] = datetime.now().isoformat()
    save_store()
    return True


def reply_for(conv):
    """Route the latest user message to the right tool: image, video or normal chat."""
    last_msg = conv["messages"][-1]
    text = last_msg["content"].strip()

    # An attached photo + question goes to the chat (vision) model, unless it's a /command
    if last_msg.get("images") and not text.startswith("/"):
        return generate_reply(conv)

    kind, subject = detect_intent(text)

    # "make another one" / "again" right after an image or video -> same prompt, new result
    if kind == "chat" and FOLLOW_UP.match(text):
        prev_kind, _ = last_media(conv)
        if prev_kind:
            kind, subject = prev_kind, ""

    if kind in ("image", "video"):
        prompt = resolve_prompt(conv, subject)
        if not prompt:
            conv["messages"].append({
                "role": "assistant",
                "content": f"What should I create? Describe it, for example `/{kind} a red apple on a wooden table`.",
            })
            conv["updated"] = datetime.now().isoformat()
            save_store()
            return True
        return chat_media_reply(conv, kind, prompt)

    return generate_reply(conv)


# =====================================================================
#  PAGE: MEDIA STUDIO
# =====================================================================
def animate_this(name):
    st.session_state.i2v_source = "From my gallery"
    st.session_state.i2v_source_pick = name
    st.toast("Image selected. Open the ✨ Image → Video tab.", icon="🎬")


def media_card(item, key_prefix, allow_actions=True):
    path = MEDIA_DIR / item["file"]
    if not path.exists():
        return
    with st.container(border=True):
        if item["kind"] == "image":
            st.image(str(path))
        else:
            st.video(str(path))
        prompt = item["prompt"]
        st.caption(f"{prompt[:110]}{'…' if len(prompt) > 110 else ''}  \n"
                   f"{item['model']} · {datetime.fromisoformat(item['created']).strftime('%d %b, %I:%M %p')}")
        cols = st.columns(3 if item["kind"] == "image" and allow_actions else 2)
        cols[0].download_button("⬇", path.read_bytes(), file_name=item["file"],
                                key=f"{key_prefix}_dl_{item['file']}", help="Download")
        if allow_actions:
            if item["kind"] == "image":
                cols[1].button("🎬", key=f"{key_prefix}_anim_{item['file']}", help="Animate into a video",
                               on_click=animate_this, args=(item["file"],))
            cols[-1].button("🗑", key=f"{key_prefix}_del_{item['file']}", help="Delete",
                            on_click=delete_media, args=(item["file"],))


def show_results(names, key_prefix):
    items = {m["file"]: m for m in load_media()}
    found = [items[n] for n in names if n in items]
    if not found:
        return
    st.markdown("#### ✨ Your results")
    cols = st.columns(min(len(found), 3))
    for i, item in enumerate(found):
        with cols[i % len(cols)]:
            media_card(item, key_prefix, allow_actions=False)


def tab_text_to_image():
    prompt = st.text_area("Describe the image you want", height=110, key="t2i_prompt",
                          placeholder="A cosy reading corner in a treehouse at sunset, warm fairy lights")
    c1, c2, c3, c4, c5 = st.columns([1.3, 1.1, 1.1, 1, 0.9])
    img_model = c1.selectbox("Model", IMAGE_MODELS, key="t2i_model")
    style = c2.selectbox("Style", list(IMAGE_STYLES), key="t2i_style")
    size = c3.selectbox("Shape", ["auto", "1024x1024", "1536x1024", "1024x1536"],
                        format_func=lambda s: {"auto": "Auto", "1024x1024": "Square",
                                               "1536x1024": "Landscape", "1024x1536": "Portrait"}[s])
    quality = c4.selectbox("Quality", ["auto", "low", "medium", "high"])
    n = c5.number_input("How many", 1, 4, 1)

    if st.button("🎨 Generate image", disabled=not prompt.strip(), key="t2i_go"):
        with st.spinner("Painting your image… this can take up to a minute"):
            try:
                images = generate_images(prompt.strip() + IMAGE_STYLES[style], img_model, size, quality, int(n))
            except Exception as e:
                st.error(friendly_error(e, img_model))
                images = []
        st.session_state.last_images = [add_media("image", b, "png", prompt.strip(), img_model) for b in images]

    show_results(st.session_state.get("last_images", []), "t2i")


def video_options(prefix):
    c1, c2, c3 = st.columns(3)
    aspect = c1.selectbox("Shape", ["16:9", "9:16"], key=f"{prefix}_aspect",
                          format_func=lambda a: "Landscape 16:9" if a == "16:9" else "Portrait 9:16")
    resolution = c2.selectbox("Resolution", ["720p", "360p", "1080p", "4k"], key=f"{prefix}_res",
                              help="720p is fastest. 1080p and 4K are upscaled and take longer.")
    style = c3.selectbox("Style", list(VIDEO_STYLES), key=f"{prefix}_style")
    return aspect, resolution, style


def video_tips():
    with st.expander("💡 Tips for better videos"):
        st.markdown(
            "- Describe the **scene, camera movement, lighting and mood**.\n"
            "- Say *“single continuous shot, no scene cuts”* if you want one unbroken scene.\n"
            "- Describe the **sound**: *“calm background music, no dialogue”*.\n"
            "- Time events: *“[0-3s] a cat sits … [3-6s] it jumps onto the table”*.\n"
            "- Clips are short (about 8–10 seconds); the model decides the exact length."
        )


def tab_text_to_video():
    prompt = st.text_area("Describe the video you want", height=110, key="t2v_prompt",
                          placeholder="A paper boat sailing down a rainy city street, single continuous shot, "
                                      "gentle rain sounds, no dialogue")
    aspect, resolution, style = video_options("t2v")
    video_tips()
    if st.button("🎬 Generate video", disabled=not prompt.strip(), key="t2v_go"):
        with st.spinner("Directing your video… this usually takes 1–3 minutes"):
            try:
                data = generate_video(prompt.strip() + VIDEO_STYLES[style], aspect=aspect,
                                      resolution=resolution, task="text_to_video")
                st.session_state.last_t2v = [add_media("video", data, "mp4", prompt.strip(), VIDEO_MODEL)]
            except Exception as e:
                st.error(friendly_error(e, VIDEO_MODEL))
    show_results(st.session_state.get("last_t2v", []), "t2v")


def pick_image(label, key):
    """Let the user upload an image or choose one from the gallery. Returns raw bytes or None."""
    source = st.radio(label, ["Upload an image", "From my gallery"], horizontal=True, key=key)
    if source == "Upload an image":
        f = st.file_uploader("Image", type=["png", "jpg", "jpeg", "webp"], key=f"{key}_file",
                             label_visibility="collapsed")
        return f.getvalue() if f else None

    gallery = [m for m in load_media() if m["kind"] == "image" and (MEDIA_DIR / m["file"]).exists()]
    if not gallery:
        st.info("No images in your gallery yet. Create one in 🖼️ Text → Image.")
        return None
    files = [m["file"] for m in gallery]
    labels = {m["file"]: f"{m['prompt'][:60]} ({datetime.fromisoformat(m['created']).strftime('%d %b %H:%M')})"
              for m in gallery}
    pick_key = f"{key}_pick"
    if st.session_state.get(pick_key) not in files:
        st.session_state.pop(pick_key, None)
    choice = st.selectbox("Choose an image", files, format_func=labels.get, key=pick_key)
    return (MEDIA_DIR / choice).read_bytes()


def tab_image_to_video():
    first = pick_image("Starting image", "i2v_source")
    use_last = st.checkbox("Also add an ending image (the video will travel from the first image to the last)")
    last = pick_image("Ending image", "i2v_last") if use_last else None

    if first or last:
        cols = st.columns(2)
        if first:
            cols[0].image(first, caption="Start", width=320)
        if last:
            cols[1].image(last, caption="End", width=320)

    prompt = st.text_area("Describe the motion", height=100, key="i2v_prompt",
                          placeholder="The camera slowly pushes in as leaves drift past and the light turns golden")
    aspect, resolution, style = video_options("i2v")
    st.caption("Photos of real, recognisable people (and of children in some regions) may be blocked by "
               "Google's safety rules. Illustrations, products and landscapes work best.")
    video_tips()

    ready = bool(first) and bool(prompt.strip()) and (not use_last or bool(last))
    if st.button("✨ Bring it to life", disabled=not ready, key="i2v_go"):
        images = [prepare_image(first)]
        if last:
            images.append(prepare_image(last))
            full = "<FIRST_FRAME> <LAST_FRAME> " + prompt.strip()
            task = None
        else:
            full = "<FIRST_FRAME> " + prompt.strip()
            task = "image_to_video"
        with st.spinner("Animating your image… this usually takes 1–3 minutes"):
            try:
                data = generate_video(full + VIDEO_STYLES[style], images=images, aspect=aspect,
                                      resolution=resolution, task=task)
                st.session_state.last_i2v = [add_media("video", data, "mp4", prompt.strip(), VIDEO_MODEL)]
            except Exception as e:
                st.error(friendly_error(e, VIDEO_MODEL))
    show_results(st.session_state.get("last_i2v", []), "i2v")


def clear_gallery():
    for m in load_media():
        (MEDIA_DIR / m["file"]).unlink(missing_ok=True)
    save_media([])


def tab_gallery():
    items = [m for m in load_media() if (MEDIA_DIR / m["file"]).exists()]
    n_img = sum(m["kind"] == "image" for m in items)
    c1, c2, c3 = st.columns(3)
    c1.metric("Images", n_img)
    c2.metric("Videos", len(items) - n_img)
    show = c3.radio("Show", ["All", "Images", "Videos"], horizontal=True, key="gal_filter")
    if show != "All":
        items = [m for m in items if m["kind"] == show[:-1].lower()]
    if not items:
        st.info("Nothing here yet. Everything you create appears in this gallery.")
        return
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            media_card(item, "gal")
    with st.expander("🗑️ Clear the whole gallery"):
        ok = st.checkbox("Yes, delete every image and video in the gallery")
        st.button("Delete everything", disabled=not ok, on_click=clear_gallery)


def page_media():
    page_heading("🎨 Media Studio", "Create images and videos from text, and bring your images to life.")
    t1, t2, t3, t4 = st.tabs(["🖼️ Text → Image", "🎬 Text → Video", "✨ Image → Video", "🗂️ Gallery"])
    with t1:
        tab_text_to_image()
    with t2:
        if not (st.session_state.get("gemini_key") or "").strip():
            st.warning("Add your Google Gemini API key in ⚙️ Settings (sidebar) to create videos.")
        tab_text_to_video()
    with t3:
        if not (st.session_state.get("gemini_key") or "").strip():
            st.warning("Add your Google Gemini API key in ⚙️ Settings (sidebar) to create videos.")
        tab_image_to_video()
    with t4:
        tab_gallery()

# =====================================================================
#  PAGE: AI TOOLKIT  (one-click writing & learning tools)
# =====================================================================
def page_toolkit():
    page_heading("🧰 AI Toolkit", "One-click tools: summarize, translate, rewrite, proofread, quiz and more.")
    tool = st.radio("Tool", list(TOOLS), horizontal=True, key="tool_pick", label_visibility="collapsed")
    task, placeholder = TOOLS[tool]

    extra = {}
    if "{lang}" in task:
        extra["lang"] = st.selectbox("🌍 Translate into", LANGUAGES, key="tool_lang")
    if "{tone}" in task:
        extra["tone"] = st.selectbox("🎭 New tone", TONES, key="tool_tone")

    text = st.text_area("Input", height=170, key=f"tool_text_{tool}", placeholder=placeholder,
                        label_visibility="collapsed")
    c1, c2 = st.columns([1, 3])
    run = c1.button("⚡ Run tool", type="primary", disabled=not (text.strip() and model), key="tool_run")
    c2.caption(f"📝 {len(text.split())} words · {len(text)} characters")

    if run:
        prompt = task.format(**extra) + "\n\n---\n" + text.strip()
        with st.container(border=True):
            try:
                out = st.write_stream(stream_answer([{"role": "user", "content": prompt}]))
                st.session_state.tool_result = (tool, out)
            except Exception as e:
                st.error(friendly_error(e))
                st.session_state.pop("tool_result", None)
    elif st.session_state.get("tool_result", (None,))[0] == tool:
        with st.container(border=True):
            st.markdown(st.session_state.tool_result[1])

    res = st.session_state.get("tool_result")
    if res and res[0] == tool and res[1]:
        d1, d2 = st.columns(2)
        d1.download_button("⬇️ Download result", res[1], file_name="suleman_ai_result.md", mime="text/markdown",
                           key="tool_dl")
        d2.button("💬 Continue in chat", key="tool_to_chat", on_click=send_to_chat,
                  args=(f"{tool} result:\n\n{res[1]}\n\nLet's discuss this further.",))


def send_to_chat(text):
    st.session_state.current_id = None
    st.session_state.page = PAGES[0]
    st.session_state.queued = text


# =====================================================================
#  PAGE: CHAT
# =====================================================================
def page_chat():
    conv = convs.get(st.session_state.current_id)

    if conv is None:
        hour = datetime.now().hour
        greet, icon = (("Good morning", "☀️") if hour < 12 else ("Good afternoon", "🌤️") if hour < 18
                       else ("Good evening", "🌙"))
        st.markdown(
            f'<div class="hero-title">{greet}! What shall we create? <span class="emo">{icon}</span></div>'
            '<div class="hero-text">Ask anything · attach an image with 📎 · say “generate an image of a red car” '
            'or type <code>/image</code> / <code>/video</code> + a description.</div>',
            unsafe_allow_html=True,
        )
        with st.container(key="starters"):
            cols = st.columns(3)
            for i, (label, text) in enumerate(STARTERS):
                cols[i % 3].button(label, key=f"starter_{i}", on_click=queue_prompt, args=(text,))
    else:
        head, opts = st.columns([5, 1.3])
        with head:
            words = sum(len(m["content"].split()) for m in conv["messages"])
            st.markdown(f'<div class="chat-title">{"📌 " if conv.get("pinned") else ""}'
                        f'{html.escape(conv["title"])}</div>', unsafe_allow_html=True)
            st.caption(f"💬 {len(conv['messages'])} messages · 📝 {words:,} words · 🕒 "
                       f"{datetime.fromisoformat(conv['updated']).strftime('%d %b, %I:%M %p')}")
        with opts:
            with st.popover("⋯ Options", use_container_width=True):
                st.text_input("✏️ Rename chat", value=conv["title"],
                              key=f"rename_box_{st.session_state.current_id}", on_change=rename_chat)
                st.button("📍 Unpin chat" if conv.get("pinned") else "📌 Pin chat", on_click=toggle_pin)
                fname = re.sub(r"[^\w\- ]", "", conv["title"])[:30].strip() or "chat"
                st.download_button("⬇️ Markdown (.md)", to_markdown(conv), file_name=f"{fname}.md",
                                   mime="text/markdown")
                st.download_button("⬇️ JSON (.json)", json.dumps(conv, indent=2, ensure_ascii=False),
                                   file_name=f"{fname}.json", mime="application/json")
                confirm_del = st.checkbox("Confirm delete")
                st.button("🗑️ Delete this chat", disabled=not confirm_del, on_click=delete_chat)

        for msg in conv["messages"]:
            show_message(msg)

    typed = st.chat_input(
        "Message, /image …, /video …, or attach an image",
        accept_file="multiple",
        file_type=["png", "jpg", "jpeg", "webp", "gif"],
        disabled=not model,
    )

    text, files = "", []
    if typed:
        text = (typed.text or "").strip()
        files = list(typed.files or [])
    else:
        text = st.session_state.pop("queued", "").strip()
    if files and not text:
        text = "Describe this image in detail."

    if st.session_state.pop("regen", False) and conv is not None:
        reply_for(conv)
        st.rerun()

    elif text:
        current_id = st.session_state.current_id
        if conv is None:
            now = datetime.now().isoformat()
            current_id = uuid.uuid4().hex[:8]
            conv = {"title": make_title(text), "created": now, "updated": now, "messages": []}
            convs[current_id] = conv
            st.session_state.current_id = current_id

        image_names = []
        for f in files:
            name = uuid.uuid4().hex[:12] + (Path(f.name).suffix.lower() or ".png")
            (IMAGES_DIR / name).write_bytes(f.getvalue())
            image_names.append(name)

        user_msg = {"role": "user", "content": text, "time": now_label()}
        if image_names:
            user_msg["images"] = image_names
        conv["messages"].append(user_msg)
        show_message(user_msg)

        if reply_for(conv):
            st.rerun()
        else:
            delete_images([conv["messages"].pop()])
            if not conv["messages"]:
                convs.pop(current_id, None)
                st.session_state.current_id = None
            save_store()

    elif conv and conv["messages"] and conv["messages"][-1]["role"] == "assistant":
        st.button("↻ Regenerate last answer", on_click=regenerate)


# =====================================================================
#  PAGE: DATA STUDIO
# =====================================================================
@st.cache_data
def sample_data():
    rng = np.random.default_rng(7)
    rows = []
    for year in range(2021, 2026):
        for month in range(1, 13):
            for product, base in [("Laptops", 120), ("Phones", 200), ("Tablets", 80)]:
                sales = base * (1 + 0.12 * (year - 2021)) * (1 + 0.25 * np.sin((month - 1) / 12 * 2 * np.pi))
                sales += rng.normal(0, 10)
                rows.append(dict(
                    Year=year, Month=month, Product=product,
                    Sales=round(sales, 1),
                    Profit=round(sales * rng.uniform(0.15, 0.3), 1),
                    Customers=int(sales * rng.uniform(0.6, 0.9)),
                ))
    return pd.DataFrame(rows)


def load_data():
    source = st.radio("Data source", ["Sample sales data", "Upload a file", "Paste data"], horizontal=True)

    if source == "Sample sales data":
        return sample_data()

    if source == "Upload a file":
        f = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
        if not f:
            return None
        try:
            return pd.read_csv(f) if f.name.lower().endswith(".csv") else pd.read_excel(f)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            return None

    raw = st.text_area("Paste CSV data (first line = column names)", height=160,
                       placeholder="Month,Sales,Profit\nJan,120,30\nFeb,150,42\nMar,170,50")
    if not raw.strip():
        return None
    try:
        return pd.read_csv(io.StringIO(raw))
    except Exception as e:
        st.error(f"Could not read the pasted data: {e}")
        return None


def build_chart(df):
    num_cols = df.select_dtypes("number").columns.tolist()
    all_cols = df.columns.tolist()

    chart = st.selectbox("Chart type", [
        "Line", "Bar", "Area", "Scatter", "Box", "Histogram",
        "Pie / Donut", "Correlation heatmap", "3D Scatter",
    ])

    if not num_cols:
        st.warning("This data has no numeric columns to plot.")
        return

    if chart in ["Line", "Bar", "Area", "Scatter", "Box"]:
        c1, c2, c3, c4 = st.columns(4)
        x = c1.selectbox("X axis", all_cols)
        y_options = [c for c in num_cols if c != x] or num_cols
        y_default = max(range(len(y_options)), key=lambda i: df[y_options[i]].nunique())
        y = c2.selectbox("Y axis", y_options, index=y_default)
        color = c3.selectbox("Colour by", [NONE] + all_cols)
        anim = c4.selectbox("Animate by", [NONE] + all_cols,
                            help="Pick a column such as Year to play the chart as an animation.")
        color = None if color == NONE else color
        anim = None if anim == NONE else anim

        data = df
        if chart in ["Line", "Bar", "Area"] and st.checkbox("Add up values that share the same X", value=True):
            keys = list(dict.fromkeys(k for k in [x, color, anim] if k))
            data = df.groupby(keys, as_index=False)[y].sum()
        if chart in ["Line", "Area"]:
            data = data.sort_values(x)

        kwargs = dict(x=x, y=y, color=color, animation_frame=anim)
        if anim:
            lo, hi = float(data[y].min()), float(data[y].max())
            pad = (hi - lo) * 0.1 or 1
            kwargs["range_y"] = [0 if lo >= 0 and chart != "Scatter" else lo - pad, hi + pad]
            if chart == "Scatter":
                lo_x, hi_x = data[x].min(), data[x].max()
                if pd.api.types.is_numeric_dtype(data[x]):
                    pad_x = (hi_x - lo_x) * 0.1 or 1
                    kwargs["range_x"] = [lo_x - pad_x, hi_x + pad_x]

        builders = {"Line": px.line, "Bar": px.bar, "Area": px.area, "Scatter": px.scatter, "Box": px.box}
        if chart == "Line":
            kwargs["markers"] = True
        if chart == "Box":
            kwargs.pop("animation_frame")
        fig = builders[chart](data, **kwargs, title=f"{y} by {x}")
        if chart == "Bar" and color:
            fig.update_layout(barmode="group")
        st.plotly_chart(style(fig, 520))

    elif chart == "Histogram":
        c1, c2, c3 = st.columns(3)
        x = c1.selectbox("Column", num_cols)
        color = c2.selectbox("Colour by", [NONE] + all_cols)
        bins = c3.slider("Bins", 5, 100, 30)
        fig = px.histogram(df, x=x, color=None if color == NONE else color, nbins=bins,
                           title=f"Distribution of {x}", barmode="overlay", opacity=0.8)
        st.plotly_chart(style(fig, 520))

    elif chart == "Pie / Donut":
        c1, c2 = st.columns(2)
        names = c1.selectbox("Slices (category)", all_cols)
        values = c2.selectbox("Values", num_cols)
        data = df.groupby(names, as_index=False)[values].sum()
        fig = px.pie(data, names=names, values=values, hole=0.45,
                     title=f"{values} share by {names}", color_discrete_sequence=COLORS)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(style(fig, 520))

    elif chart == "Correlation heatmap":
        if len(num_cols) < 2:
            st.warning("You need at least 2 numeric columns.")
            return
        corr = df[num_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1,
                        color_continuous_scale=["#00d4ff", "#141a3a", "#ff2e88"],
                        title="How strongly the numeric columns move together")
        st.plotly_chart(style(fig, 560))

    elif chart == "3D Scatter":
        if len(num_cols) < 3:
            st.warning("You need at least 3 numeric columns for a 3D chart.")
            return
        c1, c2, c3, c4 = st.columns(4)
        x = c1.selectbox("X", num_cols, index=0)
        y = c2.selectbox("Y", num_cols, index=1)
        z = c3.selectbox("Z", num_cols, index=2)
        color = c4.selectbox("Colour by", [NONE] + all_cols)
        fig = px.scatter_3d(df, x=x, y=y, z=z, color=None if color == NONE else color,
                            title=f"{x} × {y} × {z}  (drag to rotate)", opacity=0.85)
        fig.update_traces(marker=dict(size=5))
        st.plotly_chart(style_3d(fig, 640))


def page_data():
    page_heading("📊 Data Studio", "Upload or paste your data, build 2D, 3D and animated charts, and ask AI for insights.")
    df = load_data()
    if df is None:
        st.info("Add some data above to start.")
        return

    num_cols = df.select_dtypes("number").columns
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{len(df):,}")
    m2.metric("Columns", len(df.columns))
    m3.metric("Numeric columns", len(num_cols))
    m4.metric("Missing values", int(df.isna().sum().sum()))

    tab_chart, tab_table, tab_summary, tab_ai = st.tabs(["📈 Chart builder", "🗂️ Table", "🧮 Summary", "🤖 Ask AI"])

    with tab_chart:
        build_chart(df)
        st.caption("Tip: hover a chart and click the 📷 icon to save it as an image.")

    with tab_table:
        st.dataframe(df, height=460)
        st.download_button("⬇ Download as CSV", df.to_csv(index=False), "data.csv", "text/csv")

    with tab_summary:
        if len(num_cols):
            st.dataframe(df[num_cols].describe().T.round(2))
        info = pd.DataFrame({"Type": df.dtypes.astype(str), "Missing": df.isna().sum(),
                             "Unique values": df.nunique()})
        st.dataframe(info)

    with tab_ai:
        question = st.text_input("What do you want to know?",
                                 value="What are the key trends, patterns and insights in this data?")
        if st.button("Analyse with AI", disabled=not model):
            summary = (
                f"Dataset: {len(df)} rows, columns: {', '.join(map(str, df.columns))}\n\n"
                f"Statistics:\n{df.describe(include='all').round(2).to_string()[:4000]}\n\n"
                f"First rows:\n{df.head(15).to_csv(index=False)[:3000]}"
            )
            prompt = f"{question}\n\nHere is the data:\n{summary}\n\nAnswer with clear headings and bullet points."
            try:
                st.write_stream(stream_answer([{"role": "user", "content": prompt}]))
            except Exception as e:
                st.error(friendly_error(e))


# =====================================================================
#  PAGE: TRIGONOMETRY
# =====================================================================
def trig_values(a):
    th = np.radians(a)
    c, s = np.cos(th), np.sin(th)
    c = 0.0 if abs(c) < 1e-12 else c
    s = 0.0 if abs(s) < 1e-12 else s
    t = None if c == 0 else s / c
    return th, c, s, t


def unit_circle_fig(a):
    th, c, s, t = trig_values(a)
    circle = np.linspace(0, 2 * np.pi, 300)
    arc = np.linspace(0, th, 80)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.cos(circle), y=np.sin(circle), mode="lines", name="Unit circle",
                             line=dict(color="rgba(255,255,255,0.35)", width=2), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=0.25 * np.cos(arc), y=0.25 * np.sin(arc), mode="lines",
                             name=f"θ = {a}°", line=dict(color="#a78bfa", width=3)))
    fig.add_trace(go.Scatter(x=[0, c], y=[0, 0], mode="lines", name=f"cos θ = {c:.3f}",
                             line=dict(color="#00d4ff", width=6)))
    fig.add_trace(go.Scatter(x=[c, c], y=[0, s], mode="lines", name=f"sin θ = {s:.3f}",
                             line=dict(color="#ffb020", width=6)))
    fig.add_trace(go.Scatter(x=[0, c], y=[0, s], mode="lines", name="Radius = 1",
                             line=dict(color="#ff2e88", width=4)))
    if t is not None:
        fig.add_trace(go.Scatter(x=[1, 1], y=[0, float(np.clip(t, -1.85, 1.85))], mode="lines",
                                 name=f"tan θ = {t:.3f}", line=dict(color="#22c55e", width=4, dash="dash")))
    pos = ("top" if s >= 0 else "bottom") + " " + ("right" if c >= 0 else "left")
    fig.add_trace(go.Scatter(x=[c], y=[s], mode="markers+text", showlegend=False,
                             text=[f"({c:.2f}, {s:.2f})"], textposition=pos,
                             textfont=dict(color="#ffffff", size=14),
                             marker=dict(size=16, color="#ff2e88", line=dict(color="#ffffff", width=2))))
    fig.update_xaxes(range=[-1.9, 1.9])
    fig.update_yaxes(range=[-1.9, 1.9], scaleanchor="x", scaleratio=1)
    fig.update_layout(title=f"Unit circle at {a}°",
                      legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))
    return style(fig, 600)


def waves_fig(a):
    _, c, s, _ = trig_values(a)
    x = np.arange(0, 361)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=np.sin(np.radians(x)), name="sin θ", line=dict(color="#ffb020", width=4)))
    fig.add_trace(go.Scatter(x=x, y=np.cos(np.radians(x)), name="cos θ", line=dict(color="#00d4ff", width=4)))
    fig.add_trace(go.Scatter(x=[a, a], y=[s, c], mode="markers", showlegend=False,
                             marker=dict(size=14, color=["#ffb020", "#00d4ff"], line=dict(color="#fff", width=2))))
    fig.add_vline(x=a, line=dict(color="#ff2e88", width=2, dash="dash"))
    fig.update_xaxes(title="Angle (degrees)", tickvals=list(range(0, 361, 45)))
    fig.update_yaxes(title="Value", range=[-1.2, 1.2])
    fig.update_layout(title=f"sin and cos waves — marker at {a}°")
    return style(fig, 460)


def animated_trig_fig():
    angles = list(range(0, 361, 5))
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58],
                        subplot_titles=("Point moving round the unit circle", "The same point traced as waves"))

    def parts(a):
        _, c, s, _ = trig_values(a)
        return [
            go.Scatter(x=[0, c], y=[0, s], mode="lines", line=dict(color="#ff2e88", width=4), name="Radius"),
            go.Scatter(x=[0, c], y=[0, 0], mode="lines", line=dict(color="#00d4ff", width=6), name="cos"),
            go.Scatter(x=[c, c], y=[0, s], mode="lines", line=dict(color="#ffb020", width=6), name="sin"),
            go.Scatter(x=[c], y=[s], mode="markers", marker=dict(size=16, color="#ff2e88",
                       line=dict(color="#fff", width=2)), showlegend=False),
            go.Scatter(x=[a], y=[s], mode="markers", marker=dict(size=14, color="#ffb020"), showlegend=False),
            go.Scatter(x=[a], y=[c], mode="markers", marker=dict(size=14, color="#00d4ff"), showlegend=False),
        ]

    circle = np.linspace(0, 2 * np.pi, 300)
    deg = np.arange(0, 361)
    fig.add_trace(go.Scatter(x=np.cos(circle), y=np.sin(circle), mode="lines", hoverinfo="skip",
                             line=dict(color="rgba(255,255,255,0.35)", width=2), showlegend=False), 1, 1)
    first = parts(0)
    for tr in first[:4]:
        fig.add_trace(tr, 1, 1)
    fig.add_trace(go.Scatter(x=deg, y=np.sin(np.radians(deg)), name="sin θ",
                             line=dict(color="#ffb020", width=3)), 1, 2)
    fig.add_trace(go.Scatter(x=deg, y=np.cos(np.radians(deg)), name="cos θ",
                             line=dict(color="#00d4ff", width=3)), 1, 2)
    for tr in first[4:]:
        fig.add_trace(tr, 1, 2)

    fig.frames = [go.Frame(data=parts(a), traces=[1, 2, 3, 4, 7, 8], name=str(a)) for a in angles]

    fig.update_xaxes(range=[-1.3, 1.3], row=1, col=1)
    fig.update_yaxes(range=[-1.3, 1.3], scaleanchor="x", scaleratio=1, row=1, col=1)
    fig.update_xaxes(range=[0, 360], tickvals=list(range(0, 361, 90)), title="Angle (degrees)", row=1, col=2)
    fig.update_yaxes(range=[-1.2, 1.2], row=1, col=2)
    fig.update_layout(
        updatemenus=play_menu(60),
        sliders=[dict(
            active=0, currentvalue=dict(prefix="Angle: ", suffix="°", font=dict(color="#fff")),
            pad=dict(t=50), font=dict(color="#c9cff5"),
            steps=[dict(method="animate", label=str(a),
                        args=[[str(a)], dict(mode="immediate", frame=dict(duration=0, redraw=False))])
                   for a in angles],
        )],
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
    )
    return style(fig, 560)


def triangle_fig(a, hyp):
    th = np.radians(a)
    adj, opp = hyp * np.cos(th), hyp * np.sin(th)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, adj, adj, 0], y=[0, 0, opp, 0], fill="toself", mode="lines",
                             fillcolor="rgba(124,58,237,0.25)", line=dict(color="#a78bfa", width=3),
                             hoverinfo="skip", showlegend=False))
    for x0, y0, x1, y1, color, label in [
        (0, 0, adj, 0, "#00d4ff", f"Adjacent = {adj:.2f}"),
        (adj, 0, adj, opp, "#ffb020", f"Opposite = {opp:.2f}"),
        (0, 0, adj, opp, "#ff2e88", f"Hypotenuse = {hyp:.2f}"),
    ]:
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", name=label,
                                 line=dict(color=color, width=5)))
    fig.add_annotation(x=hyp * 0.12, y=hyp * 0.04, text=f"{a}°", showarrow=False,
                       font=dict(color="#ffffff", size=16))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(title="Right triangle", legend=dict(orientation="h", y=-0.12))
    return style(fig, 420)


def page_trig():
    page_heading("📐 Trigonometry Explorer",
                 "Move the angle and watch sin, cos and tan change on the unit circle and the waves.")

    a = st.slider("Angle θ (degrees)", 0, 360, 45)
    th, c, s, t = trig_values(a)

    if a % 90 == 0:
        quadrant = "On an axis"
    else:
        quadrant = f"Quadrant {['I', 'II', 'III', 'IV'][int(a // 90) % 4]}"
    ref = a if a <= 90 else 180 - a if a <= 180 else a - 180 if a <= 270 else 360 - a

    m = st.columns(6)
    m[0].metric("Radians", f"{th:.4f}", f"{a / 180:.4g} π", delta_color="off")
    m[1].metric("sin θ", f"{s:.4f}")
    m[2].metric("cos θ", f"{c:.4f}")
    m[3].metric("tan θ", "undefined" if t is None else f"{t:.4f}")
    m[4].metric("Position", quadrant)
    m[5].metric("Reference angle", f"{ref}°")

    tab_circle, tab_wave, tab_anim, tab_tri, tab_table = st.tabs(
        ["⭕ Unit circle", "〰️ Waves", "▶ Animated", "📐 Right triangle", "📋 Special angles"])

    with tab_circle:
        st.plotly_chart(unit_circle_fig(a))
        st.caption("Cyan = cos θ (horizontal), orange = sin θ (vertical), green dashed = tan θ "
                   "(touching line at x = 1, cut off when very large).")

    with tab_wave:
        st.plotly_chart(waves_fig(a))

    with tab_anim:
        st.plotly_chart(animated_trig_fig())
        st.caption("Press ▶ Play, or drag the slider under the chart.")

    with tab_tri:
        hyp = st.number_input("Hypotenuse length", min_value=0.1, value=10.0, step=0.5)
        if 0 < a < 90:
            c1, c2 = st.columns([1, 1.3])
            with c1:
                st.metric("Opposite = hyp × sin θ", f"{hyp * s:.3f}")
                st.metric("Adjacent = hyp × cos θ", f"{hyp * c:.3f}")
                st.metric("Other angle", f"{90 - a}°")
            with c2:
                st.plotly_chart(triangle_fig(a, hyp))
        else:
            st.info("A right triangle needs an angle between 1° and 89°. Move the slider above.")

    with tab_table:
        table = pd.DataFrame({
            "Degrees": ["0°", "30°", "45°", "60°", "90°", "180°", "270°", "360°"],
            "Radians": ["0", "π/6", "π/4", "π/3", "π/2", "π", "3π/2", "2π"],
            "sin": ["0", "1/2", "√2/2", "√3/2", "1", "0", "−1", "0"],
            "cos": ["1", "√3/2", "√2/2", "1/2", "0", "−1", "0", "1"],
            "tan": ["0", "√3/3", "1", "√3", "undefined", "0", "undefined", "0"],
        })
        st.dataframe(table, hide_index=True)


# =====================================================================
#  PAGE: ANIMATIONS
# =====================================================================
def projectile_fig(v, angle, g=9.81):
    th = np.radians(angle)
    T = 2 * v * np.sin(th) / g
    R = v * np.cos(th) * T
    H = (v * np.sin(th)) ** 2 / (2 * g)
    t = np.linspace(0, T, 70)
    x, y = v * np.cos(th) * t, v * np.sin(th) * t - 0.5 * g * t ** 2

    fig = go.Figure([
        go.Scatter(x=x, y=y, mode="lines", line=dict(color="rgba(255,255,255,0.2)", dash="dot"), name="Path"),
        go.Scatter(x=[x[0]], y=[y[0]], mode="lines", line=dict(color="#00d4ff", width=4), name="Trail"),
        go.Scatter(x=[x[0]], y=[y[0]], mode="markers", name="Ball",
                   marker=dict(size=18, color="#ff2e88", line=dict(color="#fff", width=2))),
    ])
    fig.frames = [go.Frame(data=[go.Scatter(x=x[:k + 1], y=y[:k + 1]), go.Scatter(x=[x[k]], y=[y[k]])],
                           traces=[1, 2]) for k in range(len(t))]
    fig.update_xaxes(range=[0, R * 1.05], title="Distance (m)")
    fig.update_yaxes(range=[0, H * 1.3 + 0.1], title="Height (m)")
    fig.update_layout(updatemenus=play_menu(40), title="Projectile motion",
                      legend=dict(orientation="h", y=1.12, x=1, xanchor="right"))
    return style(fig, 500), T, R, H


def wave_fig(amp, wavelength, speed):
    x = np.linspace(0, 4 * np.pi, 400)
    k = 2 * np.pi / wavelength
    phases = np.linspace(0, 2 * np.pi, 40, endpoint=False)
    fig = go.Figure([go.Scatter(x=x, y=amp * np.sin(k * x), mode="lines",
                                line=dict(color="#00d4ff", width=5), fill="tozeroy",
                                fillcolor="rgba(0,212,255,0.12)", name="Wave")])
    fig.frames = [go.Frame(data=[go.Scatter(x=x, y=amp * np.sin(k * x - p))]) for p in phases]
    fig.update_yaxes(range=[-amp * 1.3, amp * 1.3])
    fig.update_layout(updatemenus=play_menu(int(120 / speed)), title="Travelling sine wave  y = A·sin(kx − ωt)")
    return style(fig, 460)


def lissajous_fig(a, b, delta_deg):
    t = np.linspace(0, 2 * np.pi, 500)
    x, y = np.sin(a * t + np.radians(delta_deg)), np.sin(b * t)
    steps = np.linspace(2, len(t), 60).astype(int)
    fig = go.Figure([
        go.Scatter(x=x[:2], y=y[:2], mode="lines", line=dict(color="#ff2e88", width=4), name="Curve"),
        go.Scatter(x=[x[0]], y=[y[0]], mode="markers", marker=dict(size=14, color="#ffb020"), showlegend=False),
    ])
    fig.frames = [go.Frame(data=[go.Scatter(x=x[:k], y=y[:k]), go.Scatter(x=[x[k - 1]], y=[y[k - 1]])])
                  for k in steps]
    fig.update_xaxes(range=[-1.2, 1.2])
    fig.update_yaxes(range=[-1.2, 1.2], scaleanchor="x", scaleratio=1)
    fig.update_layout(updatemenus=play_menu(40), title=f"Lissajous curve  (a = {a}, b = {b}, δ = {delta_deg}°)")
    return style(fig, 520)


def surface_fig(kind):
    grid = np.linspace(-6, 6, 50)
    X, Y = np.meshgrid(grid, grid)
    R = np.sqrt(X ** 2 + Y ** 2)
    phases = np.linspace(0, 2 * np.pi, 30, endpoint=False)

    def z_at(p):
        if kind == "ripple":
            return np.sin(R - p) / (1 + 0.15 * R)
        return np.sin(X / 1.5 + p) * np.cos(Y / 1.5 + p)

    fig = go.Figure([go.Surface(x=X, y=Y, z=z_at(0), colorscale="Plasma", cmin=-1, cmax=1, showscale=False)])
    fig.frames = [go.Frame(data=[go.Surface(z=z_at(p))]) for p in phases]
    title = "3D ripple surface" if kind == "ripple" else "3D trig surface  z = sin(x)·cos(y)"
    fig.update_layout(
        updatemenus=play_menu(70, redraw=True), title=title,
        scene=dict(zaxis=dict(range=[-1.2, 1.2]), aspectratio=dict(x=1, y=1, z=0.5),
                   camera=dict(eye=dict(x=1.6, y=1.6, z=0.9))),
    )
    return style_3d(fig, 620)


def helix_fig():
    t = np.linspace(0, 6 * np.pi, 300)
    x, y, z = np.cos(t), np.sin(t), t / (6 * np.pi)
    steps = list(range(5, len(t) + 1, 5))

    def parts(k):
        return [
            go.Scatter3d(x=x[:k], y=y[:k], z=z[:k], mode="lines",
                         line=dict(color=z[:k], colorscale="Plasma", cmin=0, cmax=1, width=9)),
            go.Scatter3d(x=[x[k - 1]], y=[y[k - 1]], z=[z[k - 1]], mode="markers",
                         marker=dict(size=7, color="#ffffff")),
        ]

    fig = go.Figure(parts(5))
    fig.frames = [go.Frame(data=parts(k)) for k in steps]
    fig.update_layout(
        updatemenus=play_menu(40, redraw=True), showlegend=False,
        title="3D spiral helix  (x = cos t, y = sin t, z = t)",
        scene=dict(xaxis=dict(range=[-1.2, 1.2]), yaxis=dict(range=[-1.2, 1.2]), zaxis=dict(range=[0, 1.05])),
    )
    return style_3d(fig, 620)


def page_animations():
    page_heading("🎬 Animations", "Interactive 2D and 3D animations. Press ▶ Play on any chart; drag 3D charts to rotate.")
    tab2d, tab3d = st.tabs(["✨ 2D animations", "🧊 3D animations"])

    with tab2d:
        choice = st.radio("Choose an animation", ["Projectile motion", "Travelling wave", "Lissajous curve"],
                          horizontal=True)
        if choice == "Projectile motion":
            c1, c2 = st.columns(2)
            v = c1.slider("Launch speed (m/s)", 5, 60, 25)
            ang = c2.slider("Launch angle (degrees)", 5, 85, 45)
            fig, T, R, H = projectile_fig(v, ang)
            m = st.columns(3)
            m[0].metric("Flight time", f"{T:.2f} s")
            m[1].metric("Range", f"{R:.1f} m")
            m[2].metric("Max height", f"{H:.1f} m")
            st.plotly_chart(fig)
            st.caption("Uses trigonometry: horizontal speed = v·cos θ, vertical speed = v·sin θ.")
        elif choice == "Travelling wave":
            c1, c2, c3 = st.columns(3)
            amp = c1.slider("Amplitude", 0.5, 3.0, 1.0, 0.1)
            wl = c2.slider("Wavelength", 1.0, 8.0, 3.0, 0.5)
            spd = c3.slider("Speed", 1, 5, 2)
            st.plotly_chart(wave_fig(amp, wl, spd))
        else:
            c1, c2, c3 = st.columns(3)
            a = c1.slider("a (x frequency)", 1, 7, 3)
            b = c2.slider("b (y frequency)", 1, 7, 2)
            d = c3.slider("δ phase (degrees)", 0, 180, 90)
            st.plotly_chart(lissajous_fig(a, b, d))

    with tab3d:
        choice = st.radio("Choose a 3D animation", ["Ripple surface", "Trig wave surface", "Spiral helix"],
                          horizontal=True)
        if choice == "Ripple surface":
            st.plotly_chart(surface_fig("ripple"))
        elif choice == "Trig wave surface":
            st.plotly_chart(surface_fig("trig"))
        else:
            st.plotly_chart(helix_fig())


# =====================================================================
#  ROUTER
# =====================================================================
brand_header()
page = st.session_state.page
ROUTES = {
    PAGES[0]: page_chat, PAGES[1]: page_toolkit, PAGES[2]: page_media,
    PAGES[3]: page_data, PAGES[4]: page_trig, PAGES[5]: page_animations,
}
ROUTES.get(page, page_chat)()
