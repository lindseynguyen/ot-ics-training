# Lời giải Lab 2 — Modbus/TCP

## Trình tự giải

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap            # tổng quan
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --map      # bản đồ địa chỉ
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --writes   # thao tác ghi
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --floats   # số thực
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --strings  # chữ trong thanh ghi
```

## 2.1 / 2.2 — Quét

Bảng *scan / enumeration heuristics* chỉ thẳng host. Số unit id đã thử = số
dòng yêu cầu khác nhau theo `unit` trong bảng *endpoints and unit ids*.

Với mã đề 101: 9 unit id bị thử, chỉ unit 1 và 2 trả lời.

Giảng điểm: Modbus **không có dịch vụ danh bạ**. Không có cách nào hỏi "có
thiết bị nào ở đây". Nên cách duy nhất để biết là hỏi tất cả — và chính điều
đó tạo ra vệt exception rất dễ nhận.

## 2.3 — Exception code

Code **11** = `gateway-target-no-response`: gateway không nhận được trả lời từ
thiết bị serial phía sau unit id đó. (Code 2 = địa chỉ không hợp lệ, cũng hay
gặp trong quét.)

## 2.4 / 2.5 — Thao tác ghi

Chỉ có hai dòng trong `--writes`:

- **function 5** (write single coil) lên một coil → giá trị 0.
- **function 16** (write multiple registers) lên **hai** thanh ghi liền nhau.

Hai thanh ghi liền nhau gần như luôn là một giá trị 32-bit.

## 2.6 — Số thực

`--floats` in hai cột. Với mã đề 101, cặp `17019, 0`:

| Thứ tự | Giá trị |
|---|---|
| big-endian ABCD | **62.75** |
| word-swapped CDAB | một số vô lý |

Chọn cột cho ra giá trị nằm trong khoảng vận hành hợp lý.

*Sai thường gặp:* lấy cột đầu vì nó ở bên trái. Hỏi lại: "62.75 phần trăm mức
bể thì hợp lý; `2.1e+17` thì là cái gì?"

## 2.7 — Chuỗi ASCII

`--strings` giải mã phần dữ liệu trả về của lệnh đọc input register. Hai ký tự
mỗi thanh ghi.

## 2.8 — Vì sao tắt báo động trước

Trả lời đạt phải nêu được: nếu đổi setpoint trước, báo động sẽ kêu ngay lúc
giá trị vượt ngưỡng và người trực ca sẽ nhìn vào đúng chỗ. Tắt trước thì thay
đổi diễn ra trong im lặng.

Đây chính là mẫu **inhibit → impair** xuất hiện ở mọi kịch bản trong khoá.

## 2.9 — Địa chỉ 0-based

Địa chỉ 40 trên dây = thanh ghi **40041** trong tài liệu vận hành (4x, 1-based).

Nói rõ với lớp: đây là nguồn gốc của phần lớn các cuộc tranh luận "lệch một
đơn vị" khi đối chiếu với danh sách tag của nhà máy.

## Mở rộng cho người xong sớm

```bash
python3 $TK/tools/modbus-triage.py de/lab2_modbus.pcap --timeline
```

Hỏi: nhìn vào cặp request/response, bạn có phân biệt được lưu lượng hỏi vòng
hợp lệ của HMI với lưu lượng của công cụ không? Dựa vào cái gì — tần suất, số
lượng unit, hay cả hai?

## Thời gian dự kiến

35–45 phút.
