# Lời giải Lab 7 — firmware và HMI 16-bit

## Trình tự giải

```bash
python3 $TK/tools/file-inspect.py de/lab7_rig_v1.gb
python3 $TK/tools/gb-cart-inspect.py de/lab7_rig_v1.gb
python3 $TK/tools/gb-cart-inspect.py de/lab7_rig_v1.gb --strings 1
python3 $TK/tools/bin-diff.py de/lab7_rig_v1.gb de/lab7_rig_v2.gb
python3 $TK/tools/dos-bin-inspect.py de/lab7_setpoint.com
```

## 7.1 / 7.2 — Header và bank

`gb-cart-inspect.py` in tiêu đề, loại mapper (MBC3+RAM+BATTERY), kích thước
ROM, và bảng *bank profile*.

Cách đọc bảng bank:

| Entropy | Strings | Nội dung |
|---|---|---|
| thấp | nhiều | text giao diện, thông báo báo động |
| thấp | ít | bảng tra, đồ hoạ, vùng đệm |
| > 7.2 | ít | **dữ liệu nén hoặc mã hoá** |

Với mã đề 101: bank 1 chứa text, bank 2 chứa một stream zlib tại `0x8000`,
bank 3 có entropy cao.

## 7.3 → 7.5 — So hai bản build

`bin-diff.py` cho ba vùng khác nhau. Điều quan trọng là **cột
interpretation**, không phải số lượng vùng:

| Offset | Diễn giải | Nghĩa là |
|---|---|---|
| ~`0x14e` | 1–2 byte trong vùng header | checksum được tính lại → ảnh được build lại |
| `0x4000`+ | `text: 'PUMP X' -> 'PUMP X MOD'` | đổi nhãn hiển thị, đúng như kỹ sư nói |
| `0x5000` | `float 1.75 -> 8` | **một hằng số bị đổi** — không nằm trong lời khai |

Nếu công cụ báo vùng 2 byte nằm trong một giá trị 4 byte, nó sẽ tự mở rộng cửa
sổ ra ranh giới 4 byte và diễn giải thành số thực. Đây là điểm đáng chỉ cho
lớp: một số thực hiếm khi đổi cả bốn byte.

## 7.6 — Hai checksum

- **Header checksum sai** → có người sửa phần header.
- **Global checksum sai mà header đúng** → phần thân bị sửa sau khi build.
- **Cả hai đúng** (trường hợp của lab) → ảnh được **build lại hợp lệ**, tức là
  thay đổi đi qua công cụ phát triển, không phải vá byte thủ công.

## 7.7 — File .COM

`dos-bin-inspect.py` liệt kê các INT. Điểm cần rút ra:

- INT 21h: dịch vụ DOS (in chuỗi, đọc phím);
- INT 10h: vẽ màn hình;
- **INT 14h: cổng nối tiếp** → chương trình **nói chuyện trực tiếp với thiết
  bị hiện trường**, tức là nó cài đặt một giao thức trường (Modbus RTU, DF1
  hoặc giao thức ASCII riêng của hãng). Đó mới là nửa đáng quan tâm của
  chương trình.

## 7.8 — Nối với Lab 3

Các hằng số số thực trong `.COM` trùng với giá trị **cũ và mới** của tag clo
trong Lab 3. Ý nghĩa: tiện ích đặt setpoint này chính là đường mà giá trị kia
được nhập vào, hoặc ít nhất là nó biết cả hai giá trị.

Đây là câu "nối các lab lại với nhau" — không phải học viên nào cũng thấy, và
đáng cộng điểm cho người thấy.

## 7.9 — Câu trả lời gửi bộ phận kỹ thuật

Mẫu đạt yêu cầu:

> Bản v2 không chỉ đổi nhãn. Ngoài chuỗi tại `0x4000` (`PUMP P-1xx` →
> `PUMP P-1xx MOD`), hằng số số thực tại `0x5000` thay đổi từ 1.75 sang 8.0.
> Vị trí này nằm trong vùng hằng số vận hành của ảnh, nên đề nghị bộ phận kỹ
> thuật xác nhận giá trị đó là tham số gì và vì sao được thay đổi, trước khi
> bản v2 được nạp.

Chấm theo: có nêu offset, có nêu giá trị trước/sau, có yêu cầu xác nhận thay
vì kết luận thay họ.

## 7.10 — Ngưỡng nằm ngay trên giá trị vận hành

Một ngưỡng thấp hơn hẳn sẽ báo động liên tục và bị phát hiện trong vài phút.
Một ngưỡng nằm **ngay trên** dải vận hành bình thường thì im lặng trong điều
kiện thường, và chỉ bộc lộ khi quá trình đi lệch — đúng lúc mà bảo vệ lẽ ra
phải hoạt động. Đó là hình dạng của một ngưỡng bị chỉnh có chủ đích.

## Thời gian dự kiến

35–45 phút. Nếu lớp chậm, bỏ phần `.COM` và giữ phần `bin-diff`.
