# Lời giải Lab 3 — S7comm

## Trình tự giải

```bash
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap            # vai trò các host
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --szl      # fingerprint
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --blocks   # logic bị tải vào
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --writes   # giá trị bị ghi
python3 $TK/tools/s7-triage.py de/lab3_s7.pcap --control  # CPU STOP
```

## 3.1 — Máy tấn công

Bảng *endpoints*: host có nhiều `requests`, ít `responses` là phía client. Với
mã đề 101 có hai client-ish: PLC cũng xuất hiện vì nó trả lời userdata. Hướng
dẫn học viên nhìn cột `likely role` và bảng cặp (client, plc) phía dưới.

## 3.2 / 3.3 — SZL

`--szl` in sẵn mục *distinct SZL ids per source (ascending)*. Chép nguyên dạng
`0xNNNN`.

Ý nghĩa cần nói được:

| SZL-ID | Kẻ tấn công biết được gì |
|---|---|
| `0x0011` | mã đặt hàng, loại CPU, firmware → tra được lỗ hổng đã biết |
| `0x001C` | tên nhà máy, tên module, số sê-ri → xác nhận đúng mục tiêu |
| `0x0232` | mức bảo vệ và trạng thái mật khẩu → biết có cần mật khẩu không |
| `0x00A0` | bộ đệm chẩn đoán → đọc nhật ký của chính PLC |
| `0x0424` | nguyên nhân lần dừng gần nhất → biết vì sao lệnh của mình bị từ chối |

Câu 3.9: kẻ tấn công đọc `0x00A0` để xem PLC ghi lại gì — vừa để biết mình có
bị ghi nhận không, vừa để hiểu lý do lệnh bị từ chối.

## 3.4 — Khối logic

`--blocks` in dòng `distinct blocks pushed to the PLC`.

Nhấn mạnh với lớp hai điều:

1. **Download = đẩy vào PLC.** Đây là chỗ học viên sai nhiều nhất.
2. Nếu trong danh sách có **OB1** thì chương trình chạy mỗi vòng quét đã bị
   thay. Đó là mức nghiêm trọng cao nhất trong một capture S7.

Giải mã tên file: `_0800001P` = `08` (OB) + `00001` (số 1) + `P` (hệ thống
file passive).

## 3.5 / 3.6 — Tag và giá trị

`--writes` cho cả lệnh đọc trước đó và lệnh ghi, nên học viên lấy được **cả
giá trị cũ và mới**. Bảng *written values* chốt lại giá trị mới.

Giá trị là IEEE-754 **big-endian** — ngược với IEC-104 ở Lab 4. Nếu lớp có
người tự giải mã bằng Python, nhắc `struct.unpack('>f', ...)`.

## 3.7 — CPU STOP, câu quan trọng nhất

`--control` cho thấy lệnh gửi tới **hai** PLC, mỗi lệnh đều có bản tin trả về
`ack-data` mang `class 0x81 code 0x04`.

**Kết luận đúng:** lệnh đã được gửi nhưng **PLC từ chối**, nên nhà máy không
mất bộ điều khiển.

Nếu học viên viết "kẻ tấn công đã dừng được PLC" thì dừng cả lớp lại và chữa
ngay — đây là điểm phân loại của khoá. Cách kiểm tra nhanh: hỏi "bạn nhìn vào
cột nào để kết luận?"

Các lý do PLC từ chối, để giải thích cho lớp:

- keyswitch không ở vị trí cho phép đặt từ xa;
- protection level yêu cầu mật khẩu;
- khối có know-how protection;
- CPU an toàn chỉ cho dừng theo trình tự.

## 3.8 — Câu suy luận

Trả lời đạt phải so sánh theo **khả năng phát hiện**, không chỉ theo hậu quả:

- Đổi liều clo: hậu quả tức thì, nhưng **nhìn thấy được** trên xu hướng dữ
  liệu và trên chất lượng nước đầu ra.
- Tải đè OB1: có thể không gây hậu quả gì trong nhiều ngày, rồi kích hoạt theo
  điều kiện. Không có dấu hiệu nào trên màn hình vận hành. Chỉ phát hiện được
  khi so sánh logic đang chạy với bản đã duyệt — việc mà hầu hết đơn vị không
  làm định kỳ.

Vậy: nguy hiểm hơn là tải đè OB1.

## Thời gian dự kiến

45–60 phút. Phần `--control` nên để dành 15 phút cuối và chữa chung cả lớp.
