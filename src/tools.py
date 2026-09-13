"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "search_doctors",
        "description": "Tìm kiếm bác sĩ theo chuyên khoa và cơ sở Vinmec.",
        "parameters": {
            "type": "object",
            "properties": {
                "specialty": {
                    "type": "string",
                    "description": "Chuyên khoa cần tìm, ví dụ: Tim mạch, Nhi khoa, Da liễu."
                },
                "location": {
                    "type": "string",
                    "description": "Địa điểm hoặc cơ sở Vinmec cần tìm."
                }
            },
            "required": ["specialty"]
        }
    },

    {
        "name": "get_doctor_schedule",
        "description": "Tra cứu lịch làm việc của một bác sĩ tại Vinmec.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "string",
                    "description": "Mã bác sĩ cần tra cứu."
                },
                "date": {
                    "type": "string",
                    "description": "Ngày cần tra cứu lịch, định dạng DD/MM/YYYY."
                }
            },
            "required": ["doctor_id", "date"]
        }
    },

    {
        "name": "schedule_appointment",
        "description": "Đặt lịch khám với bác sĩ tại Vinmec.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "string",
                    "description": "Mã bác sĩ cần đặt lịch."
                },
                "date": {
                    "type": "string",
                    "description": "Ngày khám, định dạng DD/MM/YYYY."
                },
                "time": {
                    "type": "string",
                    "description": "Giờ khám, ví dụ: 09:00."
                },
                "patient_name": {
                    "type": "string",
                    "description": "Tên bệnh nhân."
                }
            },
            "required": [
                "doctor_id",
                "date",
                "time",
                "patient_name"
            ]
        }
    }
]
# ============================================================================== 
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DOCTORS = {
    "DOC001": {
        "name": "BS. Nguyễn Văn An",
        "specialty": "Tim mạch",
        "location": "Vinmec Times City"
    },
    "DOC002": {
        "name": "BS. Trần Thị Bình",
        "specialty": "Nhi khoa",
        "location": "Vinmec Times City"
    },
    "DOC003": {
        "name": "BS. Lê Minh Anh",
        "specialty": "Da liễu",
        "location": "Vinmec Central Park"
    }
}


# Lịch làm việc mô phỏng
# LƯU Ý: Đây là dữ liệu giả để làm Lab, không phải lịch thật của Vinmec.
MOCK_SCHEDULES = {
    "DOC001": {
        "13/09/2026": ["09:00", "10:00", "14:00"],
        "14/09/2026": ["08:30", "10:30", "15:00"]
    },
    "DOC002": {
        "13/09/2026": ["08:00", "09:30", "13:30"],
        "15/09/2026": ["09:00", "11:00", "14:30"]
    },
    "DOC003": {
        "13/09/2026": ["10:00", "11:00", "15:30"],
        "16/09/2026": ["08:30", "13:00", "16:00"]
    }
}


# ==============================================================================
# TOOL 1: TÌM KIẾM BÁC SĨ
# ==============================================================================

def execute_search_doctors(
    specialty: str,
    location: str = ""
) -> str:
    """Tìm bác sĩ theo chuyên khoa và cơ sở."""

    results = []

    for doctor_id, doctor in MOCK_DOCTORS.items():

        specialty_match = (
            specialty.strip().lower()
            in doctor["specialty"].lower()
        )

        location_match = (
            not location.strip()
            or location.strip().lower()
            in doctor["location"].lower()
        )

        if specialty_match and location_match:
            results.append({
                "doctor_id": doctor_id,
                **doctor
            })

    if results:
        return json.dumps({
            "status": "SUCCESS",
            "doctors": results
        }, ensure_ascii=False)

    return json.dumps({
        "status": "NOT_FOUND",
        "message": f"Không tìm thấy bác sĩ chuyên khoa '{specialty}'."
    }, ensure_ascii=False)


# ==============================================================================
# TOOL 2: TRA CỨU LỊCH BÁC SĨ
# ==============================================================================

def execute_get_doctor_schedule(
    doctor_id: str,
    date: str
) -> str:
    """Tra cứu các khung giờ khám còn trống của bác sĩ."""

    doctor_id = doctor_id.strip().upper()

    # Kiểm tra bác sĩ có tồn tại không
    doctor = MOCK_DOCTORS.get(doctor_id)

    if not doctor:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy bác sĩ có mã '{doctor_id}'."
        }, ensure_ascii=False)

    # Lấy lịch
    slots = MOCK_SCHEDULES.get(doctor_id, {}).get(date, [])

    return json.dumps({
        "status": "SUCCESS",
        "doctor_id": doctor_id,
        "doctor": doctor,
        "date": date,
        "available_slots": slots,
        "message": (
            f"Bác sĩ {doctor['name']} có "
            f"{len(slots)} khung giờ còn trống vào ngày {date}."
        )
    }, ensure_ascii=False)


# ==============================================================================
# TOOL 3: ĐẶT LỊCH KHÁM
# ==============================================================================

def execute_schedule_appointment(
    doctor_id: str,
    date: str,
    time: str,
    patient_name: str
) -> str:
    """Đặt lịch khám với bác sĩ."""

    doctor_id = doctor_id.strip().upper()

    # Kiểm tra bác sĩ
    doctor = MOCK_DOCTORS.get(doctor_id)

    if not doctor:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy bác sĩ có mã '{doctor_id}'."
        }, ensure_ascii=False)

    # Kiểm tra lịch
    available_slots = MOCK_SCHEDULES.get(
        doctor_id, {}
    ).get(date, [])

    # Kiểm tra giờ có tồn tại trong lịch không
    if time not in available_slots:
        return json.dumps({
            "status": "UNAVAILABLE",
            "message": (
                f"Khung giờ {time} ngày {date} "
                f"không còn trống với {doctor['name']}."
            ),
            "available_slots": available_slots
        }, ensure_ascii=False)

    # Tạo mã đặt lịch giả
    booking_id = f"BK-{doctor_id}-{date.replace('/', '')}-{time.replace(':', '')}"

    return json.dumps({
        "status": "SUCCESS",
        "booking_id": booking_id,
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"],
        "date": date,
        "time": time,
        "patient_name": patient_name,
        "message": (
            f"Đặt lịch thành công cho bệnh nhân {patient_name} "
            f"với {doctor['name']} vào lúc {time}, ngày {date}."
        )
    }, ensure_ascii=False)


# ==============================================================================
# ROUTER - ĐỊNH TUYẾN TOOL
# ==============================================================================

TOOL_ROUTER = {
    "search_doctors": execute_search_doctors,
    "get_doctor_schedule": execute_get_doctor_schedule,
    "schedule_appointment": execute_schedule_appointment
}


# ==============================================================================
# DISPATCH TOOL CALL
# ==============================================================================

def dispatch_tool_call(
    tool_name: str,
    arguments: Dict[str, Any]
) -> str:
    """Hàm trung chuyển thực thi tool."""

    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)

        except Exception as e:
            return json.dumps({
                "status": "EXECUTION_ERROR",
                "error": str(e)
            }, ensure_ascii=False)

    return json.dumps({
        "status": "UNKNOWN_TOOL",
        "error": f"Tool '{tool_name}' không tồn tại!"
    }, ensure_ascii=False)


# ==============================================================================
# TEST NHANH
# ==============================================================================

if __name__ == "__main__":

    print("\n=== TEST 1: SEARCH DOCTORS ===")

    result = dispatch_tool_call(
        "search_doctors",
        {
            "specialty": "Tim mạch"
        }
    )

    print(result)


    print("\n=== TEST 2: GET DOCTOR SCHEDULE ===")

    result = dispatch_tool_call(
        "get_doctor_schedule",
        {
            "doctor_id": "DOC001",
            "date": "13/09/2026"
        }
    )

    print(result)


    print("\n=== TEST 3: SCHEDULE APPOINTMENT ===")

    result = dispatch_tool_call(
        "schedule_appointment",
        {
            "doctor_id": "DOC001",
            "date": "13/09/2026",
            "time": "09:00",
            "patient_name": "Nguyen Van A"
        }
    )

    print(result)