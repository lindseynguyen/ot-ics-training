# Lab 7 · Firmware và HMI 16-bit — tìm hằng số bị sửa

**Thời lượng:** 45 phút · **Hiện vật:** `lab7_rig_v1.gb`, `lab7_rig_v2.gb`,
`lab7_setpoint.com` · **Mức:** trung bình

## Bối cảnh

Hai thứ đến từ kho của bộ phận kỹ thuật:

1. Hai bản build của cùng một ảnh firmware mô phỏng trạm bơm (dùng định dạng
   cartridge Game Boy, vì nó gọn và chạy được trên mọi emulator). Kỹ sư nói
   "chỉ sửa nhãn hiển thị thôi".
2. Một tiện ích DOS 16 bit lấy từ máy trạm vận hành cũ, vẫn đang dùng để đặt
   setpoint qua cổng COM.

Cần xác minh câu "chỉ sửa nhãn", và xem tiện ích kia thực sự làm gì.

## Mục tiêu học

- Phương pháp đọc hiện vật nhị phân: **container → vùng → dữ liệu → mã lệnh**.
- Dùng `bin-diff` để so hai bản build và **hiểu** chỗ khác nhau.
- Tìm chuỗi có offset, kể cả chuỗi UTF-16 mà `strings` thường bỏ sót.
- Nhận ra hằng số IEEE-754 trông giống setpoint hoặc ngưỡng cắt.

## Kiến thức tối thiểu

**Ảnh cartridge** có header tại `0x0100`: tiêu đề, loại mapper, kích thước
ROM/RAM, hai checksum. ROM chia thành **bank 16 KiB**; địa chỉ trong mã lệnh
**không phải** offset trong file.

| Checksum sai | Ý nghĩa |
|---|---|
| header | ai đó sửa phần header |
| global (header đúng) | phần thân ảnh bị sửa sau khi build |

**File .COM** không có header: byte đầu tiên của file là lệnh đầu tiên, nạp
tại `CS:0100h`. Các lệnh ngắt đáng chú ý:

| INT | Dịch vụ |
|---|---|
| 21h | DOS: đọc/ghi file, ra màn hình |
| 10h | BIOS màn hình |
| 16h | BIOS bàn phím |
| **14h** | **BIOS cổng nối tiếp** — chương trình nói chuyện với thiết bị hiện trường |

Entropy: dưới 1.5 là vùng đệm; 4–5 là văn bản; khoảng 6 là mã lệnh; trên 7.2
là nén hoặc mã hoá.

## Các bước

### Bước 1 — Đây là cái gì (10')

```bash
python3 $TK/tools/file-inspect.py de/lab7_rig_v1.gb
python3 $TK/tools/file-inspect.py de/lab7_setpoint.com
```

Ghi lại hash — trong một vụ việc thật, đó là cách chứng minh về sau rằng bạn
đã phân tích đúng file này.

### Bước 2 — Bản đồ ROM (10')

```bash
python3 $TK/tools/gb-cart-inspect.py de/lab7_rig_v1.gb
python3 $TK/tools/gb-cart-inspect.py de/lab7_rig_v1.gb --blobs
```

Bank nào nhiều chuỗi (text giao diện), bank nào entropy cao (dữ liệu nén).

```bash
python3 $TK/tools/gb-cart-inspect.py de/lab7_rig_v1.gb --strings 1
```

### Bước 3 — So hai bản build (15')

```bash
python3 $TK/tools/bin-diff.py de/lab7_rig_v1.gb de/lab7_rig_v2.gb
```

Đọc cột *interpretation*. Công cụ nói thẳng vùng nào là chữ, vùng nào là số
thực, và giá trị trước/sau.

Nguyên tắc đọc:

- thay đổi trong vùng chữ → đổi nhãn hiển thị;
- thay đổi 4 byte trong vùng dữ liệu → **một hằng số**: setpoint, ngưỡng, thời
  gian trễ;
- thay đổi riêng vùng header → chỉ là build lại.

Muốn xem byte thật:

```bash
python3 $TK/tools/bin-diff.py de/lab7_rig_v1.gb de/lab7_rig_v2.gb --hexdump
```

### Bước 4 — Tiện ích HMI (10')

```bash
python3 $TK/tools/dos-bin-inspect.py de/lab7_setpoint.com
python3 $TK/tools/dos-bin-inspect.py de/lab7_setpoint.com --screens
python3 $TK/tools/dos-bin-inspect.py de/lab7_setpoint.com --floats
```

Chuỗi cho biết chương trình điều khiển quá trình nào và theo đơn vị gì. Bảng
ngắt cho biết nó có nói chuyện với thiết bị hiện trường hay không.

### Bước 5 — Nối với Lab 3 (5')

So các hằng số số thực trong `.COM` với giá trị cũ/mới mà bạn tìm được ở Lab 3.
Chúng có liên quan gì không?

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời | Offset |
|---|---|---|---|
| 7.1 | Tiêu đề cartridge và loại mapper | | |
| 7.2 | Bank nào chứa text, bank nào chứa dữ liệu nén | | |
| 7.3 | Tổng số vùng khác nhau giữa v1 và v2 | | |
| 7.4 | Nhãn chữ bị đổi (trước → sau) | | |
| 7.5 | Hằng số số thực bị đổi (trước → sau), tại offset nào | | |
| 7.6 | Hai checksum nói lên điều gì | | — |
| 7.7 | Các INT mà file .COM sử dụng, và ý nghĩa của INT 14h | | |
| 7.8 | Các hằng số trong .COM có khớp với Lab 3 không | | |

Câu suy luận:

> **7.9** Câu "chỉ sửa nhãn hiển thị thôi" đúng hay sai? Trả lời bằng bằng
> chứng, dạng một câu mà bạn sẽ gửi lại cho bộ phận kỹ thuật.

> **7.10** Vì sao một ngưỡng nằm **ngay trên** giá trị vận hành bình thường
> đáng ngờ hơn một ngưỡng nằm thấp hơn hẳn?

## Khi bí

<details>
<summary>Gợi ý 1 — bin-diff ra quá nhiều vùng</summary>

Mặc định đã gộp các đoạn gần nhau. Nếu vẫn nhiều, tăng `--merge-gap 32`.
</details>

<details>
<summary>Gợi ý 2 — không thấy chuỗi mong đợi</summary>

Thử `strings-plus.py` với `--min-len 4`, và nhớ rằng chuỗi có thể ở dạng
UTF-16. Công cụ quét cả hai.
</details>

<details>
<summary>Gợi ý 3 — muốn xem byte tại một offset cụ thể</summary>

```bash
python3 $TK/tools/hexview.py de/lab7_rig_v1.gb --at 0x5000 --length 64
python3 $TK/tools/hexview.py de/lab7_setpoint.com --find "SETPOINT"
```
</details>

## Ý nghĩa thực tế

Đây là bài gần nhất với công việc thẩm định thay đổi thật: **một bản firmware
mới, một câu giải thích, và việc của bạn là kiểm chứng câu giải thích đó**.

Ba việc làm được ngay ở đơn vị:

1. Lưu hash của mọi bản firmware đã được duyệt. Không có hash thì không so
   được.
2. Khi nhận bản mới, `bin-diff` với bản đang chạy trước khi nạp.
3. Yêu cầu bộ phận kỹ thuật ghi rõ *vùng nào thay đổi và vì sao* trong hồ sơ
   thay đổi, chứ không chỉ ghi "cập nhật".

Đọc thêm: [`docs/firmware-artifacts.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/firmware-artifacts.md),
[`docs/forensic-tools.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/forensic-tools.md).

Lời giải theo phương pháp: [`loi-giai/lab7-firmware.md`](loi-giai/lab7-firmware.md).
