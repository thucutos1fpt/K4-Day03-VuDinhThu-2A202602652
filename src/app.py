"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)

So sánh:
- Chatbot Baseline: chỉ gọi LLM, không có Tool
- ReAct Agent: LLM -> Tool -> Observation -> LLM -> ...

Kết nối Tool thông qua MCP Server.
"""

import json
import os
import sys
import time

from dotenv import load_dotenv

# Cho phép import các file trong cùng thư mục src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp_server import MCPAcademicServer
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)
from providers import get_llm_provider


load_dotenv()


# ============================================================
# 1. LOAD TEST CASES
# ============================================================

def load_test_cases():
    """
    Tải test cases từ:
    config/test_cases.json

    Nếu chưa có thì dùng:
    config/test_cases.example.json
    """

    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    config_path = os.path.join(
        base_dir,
        "config",
        "test_cases.json"
    )

    if not os.path.exists(config_path):

        example_path = os.path.join(
            base_dir,
            "config",
            "test_cases.example.json"
        )

        if os.path.exists(example_path):
            print(
                "⚠️ [CONFIG NOTICE]: "
                "Chưa thấy file 'config/test_cases.json'. "
                "Đang dùng file mẫu."
            )

            print(
                "👉 Hãy tạo config/test_cases.json "
                "theo đề tài Vinmec.\n"
            )

            config_path = example_path

        else:
            config_path = "test_cases.json"

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# 2. SAVE WATERFALL TRACE
# ============================================================

def save_waterfall_trace(trace_data: list):
    """
    Lưu Waterfall Trace vào:
    docs/trace_waterfall.json
    """

    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    docs_dir = os.path.join(
        base_dir,
        "docs"
    )

    os.makedirs(
        docs_dir,
        exist_ok=True
    )

    trace_path = os.path.join(
        docs_dir,
        "trace_waterfall.json"
    )

    with open(
        trace_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            trace_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"📊 [OBSERVABILITY]: "
        f"Đã lưu {len(trace_data)} sự kiện "
        f"Waterfall Trace tại '{trace_path}'!"
    )


# ============================================================
# 3. BASELINE CHATBOT
# ============================================================

def run_baseline_chatbot(
    user_query: str,
    provider
):
    """
    Chatbot baseline:
    - Không có Tool
    - Không có MCP
    - Chỉ gọi LLM
    """

    print(
        f"\n💬 [CHATBOT BASELINE] "
        f"Câu hỏi: {user_query}"
    )

    response = provider.generate(
        user_query,
        system_prompt=CHATBOT_BASELINE_PROMPT
    )

    print(
        f"🤖 Chatbot phản hồi:\n{response}"
    )

    return response


# ============================================================
# 4. REACT AGENT LOOP
# ============================================================

def run_react_agent(
    user_query: str,
    provider,
    mcp_server: MCPAcademicServer
) -> list:

    """
    ReAct Agent Loop:

        Thought
           ↓
        Action
           ↓
        Observation
           ↓
        Thought
           ↓
        Action
           ↓
        Observation
           ↓
        Final Answer

    Agent có thể gọi nhiều Tool liên tiếp
    cho tới khi có câu trả lời cuối cùng.
    """

    print(
        f"\n🤖 [REACT AGENT] "
        f"Câu hỏi: {user_query}"
    )

    # --------------------------------------------------------
    # Biến lưu trạng thái
    # --------------------------------------------------------

    step = 0

    trace_logs = []

    tools_list = mcp_server.list_tools()

    # --------------------------------------------------------
    # Context dùng để đưa Observation quay lại cho LLM
    # --------------------------------------------------------

    agent_context = (
        f"User Query:\n{user_query}\n\n"
    )

    # --------------------------------------------------------
    # REACT LOOP
    # --------------------------------------------------------

    while step < MAX_ITERATIONS:

        step += 1

        step_start_time = time.time()

        print(
            f"\n--- 🔄 ReAct Loop "
            f"(Step {step}/{MAX_ITERATIONS}) ---"
        )

        # ====================================================
        # STEP 1 — GỌI LLM
        # ====================================================

        llm_response = provider.generate_with_tools(
            agent_context,
            tools_list,
            system_prompt=REACT_AGENT_SYSTEM_PROMPT
        )

        latency_ms = round(
            (time.time() - step_start_time) * 1000,
            2
        )

        thought = llm_response.get(
            "thought",
            "Đang suy luận..."
        )

        print(
            f"🧠 [Thought]: {thought}"
        )

        # ====================================================
        # STEP 2 — LLM TRẢ VỀ FINAL ANSWER
        # ====================================================

        if llm_response.get("type") == "text":

            final_content = llm_response.get(
                "content",
                ""
            )

            print(
                f"🏁 [Final Answer]: "
                f"{final_content}"
            )

            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })

            break

        # ====================================================
        # STEP 3 — LLM GỌI TOOL
        # ====================================================

        elif llm_response.get("type") == "tool_call":

            tool_name = llm_response.get(
                "tool_name"
            )

            arguments = llm_response.get(
                "arguments",
                {}
            )

            print(
                f"🛠️ [Action Proposed]: "
                f"{tool_name}({arguments})"
            )

            # =================================================
            # STEP 4 — MCP SERVER THỰC THI TOOL
            # =================================================

            tool_start_time = time.time()

            try:

                mcp_result = mcp_server.call_tool(
                    tool_name,
                    arguments
                )

                obs_data = mcp_result.get(
                    "result",
                    {}
                )

            except Exception as e:

                obs_data = {
                    "status": "ERROR",
                    "message": str(e)
                }

            tool_latency_ms = round(
                (time.time() - tool_start_time) * 1000,
                2
            )

            # =================================================
            # STEP 5 — OBSERVATION
            # =================================================

            obs_str = json.dumps(
                obs_data,
                ensure_ascii=False
            )

            print(
                f"👁️ [Observation từ MCP Server]: "
                f"{obs_str}"
            )

            # =================================================
            # TRACE TOOL EXECUTION
            # =================================================

            trace_logs.append({

                "step": step,

                "query": user_query,

                "action_type": "TOOL_EXECUTION",

                "tool_name": tool_name,

                "arguments": arguments,

                "observation": obs_data,

                "latency_ms": tool_latency_ms

            })

            # =================================================
            # STEP 6 — QUAN TRỌNG:
            # ĐƯA OBSERVATION QUAY LẠI CHO AGENT
            # =================================================

            agent_context += (
                "\n\n"
                f"Action:\n"
                f"{tool_name}({json.dumps(arguments, ensure_ascii=False)})\n"
                "\n"
                f"Observation:\n"
                f"{obs_str}\n"
            )

            # ------------------------------------------------
            # Nhắc Agent rằng nó phải tiếp tục suy luận
            # thay vì kết thúc ngay sau 1 Tool.
            # ------------------------------------------------

            agent_context += (
                "\n"
                "Hãy tiếp tục xử lý dựa trên Observation ở trên. "
                "Nếu còn thiếu thông tin hoặc cần Tool khác, "
                "hãy gọi Tool tiếp theo. "
                "Chỉ trả lời cuối cùng khi đã đủ thông tin.\n"
            )

            print(
                "🔁 [REACT]: "
                "Observation đã được đưa lại cho Agent."
            )

            # ------------------------------------------------
            # Không break ở đây!
            #
            # Vòng while sẽ chạy tiếp.
            # ------------------------------------------------

            continue

        # ====================================================
        # STEP 7 — RESPONSE KHÔNG HỢP LỆ
        # ====================================================

        else:

            print(
                "⚠️ [ERROR]: "
                "LLM trả về response không hợp lệ."
            )

            error_message = (
                "Xin lỗi, Agent không thể xử lý "
                "yêu cầu này."
            )

            trace_logs.append({

                "step": step,

                "query": user_query,

                "action_type": "FINAL_ANSWER",

                "thought": "Response không hợp lệ.",

                "output": error_message,

                "latency_ms": latency_ms

            })

            break

    # ========================================================
    # STEP 8 — KIỂM TRA MAX ITERATIONS
    # ========================================================

    if step >= MAX_ITERATIONS:

        print(
            f"\n⚠️ [MAX ITERATIONS]: "
            f"Agent đã đạt giới hạn {MAX_ITERATIONS} vòng."
        )

        trace_logs.append({

            "step": step + 1,

            "query": user_query,

            "action_type": "FINAL_ANSWER",

            "thought": (
                "Agent dừng vì đạt MAX_ITERATIONS."
            ),

            "output": (
                "Agent đã đạt giới hạn số vòng "
                "suy luận cho phép."
            ),

            "latency_ms": 0

        })

    return trace_logs


# ============================================================
# 5. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        "=========================================================="
    )

    print(
        "🏥 VINMEC AI COURSE - DAY 03 LAB"
    )

    print(
        "🤖 CHATBOT VS REACT AGENT + MCP"
    )

    print(
        "=========================================================="
    )

    # --------------------------------------------------------
    # Khởi tạo LLM Provider
    # --------------------------------------------------------

    provider = get_llm_provider()

    # --------------------------------------------------------
    # Khởi tạo MCP Server
    # --------------------------------------------------------

    mcp_server = MCPAcademicServer()

    print(
        f"🔌 LLM Provider: "
        f"{provider.__class__.__name__}"
    )

    print(
        f"🌐 MCP Server: "
        f"{mcp_server.server_name}\n"
    )

    # --------------------------------------------------------
    # Load test cases
    # --------------------------------------------------------

    tests = load_test_cases()

    print(
        f"✅ Đã tải thành công "
        f"{len(tests)} Test Cases thử nghiệm.\n"
    )

    # ========================================================
    # INTERACTIVE MODE
    # ========================================================

    if "--interactive" in sys.argv:

        print(
            "🎮 [INTERACTIVE MODE] "
            "Trò chuyện trực tiếp với ReAct Agent:"
        )

        print(
            "💡 Gợi ý câu hỏi:"
        )

        print(
            "   - "
            "'Tìm bác sĩ Tim mạch'"
        )

        print(
            "   - "
            "'Tìm bác sĩ Nhi khoa'"
        )

        print(
            "   - "
            "'Tìm bác sĩ Da liễu'"
        )

        print(
            "   - "
            "'Cho tôi xem lịch bác sĩ DOC001'"
        )

        print(
            "   - "
            "'Tôi muốn đặt lịch khám'"
        )

        print(
            "   - "
            "Gõ 'exit' hoặc 'quit' để thoát.\n"
        )

        while True:

            try:

                user_input = input(
                    "👤 Người dùng hỏi: "
                ).strip()

                if (
                    not user_input
                    or user_input.lower()
                    in ["exit", "quit"]
                ):

                    print(
                        "👋 Tạm biệt! "
                        "Kết thúc phiên trò chuyện."
                    )

                    break

                logs = run_react_agent(
                    user_input,
                    provider,
                    mcp_server
                )

                save_waterfall_trace(logs)

            except (
                KeyboardInterrupt,
                EOFError
            ):

                print(
                    "\n👋 Đã thoát phiên tương tác."
                )

                break

    # ========================================================
    # TEST SUITE MODE
    # ========================================================

    elif "--all" in sys.argv:

        print(
            "🚀 [TEST SUITE MODE] "
            "Kiểm tra toàn bộ Test Cases:"
        )

        completed_count = 0

        todo_count = 0

        all_traces = []

        for tc in tests:

            print(
                "\n=================================================="
            )

            print(
                f"🧪 [{tc['id']}] "
                f"Loại test: {tc['type']} "
                f"(Độ phức tạp: {tc['complexity']})"
            )

            print(
                f"📌 Kỳ vọng: "
                f"{tc['expected_behavior']}"
            )

            question = tc["question"].strip()

            if question.startswith("TODO"):

                print(
                    "⏸️ [CHƯA KÍCH HOẠT - TODO]:"
                )

                print(
                    f"   {question}"
                )

                todo_count += 1

            else:

                logs = run_react_agent(
                    question,
                    provider,
                    mcp_server
                )

                all_traces.extend(logs)

                completed_count += 1

        print(
            "\n=================================================="
        )

        print(
            f"📊 [KẾT QUẢ TEST SUITE]: "
            f"Đã thực thi "
            f"{completed_count}/{len(tests)} Test Cases"
        )

        print(
            f"⏸️ {todo_count} Test Cases đang là TODO."
        )

        if all_traces:

            save_waterfall_trace(
                all_traces
            )

        print(
            "\n💡 Chat trực tiếp:"
        )

        print(
            "python src/app.py --interactive"
        )

    # ========================================================
    # DEFAULT MODE
    # ========================================================

    else:

        print(
            "ℹ️ HƯỚNG DẪN SỬ DỤNG:"
        )

        print(
            "  1. Chat trực tiếp:"
        )

        print(
            "     python src/app.py --interactive"
        )

        print(
            "  2. Chạy toàn bộ Test Cases:"
        )

        print(
            "     python src/app.py --all"
        )

        # ----------------------------------------------------
        # Demo test đầu tiên không phải TODO
        # ----------------------------------------------------

        demo_test = None

        for tc in tests:

            question = tc.get(
                "question",
                ""
            ).strip()

            if question and not question.startswith("TODO"):

                demo_test = tc

                break

        if demo_test:

            print(
                "\n--- 🏁 DEMO CHẠY THỬ ---"
            )

            print(
                f"Test Case: {demo_test['id']}"
            )

            logs = run_react_agent(
                demo_test["question"],
                provider,
                mcp_server
            )

            save_waterfall_trace(
                logs
            )

        else:

            print(
                "\n⚠️ Chưa có Test Case hợp lệ "
                "để chạy demo."
            )