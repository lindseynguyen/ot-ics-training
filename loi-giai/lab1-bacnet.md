# Lời giải Lab 1 — BACnet/IP

## Trình tự giải

```bash
python3 $TK/tools/pcap-overview.py de/lab1_bms.pcap     # 1. ai có mặt
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --devices   # 2. ai là thiết bị
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --dcc       # 3. mật khẩu
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --writes    # 4. thay đổi gì
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --timeline  # 5. dọn dấu vết
```

## 1.1 — Thiết bị lạ

`--devices` kết thúc bằng danh sách host *chỉ gửi yêu cầu, không trả lời, không
`i-Am`*. Đó là đáp án.

Lập luận cần nghe được từ học viên: thiết bị BACnet **phải** trả lời, vì mục
đích tồn tại của nó là phục vụ yêu cầu. Một host chỉ hỏi là phần mềm, không
phải bộ điều khiển.

*Sai thường gặp:* chọn host gửi nhiều gói nhất. Máy trạm vận hành hợp lệ cũng
gửi nhiều.

## 1.2 — Số lần thử DCC

Đếm **số dòng có service `deviceCommunicationControl`** trong `--dcc` hướng tới
Building Controller. Với mã đề 101 là **5** (4 dòng `password-failure` + 1 dòng
`ok`).

Bảng *attempts per pair* hiển thị **6** vì gộp cả `reinitializeDevice` ở cuối
phiên. Đây là bẫy có chủ đích; học viên phải đọc được rằng hai dịch vụ khác
nhau.

## 1.3 / 1.4 — Mật khẩu

Dòng duy nhất có `outcome = ok` chứa mật khẩu đúng. Các dòng
`security/password-failure` là mật khẩu sai.

Giải thích cho lớp: BACnet trả lời mật khẩu sai bằng Error PDU **class
`security` (4), code `password-failure` (26)**. Không có giới hạn số lần thử,
không có khoá tài khoản, không có độ trễ. Đó là lý do dò được trong vài trăm
mili giây.

## 1.5 — Thứ tự zone

Sắp theo frame tăng dần trong `--dcc` hoặc `--writes`. Với mã đề 101: ba IP
zone theo đúng thứ tự xuất hiện.

*Sai thường gặp:* liệt kê theo thứ tự IP tăng dần thay vì thứ tự thời gian.

## 1.6 — Object bị ghi

Cột `abbr` trong `--writes` cho dạng viết tắt kiểu Wireshark. Với mã đề 101,
zone đầu tiên: `BO:10` (khoá cửa), `BO:20` (chiếu sáng), `BI:30` (cảm biến).

Lưu ý kiểu object: **BO** = binary-output (rơ-le cửa, đầu ra chiếu sáng),
**BI** = binary-input (cảm biến). Học viên hay viết nhầm thành `AO`.

## 1.7 — out-of-service

Thuộc tính `out-of-service`, giá trị 1, **priority 8**.

Đây là điểm giảng quan trọng nhất của lab. So sánh hai cách:

| Cách | Người vận hành thấy gì |
|---|---|
| Ghi `present-value` | giá trị đổi, nhưng cảm biến vẫn gắn với thực tế; khi điều kiện thay đổi, giá trị sẽ tự đổi lại và lộ ra |
| Ghi `out-of-service` | object **tách khỏi thực tế**; màn hình giữ nguyên con số cũ mãi mãi, không có gì mâu thuẫn để phát hiện |

Trả lời đúng cho câu 1.9 phải nêu được ý: cách thứ hai bền vững hơn và không
tạo ra tín hiệu mâu thuẫn.

## 1.8 — Dịch vụ cuối cùng

`reinitializeDevice` với tham số `warmstart`. Nó khởi động lại bộ điều khiển —
xuất hiện ở cuối dòng thời gian thì gần như luôn là bước dọn dẹp: xoá trạng
thái tạm, làm mọi thứ trông như một lần khởi động lại bình thường.

## Bảng tóm tắt cho phần chữa bài

| Hành động | Giai đoạn ATT&CK for ICS |
|---|---|
| `who-Is` quét toàn mạng | Remote System Discovery (T0846) |
| Dò mật khẩu DCC | Default/weak credentials (T0812) |
| DCC `disable` | Denial of Service (T0814) |
| Ghi `out-of-service` | Spoof Reporting Message (T0856) |
| Mở khoá cửa | Unauthorized Command Message (T0855) |
| `reinitializeDevice` | Change Operating Mode (T0858) |

## Thời gian dự kiến

Học viên trung bình: 45–55 phút. Nếu quá 60 phút, thường là do chưa chạy
`--devices` mà cố đọc timeline thủ công.
