"""Streamlit UI for the research agent.

Run from starter_v0/:
    streamlit run app.py

Reuses the same model/tool loop as chat.py, shows every tool call + raw result
(errors are NOT hidden), and writes a transcript to transcripts/ like chat.py.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROVIDER = "openai"
VERSION = "v8"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

SAMPLE_QUESTIONS = [
    "Tin AI hôm nay có gì nổi bật?",
    "Lấy 5 tweet mới nhất của Sam Altman",
    "Dân dev trên Hacker News đang bàn gì về Rust?",
    "Tóm tắt bài này giúp mình: https://openai.com/research/",
    "Đăng bản tin AI hôm nay lên Telegram giúp mình",
]


@st.cache_resource
def load_agent() -> dict[str, Any]:
    provider = make_provider(PROVIDER)
    return {
        "provider": provider,
        "model": getattr(provider, "default_model", None),
        "system_prompt": SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"),
        "tools": to_openai_tools(load_tool_declarations(TOOLS_PATH)),
        "artifact_version": build_artifact_version(VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH),
    }


def new_transcript(agent: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{safe_slug(VERSION)}_{PROVIDER}_ui_{stamp}"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(agent["artifact_version"]),
        "provider": PROVIDER,
        "model": agent["model"],
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return ROOT / "transcripts" / f"{transcript_id}.transcript.json", transcript


def render_tool_events(events: list[dict[str, Any]]) -> None:
    for event in events:
        result = event.get("result", {})
        failed = isinstance(result, dict) and "error" in result
        label = f"{'⚠️' if failed else '🔧'} {event.get('tool')}({event.get('args', {})})"
        with st.expander(label, expanded=failed):
            st.json(event)


st.set_page_config(page_title="Research Agent", page_icon="🔎")
agent = load_agent()

if "history" not in st.session_state:
    st.session_state.history = []          # model context: user/assistant text
    st.session_state.display = []          # what we render, incl. tool events
    st.session_state.transcript_path, st.session_state.transcript = new_transcript(agent)

with st.sidebar:
    st.header("Research Agent")
    st.caption("Tìm tin web, tweet theo tài khoản/chủ đề, Hacker News, đọc URL, paper arXiv; "
               "chỉ gửi Telegram sau khi bạn xác nhận.")
    st.write(f"**Provider:** `{PROVIDER}` / `{agent['model']}`")
    st.write(f"**Artifact:** `{agent['artifact_version'].artifact_version}`")
    st.subheader("Câu hỏi mẫu")
    for question in SAMPLE_QUESTIONS:
        if st.button(question, use_container_width=True):
            st.session_state.pending = question
    if st.button("🗑️ Cuộc trò chuyện mới", use_container_width=True):
        for key in ["history", "display", "transcript_path", "transcript"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.caption(f"Transcript: `{st.session_state.transcript_path.name}`")

st.title("🔎 Research Agent")

for message in st.session_state.display:
    with st.chat_message(message["role"]):
        if message.get("tool_events"):
            render_tool_events(message["tool_events"])
        st.markdown(message["content"])

user_text = st.chat_input("Hỏi agent...") or st.session_state.pop("pending", None)

if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.display.append({"role": "user", "content": user_text})

    messages = [
        {"role": "system", "content": agent["system_prompt"]},
        *trim_history(st.session_state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
    }
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                result = run_model_tool_loop(
                    provider=agent["provider"], messages=messages, tools=agent["tools"],
                    model=None, max_tool_rounds=MAX_TOOL_ROUNDS,
                )
            except Exception as exc:  # show the error instead of hiding it
                result = {"status": "error", "assistant_text": f"❌ Lỗi provider: {type(exc).__name__}: {exc}",
                          "rounds": [], "tool_events": []}
        render_tool_events(result["tool_events"])
        st.markdown(result["assistant_text"])

    st.session_state.display.append({
        "role": "assistant", "content": result["assistant_text"], "tool_events": result["tool_events"],
    })
    st.session_state.history += [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": result["assistant_text"]},
    ]
    turn.update(result)
    turn["finished_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    st.session_state.transcript["updated_at"] = now_iso()
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
