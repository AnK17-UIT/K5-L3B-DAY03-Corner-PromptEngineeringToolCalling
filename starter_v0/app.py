import streamlit as st
import time
import json
from pathlib import Path
from agent import ResearchAgent

# Cấu hình giao diện Wide Mode
st.set_page_config(
    page_title="AI20k Research Agent Inspector",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo state
if "agent" not in st.session_state:
    st.session_state.agent = ResearchAgent(
        provider="openai",
        system_prompt=Path("artifacts/system_prompt.md").read_text(encoding="utf-8"),
        tools="artifacts/tools.yaml"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_telemetry" not in st.session_state:
    st.session_state.latest_telemetry = None

st.title("✨ AI20k Research Agent — Live Observability Dashboard")
st.caption("Giao diện kiểm thử ReAct Tool-Calling kết hợp giám sát độ trễ & token tiêu hao theo thời gian thực")

# Chia 2 cột: Chat (65%) và Inspector (35%)
col_chat, col_inspect = st.columns([13, 7], gap="large")

# ----------------- CỘT 1: CHAT GIAO DIỆN -----------------
with col_chat:
    st.subheader("💬 Cuộc trò chuyện")
    
    # Hiển thị lịch sử chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_calls"):
                with st.expander(f"🛠️ Đã dùng {len(msg['tool_calls'])} công cụ"):
                    st.json(msg["tool_calls"])

    # Nhận câu hỏi mới
    if prompt := st.chat_input("Nhập câu hỏi nghiên cứu, tìm tweet, đọc báo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status_box = st.status("🚀 Đang xử lý yêu cầu...", expanded=True)
            msg_placeholder = st.empty()

            start_total_time = time.time()
            step_logs = []

            # Bước 1: Ingest
            step_logs.append({
                "step": "1. Ingest Prompt",
                "desc": "Nạp System Instructions và Tool Schemas",
                "elapsed": 0.01,
            })
            status_box.write("⚙️ Đã nạp cấu hình prompt và tools...")

            # Bước 2: Model Inference
            t_model_start = time.time()
            status_box.write("🧠 Mô hình đang suy nghĩ và quyết định gọi công cụ...")

            try:
                # Gọi hàm của ResearchAgent
                raw_response = st.session_state.agent.run(prompt)
                model_latency = round(time.time() - t_model_start, 3)

                step_logs.append({
                    "step": "2. Model Inference",
                    "desc": "Mô hình phân tích và sinh phản hồi",
                    "elapsed": model_latency,
                })

                # Trích xuất text và tool_calls an toàn dù raw_response là dict, str hay object
                final_text = ""
                tool_calls = []

                if isinstance(raw_response, dict):
                    final_text = raw_response.get("text") or raw_response.get("content") or raw_response.get("response") or str(raw_response)
                    tool_calls = raw_response.get("tool_calls", [])
                elif isinstance(raw_response, str):
                    final_text = raw_response
                    tool_calls = getattr(st.session_state.agent, "last_tool_calls", [])
                else:
                    final_text = getattr(raw_response, "text", str(raw_response))
                    tool_calls = getattr(raw_response, "tool_calls", [])

                # Bước 3: Tool Execution Log
                if tool_calls:
                    step_logs.append({
                        "step": "3. Tool Execution",
                        "desc": f"Thực thi {len(tool_calls)} tool(s)",
                        "elapsed": 0.05,
                    })
                else:
                    step_logs.append({
                        "step": "3. Direct Response",
                        "desc": "Trả lời trực tiếp (không cần tool)",
                        "elapsed": 0.0,
                    })

                total_time = round(time.time() - start_total_time, 2)
                status_box.update(label=f" Hoàn tất trong {total_time}s!", state="complete", expanded=False)

                # Hiển thị câu trả lời
                msg_placeholder.markdown(final_text)

                # Ước lượng Token
                est_prompt_tokens = int(len(prompt.split()) * 1.3) + 1200
                est_completion_tokens = int(len(final_text.split()) * 1.3)
                token_usage = {
                    "prompt_tokens": est_prompt_tokens,
                    "completion_tokens": est_completion_tokens,
                    "total_tokens": est_prompt_tokens + est_completion_tokens
                }

                # Lưu telemetry
                st.session_state.latest_telemetry = {
                    "total_time": total_time,
                    "steps": step_logs,
                    "tool_calls": tool_calls,
                    "token_usage": token_usage,
                }

                # Lưu vào lịch sử chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_text,
                    "tool_calls": tool_calls
                })

            except Exception as e:
                status_box.update(label="❌ Lỗi thực thi", state="error")
                st.error(f"Chi tiết lỗi: {str(e)}")

# ----------------- CỘT 2: GIÁM SÁT TIẾN TRÌNH & METRICS -----------------
with col_inspect:
    st.subheader("📊 Live Telemetry & Inspector")

    telemetry = st.session_state.latest_telemetry
    if telemetry:
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("⏱️ Tổng thời gian", f"{telemetry['total_time']} s")
        
        usage = telemetry["token_usage"]
        kpi2.metric("🪙 Tokens dùng", f"{usage.get('total_tokens', 0):,}")
        kpi3.metric("🛠️ Tool Calls", len(telemetry["tool_calls"]))

        st.divider()

        st.markdown("**💰 Tiêu hao Token**")
        tok_col1, tok_col2 = st.columns(2)
        tok_col1.write(f"- **Input:** `{usage.get('prompt_tokens', 0):,}`")
        tok_col2.write(f"- **Output:** `{usage.get('completion_tokens', 0):,}`")

        st.divider()

        st.markdown("**🧭 Tiến trình chạy chi tiết**")
        for s in telemetry["steps"]:
            with st.container(border=True):
                c_a, c_b = st.columns([4, 1])
                c_a.markdown(f"**{s['step']}**")
                c_a.caption(s["desc"])
                c_b.write(f"`{s['elapsed']}s`")

        if telemetry["tool_calls"]:
            st.divider()
            st.markdown("**🔍 Payload công cụ đã kích hoạt**")
            for idx, tc in enumerate(telemetry["tool_calls"], 1):
                st.code(
                    f"Tool #{idx}: {tc.get('name')}\nArgs: {json.dumps(tc.get('args', {}), indent=2, ensure_ascii=False)}",
                    language="json"
                )
    else:
        st.info("💡 Chưa có lượt truy vấn nào. Hãy gửi một câu hỏi ở khung chat bên trái để xem biểu đồ thời gian và lượng token tiêu tốn theo thời gian thực!")