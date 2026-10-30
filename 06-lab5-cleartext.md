# Lab 5 · Thông tin đăng nhập dạng rõ trong vùng DMZ

**Thời lượng:** 30 phút · **Hiện vật:** `lab5_dmz.pcap` · **Mức:** cơ bản

## Bối cảnh

Kẻ tấn công đã vào được jump host trong vùng OT-DMZ. Trong thời gian đó, một
bản bắt gói ghi lại lưu lượng giữa jump host và các dịch vụ phía trong. Mọi
truy vấn, mọi thông tin đăng nhập đều đi dạng rõ.

## Mục tiêu học

- Thấy tận mắt rằng **không cần bẻ khoá gì cả** — giao thức tự gửi đi.
- Hiểu "mã hoá" của trường mật khẩu TDS (MS SQL Server) thực chất là gì.
- Nhận ra giá trị trinh sát của chính câu truy vấn SQL.

## Kiến thức tối thiểu

| Giao thức | Vấn đề |
|---|---|
| FTP (21) | `USER` và `PASS` đi dạng rõ, từng dòng một |
| Telnet (23) | toàn bộ phiên dạng rõ, kể cả lúc gõ mật khẩu |
| SNMP v1/v2c (161) | *community string* là mật khẩu, gửi trong **mỗi** gói |
| HTTP (80) | Basic auth chỉ là base64 — mã hoá ký tự, không phải bảo mật |
| **MS SQL Server / TDS (1433)** | gói LOGIN7 mang mật khẩu **xáo trộn**, không mã hoá |

Trường mật khẩu TDS: mỗi byte **đảo hai nửa nibble rồi XOR với 0xA5**. Đó là
che giấu, không phải mã hoá — biết công thức là đọc ngược ra ngay.

## Các bước

### Bước 1 — Thu hoạch (10')

```bash
python3 $TK/tools/cleartext-creds.py de/lab5_dmz.pcap
```

Mỗi dòng là một phát hiện kèm frame number.

### Bước 2 — Hiểu phần TDS (10')

Dòng `login7` chứa hostname, username, **password đã giải mã**, tên ứng dụng,
tên server và tên database.

Thử tự giải mã một chuỗi để hiểu cơ chế:

```bash
python3 $TK/tools/cleartext-creds.py --tds-decode <chuỗi hex>
```

### Bước 3 — Đọc câu truy vấn (5')

Dòng `query` chứa câu SQL. Tên bảng và tên cột cho biết **cách đặt tên tag**
và **các khu vực của nhà máy** — bản thân nó đã là trinh sát.

### Bước 4 — Xem luồng đầy đủ (5')

```bash
python3 $TK/tools/stream-carve.py de/lab5_dmz.pcap
python3 $TK/tools/stream-carve.py de/lab5_dmz.pcap --stream 0 --ascii
```

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời | Frame |
|---|---|---|---|
| 5.1 | Tài khoản dùng để đăng nhập SQL Server | | |
| 5.2 | Mật khẩu SQL Server | | |
| 5.3 | Cơ chế che giấu mật khẩu TDS (mô tả bằng một câu) | | — |
| 5.4 | Mật khẩu FTP | | |
| 5.5 | SNMP community string | | |
| 5.6 | Tên database và tên bảng bị truy vấn | | |

Câu suy luận:

> **5.7** Historian thường là bước nhảy tiếp theo của kẻ tấn công sau khi vào
> được DMZ. Nêu hai lý do.

> **5.8** SNMP community string đọc được có thể dùng làm gì? Phân biệt cộng
> đồng chỉ đọc và cộng đồng ghi.

## Ý nghĩa thực tế

Các bản bắt gói trong khoá này chứa thông tin đăng nhập dạng rõ vì **môi
trường thật cũng vậy**. Việc cần làm, theo thứ tự dễ đến khó:

1. Bỏ community string mặc định; chuyển SNMPv3 hoặc tắt hẳn quyền ghi SNMP.
2. Khai tử FTP và Telnet trên thiết bị hiện trường nếu firmware cho phép.
3. Bật TLS cho listener SQL của historian.
4. Chấm dứt việc dùng tài khoản dịch vụ dùng chung có quyền cao, truy cập được
   từ OT-DMZ.

Đọc thêm: [`docs/defense-notes.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/defense-notes.md).

Lời giải theo phương pháp: [`loi-giai/lab5-cleartext.md`](loi-giai/lab5-cleartext.md).
