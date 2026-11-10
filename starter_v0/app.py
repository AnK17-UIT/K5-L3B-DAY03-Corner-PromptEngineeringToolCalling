import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

st.set_page_config(page_title="Corner Research Agent")
st.title("Corner Research Agent")
st.caption("Tìm kiếm, đọc và tổng hợp nguồn. Chế độ demo hỗ trợ nghiên cứu và soạn nội dung.")
with st.sidebar:
    st.markdown("**Gợi ý dùng thử**")
    st.write("Tìm 3 bài arXiv mới về retrieval-augmented generation.")
    st.write("Tìm 3 tin web về pin thể rắn trong một tháng qua.")
    st.write("Lọc URL trùng: https://example.com/a, https://example.com/b, https://example.com/a.")
    if st.button("Cuộc trò chuyện mới"):
        st.session_state.history = []
        st.session_state.events = []

history = st.session_state.setdefault("history", [])
events = st.session_state.setdefault("events", [])


def show_calls(tool_names: list[str]) -> None:
    if tool_names:
        st.caption("Công cụ đã gọi: " + ", ".join(tool_names))


for index, message in enumerate(history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            show_calls(events[index // 2])

if user_text := st.chat_input("Nhập yêu cầu nghiên cứu"):
    with st.chat_message("user"):
        st.markdown(user_text)
    with st.chat_message("assistant"), st.spinner("Đang xử lý…"):
        try:
            prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
            prompt += "\nChế độ demo chỉ hỗ trợ soạn nội dung. Không tuyên bố đã đăng hoặc gửi."
            tools = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))
            result = run_model_tool_loop(
                provider=make_provider("openai"),
                messages=[
                    {"role": "system", "content": prompt},
                    *trim_history(history, 5),
                    {"role": "user", "content": user_text},
                ],
                tools=[tool for tool in tools if tool["function"]["name"] != "send"],
                model="gpt-4o-mini",
                max_tool_rounds=4,
            )
        except Exception:
            st.error("Không xử lý được yêu cầu. Kiểm tra cấu hình OpenAI và thử lại.")
        else:
            answer = result["assistant_text"]
            tool_names = [event["tool"] for event in result["tool_events"]]
            st.markdown(answer)
            show_calls(tool_names)
            history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": answer},
            ])
            events.append(tool_names)
