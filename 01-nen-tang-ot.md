# 1 · Nền tảng OT cho người mới

Thời lượng: 60 phút. Phần lý thuyết duy nhất của khoá — phần còn lại là thực
hành.

## 1.1 OT là gì, khác IT chỗ nào

**IT** xử lý thông tin. **OT** (Operational Technology) điều khiển vật lý: bơm
chạy hay dừng, van mở bao nhiêu phần trăm, hoá chất châm bao nhiêu mg/L.

Khác biệt quyết định cách ta phân tích:

| | IT | OT |
|---|---|---|
| Hậu quả xấu nhất | mất/lộ dữ liệu | sự cố vật lý: tràn bể, quá áp, bơm chạy khô, mất điện |
| Ưu tiên | Bảo mật → Toàn vẹn → Sẵn sàng | **Sẵn sàng → Toàn vẹn → Bảo mật** |
| Vòng đời thiết bị | 3–5 năm | 15–25 năm |
| Vá lỗi | hàng tháng | theo kỳ dừng máy, có khi vài năm một lần |
| Lưu lượng mạng | đa dạng, khó đoán | lặp lại, có chu kỳ, các cặp host cố định |

Dòng cuối là món quà cho người phân tích: **traffic OT đều đặn đến mức bất
thường rất dễ lộ**. Một host nói chuyện với 20 thiết bị trong mạng điều khiển
gần như chắc chắn là công cụ, không phải thiết bị.

## 1.2 Các thành phần

- **PLC** (Programmable Logic Controller): máy tính công nghiệp chạy một
  chương trình nhỏ lặp đi lặp lại — đọc cảm biến, quyết định, xuất tín hiệu.
  Vòng lặp đó gọi là *scan cycle*, thường vài chục lần mỗi giây.
- **RTU** (Remote Terminal Unit): như PLC nhưng thiên về thu thập và báo cáo
  từ xa, hay gặp trong điện lực và cấp nước.
- **HMI** (Human-Machine Interface): màn hình của người vận hành. Bản thân nó
  không điều khiển gì — nó đọc giá trị từ PLC và gửi lệnh của operator xuống.
- **SCADA**: hệ thống giám sát và điều khiển cấp trên, gom nhiều PLC/RTU.
- **Historian**: cơ sở dữ liệu lưu giá trị quá trình theo thời gian. Thường là
  SQL Server, và thường là bàn đạp để đi tiếp.
- **BMS** (Building Management System): điều khiển cửa, đèn, điều hoà, cảm
  biến hiện diện. Hay bị bỏ quên khi kiểm kê tài sản.

Một vài từ xuất hiện liên tục:

- **tag** / **point**: một giá trị có tên trong bộ điều khiển — `TANK_LEVEL`,
  `PUMP_RUN`, `CL2_DOSE_A`.
- **setpoint**: giá trị mục tiêu mà vòng điều khiển hướng tới. Đổi setpoint là
  đổi hành vi nhà máy **mà không cần sửa một dòng code nào** — nên nó là đích
  ưa thích.
- **coil**: một bit ra on/off trong Modbus. Ép một coil có thể khởi động bơm
  hoặc tắt còi báo động.
- **interlock**: điều kiện an toàn khoá lẫn nhau, ví dụ không cho chạy bơm khi
  van hút chưa mở.

## 1.3 Vì sao gần như mọi phát hiện đều quy về một điều

**Các giao thức công nghiệp không có xác thực.**

Chúng được thiết kế cho một sợi cáp riêng, tin cậy, trong một nhà máy mà ai
vào được phòng điều khiển thì đã có quyền. Không có mật khẩu, không có mã hoá,
không có phiên. Ai định tuyến được tới thiết bị thì gửi được lệnh hợp lệ.

Những thứ trông giống kiểm soát an ninh thực ra không phải:

- Mật khẩu **DCC** của BACnet: chuỗi rõ, không giới hạn số lần thử, không khoá.
- **Unit id** của Modbus: địa chỉ thiết bị phía sau gateway, không phải danh
  tính.
- **Protection level** của Siemens: có tác dụng, nhưng là tuỳ chọn cấu hình và
  thường để mặc định.

Hệ quả thực tế: **phân đoạn mạng và danh sách cho phép (allow-list) là biện
pháp bảo vệ chính**, vì bản thân giao thức không tự bảo vệ được.

## 1.4 Các giao thức sẽ gặp trong khoá

| Giao thức | Cổng | Dùng ở đâu | Gặp ở lab |
|---|---|---|---|
| BACnet/IP | UDP 47808 | toà nhà: cửa, đèn, điều hoà | Lab 1 |
| Modbus/TCP | TCP 502 | PLC nhỏ, skid đóng gói, biến tần | Lab 2 |
| S7comm | TCP 102 | PLC Siemens S7-300/400 | Lab 3 |
| IEC 60870-5-104 | TCP 2404 | truyền tải và phân phối điện | Lab 4 |
| DNP3 | TCP 20000 | trạm biến áp, cấp nước (Bắc Mỹ) | Lab 4 mở rộng |

## 1.5 Bốn câu hỏi

Mọi lab trong khoá đều là một cách hỏi lại bốn câu này:

1. **Ai đã nói chuyện?** Traffic điều khiển đi giữa các cặp host cố định. Một
   host liên hệ nhiều thiết bị, hoặc chỉ hỏi mà không bao giờ trả lời, là công
   cụ chứ không phải thiết bị.
2. **Đọc hay ghi?** Đọc là giám sát. **Ghi** — ép một coil, đổi một setpoint,
   tải một khối logic — mới là thứ thay đổi quá trình vật lý.
3. **Thiết bị có chấp nhận không?** Mọi giao thức trong khoá đều trả lời khác
   nhau cho thành công và từ chối. Lệnh bị từ chối cũng là bằng chứng: nó cho
   biết kẻ tấn công đã **thử** gì mà không làm được.
4. **Theo thứ tự nào?** Kẻ tấn công thường **làm im tiếng báo cáo trước, rồi
   mới ra tay**. Một mốc thời gian nói được nhiều hơn bất kỳ gói tin đơn lẻ nào.

## 1.6 Dấu hiệu thành công và từ chối, theo giao thức

Bảng này nên in ra dán cạnh màn hình trong suốt khoá:

| Giao thức | Dấu hiệu bị từ chối |
|---|---|
| BACnet | Error PDU, class `security`, code `password-failure` |
| S7comm | ack-data có error class/code khác 0 |
| Modbus | mã hàm **OR 0x80** kèm exception code |
| IEC-104 | actcon có cờ **P/N** (negative) |
| DNP3 | cờ IIN: `func-not-supported`, `already-executing` |

## 1.7 Mô hình giai đoạn tấn công OT

Dùng để hiểu vì sao các lab xếp theo thứ tự này:

1. **Truy cập ban đầu và di chuyển ngang** — phía IT: khai thác dịch vụ, lấy
   tài khoản, nhảy vào vùng DMZ của OT. *(Lab 5, Lab 6)*
2. **Thu thập** — kiểm kê môi trường: quét, đọc thông tin thiết bị, truy vấn
   historian. *(Lab 2, Lab 3)*
3. **Làm tê liệt chức năng phản hồi** — tắt báo động và báo cáo để người vận
   hành không thấy gì. *(Lab 1, Lab 4)*
4. **Làm sai lệch điều khiển** — đổi setpoint, ép coil, tải logic. *(Lab 2,
   Lab 3, Lab 4)*
5. **Tác động** — quá trình vật lý ra ngoài vùng an toàn. *(câu hỏi cuối của
   từng lab)*

Ánh xạ chi tiết sang MITRE ATT&CK for ICS có trong
[`docs/attack-mapping.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/attack-mapping.md).

## Câu hỏi nhanh cuối phần (5 phút, hỏi miệng)

1. Vì sao thứ tự ưu tiên của OT lại đảo ngược so với IT?
2. Một host trong mạng BACnet gửi 300 yêu cầu và không trả lời yêu cầu nào.
   Nó là gì?
3. Modbus function code 3 và function code 6 khác nhau ở điểm nào về hậu quả?
4. Vì sao "lệnh bị từ chối" lại là bằng chứng có giá trị?
5. Đổi một setpoint và tải một khối logic mới — cái nào khó phát hiện hơn, vì
   sao?
