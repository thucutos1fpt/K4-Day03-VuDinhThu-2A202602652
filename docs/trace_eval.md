# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Vũ Đình Thư
> **Mã Sinh Viên / Mã Học viên:** 2A202602652  
> **Chủ đề Lựa chọn:**  Trợ lý Tư vấn Sức khỏe Vinmec: Tra cứu lịch làm việc bác sĩ chuyên khoa và đặt lịch khám bệnh 
---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 5 / 5 | Bài toán có yêu cầu chia nhỏ nhiều bước suy luận nối tiếp nhau không? |
| **2. Tool Interaction** | 5 / 5 | Hệ thống có cần kết nối với MCP Server / Cơ sở dữ liệu bên ngoài không? |
| **3. Dynamic Decision** | 5 / 5 | Bước tiếp theo có phụ thuộc vào kết quả quan sát bước trước không? |
| **4. Long Horizon Goal** | 5 / 5 | Hệ thống có phải giữ mục tiêu xuyên suốt qua nhiều lượt xử lý không? |
| **TỔNG ĐIỂM AGENTIC FIT** | **18 / 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Agent được cấu hình sử dụng Gemini API thật thông qua GEMINI_API_KEY trong tệp .env. Model sử dụng là gemini-3.6-flash. Agent đã chạy thành công trên LLM API thật và không sử dụng Mock Offline Provider trong lần kiểm thử.

Một đoạn Waterfall Trace tiêu biểu của Agent với truy vấn: “Tìm bác sĩ Da liễu và cho tôi xem lịch khám ngày 13/09/2026”

[ { "step": 1, "action_type": "TOOL_EXECUTION", "tool_name": "search_doctors", "arguments": { "specialty": "Da liễu" }, "observation": { "status": "SUCCESS", "doctors": [ { "id": "DOC003", "name": "BS. Lê Minh Anh", "specialty": "Da liễu", "location": "Vinmec Central Park" } ] } }, { "step": 2, "action_type": "TOOL_EXECUTION", "tool_name": "get_doctor_schedule", "arguments": { "doctor_id": "DOC003", "date": "13/09/2026" }, "observation": { "status": "SUCCESS", "doctor_id": "DOC003", "date": "13/09/2026", "available_slots": [ "10:00", "11:00", "15:30" ] } } ]

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 3 lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
