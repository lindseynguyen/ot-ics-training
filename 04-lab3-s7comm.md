# Lab 3 · S7comm — PLC Siemens bị dò và bị sửa logic

**Thời lượng:** 60 phút · **Hiện vật:** `lab3_s7.pcap` · **Mức:** trung bình

> Từ lab này trở đi, **làm bằng dòng lệnh**. Giao diện vẫn chạy được, nhưng
> bài làm phải có câu lệnh, vì đó là thứ dán được vào báo cáo sự cố.

## Bối cảnh

Khu xử lý của nhà máy chạy PLC Siemens S7. Lúc 10:47 một ngày thứ Ba, hai PLC
báo từ chối lệnh CPU STOP đến từ một nguồn không xác định. IDS tự động chặn
host đó ở biên VLAN OT.

Câu hỏi của ban lãnh đạo không phải "ai chặn được" mà là: **chúng đã làm được
gì trước khi bị chặn?**

## Mục tiêu học

- Nhận ra hoạt động *fingerprint* PLC và hiểu vì sao nó không cần mật khẩu.
- Hiểu "download" trong thuật ngữ Siemens nghĩa là **đẩy logic vào PLC**.
- Đọc giá trị IEEE-754 big-endian ghi vào tag.
- Quan trọng nhất: **phân biệt lệnh đã thử và lệnh đã thành công**.

## Kiến thức tối thiểu

S7comm chạy trên **TCP 102** (ISO-on-TCP). Các lớp: TPKT → COTP → S7 header →
tham số.

Mã hàm cần nhớ:

| Mã | Tên | Ý nghĩa |
|---|---|---|
| 0x04 / 0x05 | read-var / **write-var** | đọc / **ghi** giá trị tag |
| 0x1A / 0x1B | request-download / download-block | **đẩy code vào PLC** |
| 0x1D / 0x1E | start-upload / upload | kéo code ra khỏi PLC |
| 0x28 | PI-service | khởi động lại chương trình |
| 0x29 | **plc-stop** | **dừng vòng quét của CPU** |

**Chiều của từ "download" ngược với cảm giác thông thường:** download = từ máy
kỹ thuật **xuống** PLC. Đó mới là sự kiện làm đổi hành vi nhà máy.

**SZL** (System Status List) là dữ liệu chẩn đoán có sẵn trong PLC, đọc được
**không cần mật khẩu**:

| SZL-ID | Nội dung |
|---|---|
| `0x0011` | mã đặt hàng (6ES7...), loại CPU, firmware |
| `0x001C` | tên nhà máy, tên module, số sê-ri |
| `0x00A0` | **bộ đệm chẩn đoán** — nhật ký của chính PLC |
| `0x0232` | mức bảo vệ / trạng thái mật khẩu |
| `0x0424` | nguyên nhân lần dừng gần nhất |

Địa chỉ tag: `DB7.DBX10.0` nghĩa là Data Block 7, byte 10, bit 0. Transport
size `real` là **4 byte IEEE-754 big-endian**.

## Các bước

### Bước 1 — Ai nói với ai (5')

```bash
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap
```

Bảng *endpoints* đoán vai trò: host gửi nhiều yêu cầu là máy kỹ thuật (hoặc
công cụ), host trả lời là PLC.

### Bước 2 — Fingerprint (10')

```bash
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --szl
```

Liệt kê các SZL-ID, **sắp xếp tăng dần** như yêu cầu của câu hỏi. Mỗi ID tra
theo bảng trên để nói được kẻ tấn công đang tìm hiểu cái gì.

### Bước 3 — Logic bị thay đổi (15')

```bash
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --blocks
```

Tên file khối có dạng `_` + 2 chữ số loại + 5 chữ số số hiệu + 1 ký tự hệ
thống file:

| Mã | Loại khối |
|---|---|
| 08 | OB — organisation block, trong đó OB1 là chương trình chạy mỗi vòng quét |
| 0A | DB — data block |
| 0C | FC — function |
| 0E | FB — function block |

`_0800001P` = OB1. Nếu OB1 bị ghi đè thì **chương trình chạy mỗi vòng quét đã
bị thay**.

### Bước 4 — Giá trị bị ghi (15')

```bash
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --writes
```

Có một lệnh đọc rồi một lệnh ghi lên cùng một tag. Ghi lại cả hai giá trị: cũ
và mới. Giá trị trong đề của bạn là liều châm clo, tính bằng mg/L.

### Bước 5 — CPU STOP (15')

```bash
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --control
```

Đây là câu hỏi quan trọng nhất của lab. Lệnh STOP được gửi tới **hai** PLC.
Nhìn cột `error`: `class 0x81 code 0x04` nghĩa là **CPU đã từ chối**.

Lý do thường gặp khi CPU từ chối:

- công tắc chế độ (keyswitch) không ở vị trí cho phép đặt từ xa;
- mức bảo vệ (protection level) yêu cầu mật khẩu;
- khối có know-how protection;
- CPU an toàn (F-CPU) chỉ cho dừng theo trình tự có kiểm soát.

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời | Frame |
|---|---|---|---|
| 3.1 | IP máy tấn công | | |
| 3.2 | Các SZL-ID đã đọc, **tăng dần**, dạng `0xNNNN` | | |
| 3.3 | Mỗi SZL-ID đó cho kẻ tấn công biết điều gì | | — |
| 3.4 | Các khối logic bị tải **vào** PLC (dạng OB1, DB5...) | | |
| 3.5 | Tag bị ghi (dạng `DBn.DBXb.x`) | | |
| 3.6 | Giá trị cũ → giá trị mới (mg/L) | | |
| 3.7 | Lệnh CPU STOP gửi tới mấy PLC, **có thành công không**, vì sao biết | | |

Câu suy luận:

> **3.8** Trong hai việc sau, việc nào nguy hiểm hơn với nhà máy: tải đè OB1,
> hay đổi giá trị liều clo? Lập luận theo hướng *phát hiện được hay không* chứ
> không chỉ theo hậu quả tức thời.

> **3.9** Kẻ tấn công đọc SZL `0x00A0` (bộ đệm chẩn đoán). Chúng tìm gì trong
> đó?

## Khi bí

<details>
<summary>Gợi ý 1 — không thấy khối nào</summary>

Dùng `--blocks`. Nếu trống, kiểm tra lại đường dẫn file; capture của lab 3 là
`lab3_s7.pcap`, không phải lab 1.
</details>

<details>
<summary>Gợi ý 2 — giá trị float ra số vô lý</summary>

S7 dùng **big-endian**. Công cụ đã giải mã sẵn ở cột `value`; nếu bạn tự tính
bằng tay thì nhớ không đảo byte.
</details>

<details>
<summary>Gợi ý 3 — câu 3.7, không biết "thành công" hay không</summary>

Cột `error` trong `--control`. Bản tin trả về là `ack-data`; nếu error class
khác 0 thì CPU đã từ chối. Lệnh *đã được gửi* nhưng *không có hiệu lực*.
</details>

## Ý nghĩa thực tế

Lab này cho thấy ba mức hậu quả khác nhau trong cùng một phiên:

1. **Đọc SZL** — không thay đổi gì, nhưng là bước chuẩn bị, và không cần mật
   khẩu.
2. **Ghi tag** — đổi liều hoá chất; *thành công*; hậu quả vật lý ngay.
3. **CPU STOP** — bị từ chối; không gây hậu quả, nhưng cho thấy **ý định**.

Trong báo cáo, ba mức này phải được viết khác nhau. Gộp chung thành "PLC bị
tấn công" là mất thông tin.

Biện pháp:

- Truy cập kỹ thuật qua jump host; chỉ cho phép TCP/102 từ đó.
- Protection level 3 + know-how protection; keyswitch không để RUN-P khi vận
  hành.
- Cảnh báo với mọi `request-download`, `plc-stop`, `PI-service` nằm ngoài cửa
  sổ thay đổi đã lên kế hoạch.
- Ghi log các lần đọc SZL: một loạt `0x0011`/`0x001C` từ host lạ là trinh sát.

Đọc thêm: [`docs/s7comm.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/s7comm.md).

Lời giải theo phương pháp: [`loi-giai/lab3-s7comm.md`](loi-giai/lab3-s7comm.md).
