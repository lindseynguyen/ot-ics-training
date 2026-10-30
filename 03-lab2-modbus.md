# Lab 2 · Modbus/TCP — quét, tắt báo động, sửa setpoint

**Thời lượng:** 60 phút · **Hiện vật:** `lab2_modbus.pcap` · **Mức:** cơ bản

## Bối cảnh

Khu bơm của nhà máy dùng một PLC nhỏ nói Modbus/TCP với HMI. Sau sự việc ở Lab
1, SOC bật thêm cổng giám sát ở phân đoạn này và bắt được 30 giây lưu lượng.

Trong đó có cả hoạt động bình thường lẫn hoạt động không bình thường. Tách hai
thứ đó ra.

## Mục tiêu học

- Nhận ra dấu vết quét trong một giao thức không có dịch vụ danh bạ.
- Phân biệt mã hàm đọc và mã hàm ghi, và hậu quả vật lý của từng loại.
- Ghép hai thanh ghi 16-bit thành một số thực, và chọn đúng thứ tự từ.
- Nhớ bẫy đánh địa chỉ 0-based / 1-based.

## Kiến thức tối thiểu

Khung Modbus/TCP: 7 byte MBAP (transaction id, protocol id, length, **unit
id**) rồi tới PDU bắt đầu bằng **function code**.

| Mã | Tên | Hậu quả |
|---|---|---|
| 1, 2 | đọc coil / đầu vào rời rạc | giám sát |
| 3, 4 | đọc thanh ghi | giám sát |
| **5** | ghi một coil | **bật/tắt một đầu ra**: khởi động bơm, tắt còi |
| **6** | ghi một thanh ghi | **đổi một giá trị 16-bit** |
| **15, 16** | ghi nhiều coil / thanh ghi | **cách thường dùng để đặt số thực** |

Lỗi trả về là mã hàm **OR 0x80** kèm exception code: 2 = địa chỉ không hợp lệ,
11 = gateway không nhận được trả lời từ thiết bị phía sau.

Hai cái bẫy:

1. **Địa chỉ trên dây là 0-based**, tài liệu vận hành thường 1-based. Địa chỉ
   0 trên dây chính là thanh ghi 40001.
2. **Giá trị 32-bit chiếm hai thanh ghi**, và hãng nào theo thứ tự từ của hãng
   đó: `ABCD` (big-endian) và `CDAB` (hoán vị từ) đều phổ biến.

## Các bước

### Bước 1 — Toàn cảnh (10')

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap
```

Ba bảng đầu: ai nói với ai và unit id nào; mã hàm nào xuất hiện; exception nào
trả về. Bảng *scan / enumeration heuristics* chỉ thẳng host khả nghi.

### Bước 2 — Vì sao quét lại lộ (10')

Modbus không có cách nào để hỏi "thiết bị nào đang tồn tại". Cách duy nhất để
biết là **hỏi tất cả rồi giữ lại cái nào trả lời** — và chính điều đó để lại
một vệt exception rất dễ thấy.

Đếm xem bao nhiêu unit id đã bị thử, và bao nhiêu trong số đó thực sự trả lời.

### Bước 3 — Bản đồ thanh ghi (10')

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --map
```

Bảng dưới liệt kê các khối đã được yêu cầu (địa chỉ bắt đầu + số lượng). Đây
chính là bản đồ mà kẻ tấn công đã dựng.

### Bước 4 — Cái gì bị ghi (15')

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --writes
```

Hai thao tác ghi. Một là function 5 lên một coil; một là function 16 lên hai
thanh ghi liền nhau. Hai thanh ghi liền nhau gần như luôn là **một số thực**.

### Bước 5 — Đọc ra số thực (10')

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --floats
```

Công cụ in cả hai thứ tự từ. Giữ lại cột cho ra giá trị **hợp lý về mặt công
nghệ**: mức bể tính theo %, lưu lượng theo gpm, áp suất theo psi. Giá trị kiểu
`1.4e-42` là chọn sai thứ tự.

### Bước 6 — Chữ giấu trong thanh ghi (5')

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --strings
```

Văn bản được nhét hai ký tự mỗi thanh ghi. Tên thiết bị, tên tag đi đường này
— và đôi khi cả thứ người ta cố tình để lại.

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời | Frame |
|---|---|---|---|
| 2.1 | IP thực hiện quét | | |
| 2.2 | Bao nhiêu unit id bị thử, bao nhiêu unit trả lời | | |
| 2.3 | Exception code mà các unit không tồn tại trả về | | |
| 2.4 | Số hiệu coil bị ép về 0, và mã hàm dùng | | |
| 2.5 | Dải thanh ghi bị ghi (dạng `4x40-41`) | | |
| 2.6 | Giá trị số thực được ghi, và thứ tự từ đúng | | |
| 2.7 | Chuỗi ASCII giấu trong input register | | |

Câu suy luận:

> **2.8** Coil bị ép về 0 trong kịch bản này là một còi báo động. Vì sao kẻ
> tấn công làm việc đó **trước** khi đổi setpoint, chứ không phải sau?

> **2.9** Nếu địa chỉ trên dây là 40 thì trong tài liệu vận hành của nhà máy
> nó được ghi là thanh ghi số mấy?

## Khi bí

<details>
<summary>Gợi ý 1 — phân biệt đọc và ghi</summary>

Nhìn cột `function`. Tên có chữ `read` là đọc, có chữ `write` là ghi. Chỉ hai
dòng là ghi.
</details>

<details>
<summary>Gợi ý 2 — số thực ra giá trị vô lý</summary>

Bạn đang đọc nhầm cột. Bảng `--floats` in hai cột: `big-endian (ABCD)` và
`word-swapped (CDAB)`. Chọn cột cho ra số nằm trong khoảng hợp lý của một
setpoint.
</details>

<details>
<summary>Gợi ý 3 — không thấy chuỗi ASCII</summary>

Chuỗi nằm trong phần dữ liệu trả về của một lệnh đọc input register (function
4), không phải trong lệnh ghi. Dùng `--strings`.
</details>

## Ý nghĩa thực tế

Modbus không có xác thực. Thực tế nghĩa là: **mọi cổng TCP/502 mà bạn định
tuyến tới được đều là ghi được**, với bất kỳ ai định tuyến tới được.

Biện pháp:

- Phân đoạn mạng; historian chỉ đọc, và không bao giờ chủ động mở kết nối vào
  vùng điều khiển.
- Firewall hiểu giao thức, chỉ cho qua những mã hàm thực sự cần (chỉ đọc với
  máy thu thập dữ liệu).
- Cảnh báo với **bất kỳ mã hàm ghi nào** phát ra từ host vốn chỉ đọc, và với
  ghi vào coil báo động hay thanh ghi ngưỡng.

Đọc thêm: [`docs/modbus-tcp.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/modbus-tcp.md).

Lời giải theo phương pháp: [`loi-giai/lab2-modbus.md`](loi-giai/lab2-modbus.md).
