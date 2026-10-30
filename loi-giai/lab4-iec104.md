# Lời giải Lab 4 — IEC-104 và DNP3

## Trình tự giải

```bash
python3 $TK/tools/iec104-triage.py de/lab4_iec104.pcap             # phiên + từ chối
python3 $TK/tools/iec104-triage.py de/lab4_iec104.pcap --commands  # chiều điều khiển
python3 $TK/tools/iec104-triage.py de/lab4_iec104.pcap --sbo       # kiểm tra trình tự
python3 $TK/tools/iec104-triage.py de/lab4_iec104.pcap --ioa       # bản đồ điểm
python3 $TK/tools/dnp3-triage.py   de/lab4_dnp3.pcap --controls
```

## 4.1 — Common address

Cột `CA` trong `--commands`, hoặc bảng *common addresses (stations)* trong báo
cáo mặc định.

## 4.2 / 4.3 / 4.4 — Trình tự select/execute

Cách đọc `--commands`: theo dõi từng IOA qua thời gian, nhìn cột `S/E`.

Với mã đề 101:

| IOA | Diễn biến | Kết luận |
|---|---|---|
| IOA bơm | SELECT → actcon → EXECUTE → actcon → actterm | **đúng chuẩn** |
| IOA van | chỉ có EXECUTE | **execute không select** |
| IOA van + 1 | chỉ có SELECT | **select không bao giờ execute** |

`--sbo` tự động hoá đúng việc này. Lưu ý với lớp: báo cáo SBO có thể liệt kê
thêm lệnh setpoint (type 50) vì nó cũng được execute thẳng — không phải lỗi
của công cụ, mà là đặc điểm của kịch bản.

Giải thích ý nghĩa:

- **Execute không select**: hoặc thiết bị cho phép lệnh trực tiếp (nhiều thiết
  bị cho phép), hoặc ai đó phát lại gói đã bắt được mà không hiểu bắt tay.
- **Select treo**: điểm bị giữ chỗ. Khi người vận hành thật muốn thao tác, họ
  có thể bị từ chối. Đây là một dạng từ chối dịch vụ rất khó nhận ra.

## 4.5 — Lệnh bị từ chối

Tìm cờ `NEG` trong `--commands`, hoặc bảng *negative confirmations*. Đó là
lệnh setpoint với giá trị cụ thể trong đề.

Giảng điểm: **bit P/N trong COT**. Thiết bị nói "tôi nhận được, và tôi không
làm". Trong một chuỗi điều khiển có interlock, các lệnh bị từ chối chính là
bản đồ cho biết bạn chưa thoả mãn điều kiện nào.

## 4.6 — STOPDT

Khung U cuối phiên. Nó dừng chiều giám sát **trong khi TCP vẫn mở**.

Câu 4.8 — so với rút cáp: rút cáp làm hệ thống báo *mất kết nối*, và đó là một
cảnh báo rõ ràng, có quy trình xử lý. `STOPDT` không tạo cảnh báo nào: phiên
TCP vẫn sống, thiết bị vẫn "online", chỉ là không có số liệu mới. Người trực
ca thấy màn hình đứng im — và màn hình đứng im trong vài phút là chuyện bình
thường.

## 4.7 — DNP3

`--controls` giải mã CROB: mã điều khiển (`LATCH_ON`...), chỉ số điểm, thời
gian xung. Sau đó là `disable-unsolicited` và `cold-restart`.

Chuỗi ba lệnh này là mẫu kinh điển: thao tác đầu ra → tắt báo cáo chủ động →
khởi động lại thiết bị. Mỗi lệnh một gói tin, không có payload nhiều giai đoạn
để chặn.

## Thời gian dự kiến

35–45 phút. Phần DNP3 có thể bỏ nếu thiếu giờ.
