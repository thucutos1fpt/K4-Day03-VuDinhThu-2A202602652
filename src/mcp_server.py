"""
MCP SERVER
Server trung gian kết nối Agent với các Tools.
"""

import json
from typing import Dict, Any

from tools import TOOLS_SCHEMA, dispatch_tool_call


class MCPAcademicServer:

    def __init__(self):
        self.server_name = "vinmec-health-mcp-server"
        self.version = "2026.1.0"

    def list_tools(self):
        """Trả về danh sách các tools mà MCP Server công bố."""
        return TOOLS_SCHEMA

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gọi một tool thông qua execution layer.
        """

        # Bước 1: Gọi dispatcher
        content = dispatch_tool_call(
            tool_name,
            arguments
        )

        # Bước 2: Chuyển JSON string thành Python dictionary
        result = json.loads(content)

        # Bước 3: Đóng gói kết quả theo format MCP
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": result
        }


# ==============================================================================
# KIỂM THỬ ĐỘC LẬP MCP SERVER
# ==============================================================================

if __name__ == "__main__":

    print("=" * 58)
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER")
    print("=" * 58)

    # Khởi tạo server
    server = MCPAcademicServer()

    print(
        f"✅ Khởi tạo thành công MCP Server: "
        f"{server.server_name} "
        f"(Version: {server.version})"
    )

    # Kiểm tra số lượng tools
    tools = server.list_tools()

    print(
        f"📦 Số lượng Tools công bố: {len(tools)}"
    )

    # Kiểm tra schema
    tool_names = [
        tool["name"]
        for tool in tools
    ]

    print(f"🔧 Tools: {tool_names}")

    # --------------------------------------------------------------------------
    # TEST 1: Search doctors
    # --------------------------------------------------------------------------

    print("\n" + "-" * 58)
    print("🧪 TEST 1: search_doctors")
    print("-" * 58)

    result = server.call_tool(
        "search_doctors",
        {
            "specialty": "Tim mạch"
        }
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ))

    # --------------------------------------------------------------------------
    # TEST 2: Get doctor schedule
    # --------------------------------------------------------------------------

    print("\n" + "-" * 58)
    print("🧪 TEST 2: get_doctor_schedule")
    print("-" * 58)

    result = server.call_tool(
        "get_doctor_schedule",
        {
            "doctor_id": "DOC001",
            "date": "13/09/2026"
        }
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ))

    # --------------------------------------------------------------------------
    # TEST 3: Schedule appointment
    # --------------------------------------------------------------------------

    print("\n" + "-" * 58)
    print("🧪 TEST 3: schedule_appointment")
    print("-" * 58)

    result = server.call_tool(
        "schedule_appointment",
        {
            "doctor_id": "DOC001",
            "date": "13/09/2026",
            "time": "09:00",
            "patient_name": "Nguyen Van A"
        }
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ))

    print("\n" + "=" * 58)
    print("✅ MCP SERVER TEST HOÀN TẤT")
    print("=" * 58)