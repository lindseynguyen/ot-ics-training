# Lời giải Lab 5 — thông tin đăng nhập dạng rõ

## Trình tự giải

```bash
python3 $TK/tools/cleartext-creds.py de/lab5_dmz.pcap
python3 $TK/tools/stream-carve.py de/lab5_dmz.pcap
python3 $TK/tools/stream-carve.py de/lab5_dmz.pcap --stream 0 --ascii
```

## 5.1 / 5.2 — Tài khoản và mật khẩu SQL

Dòng `tds / login7` chứa toàn bộ: hostname, username, password (đã giải mã),
appname, servername, database.

## 5.3 — Cơ chế che giấu TDS

Mỗi byte của mật khẩu (dạng UTF-16LE) bị **đảo hai nửa nibble rồi XOR với
0xA5**. Không có khoá, không có muối, không phụ thuộc phiên.

Minh hoạ cho lớp bằng một dòng Python:

```python
b = 0x41                      # ký tự 'A'
b = ((b & 0x0F) << 4) | (b >> 4)
print(hex(b ^ 0xA5))
```

Nhấn mạnh: đây là **che giấu**, không phải mã hoá. Bất kỳ ai bắt được gói đều
đọc được. Nếu trong đơn vị còn listener SQL không bật TLS thì mọi lần đăng
nhập đều đang để lộ mật khẩu.

## 5.4 / 5.5 — FTP và SNMP

FTP gửi `USER` rồi `PASS` thành hai dòng riêng, dạng rõ hoàn toàn.

SNMP community string nằm trong **mỗi** gói tin. Phân biệt:

- community chỉ đọc: lộ thông tin cấu hình, danh sách interface, phiên bản
  firmware;
- community ghi: **thay đổi được cấu hình thiết bị** — tắt cổng, đổi tham số.

## 5.6 — Database và bảng

Trong dòng `tds / query`. Tên bảng và tên cột cho biết cách đặt tên tag và
các khu vực nhà máy.

## 5.7 — Vì sao historian là bước nhảy tiếp theo

Hai lý do cần có trong câu trả lời đạt:

1. **Nó nằm ở cả hai vùng.** Historian phải đọc được dữ liệu từ vùng điều
   khiển và phải cho vùng văn phòng truy vấn — nên nó là một trong số ít máy
   chủ hợp lệ bắc cầu hai bên.
2. **Nó chứa bản đồ.** Tên tag, đơn vị, khu vực, ngưỡng — toàn bộ thông tin
   cần để biết ghi vào đâu cho có hậu quả. Không có nó, kẻ tấn công phải quét
   mò.

Thêm một lý do hay gặp trong thực tế: tài khoản của historian thường dùng
chung, quyền cao, và mật khẩu ít khi đổi vì sợ gãy tích hợp.

## Thời gian dự kiến

20–30 phút. Đây là lab ngắn, dùng để nghỉ giữa hai lab nặng.
