# Lab 1 · BACnet/IP — hệ thống quản lý toà nhà bị chiếm

**Thời lượng:** 75 phút · **Hiện vật:** `lab1_bms.pcap` · **Mức:** cơ bản

## Bối cảnh

Nhà máy trong đề của bạn dùng một hệ BMS trên BACnet/IP để quản lý cửa ra vào,
chiếu sáng và cảm biến hiện diện cho sáu khu vực. Đêm hôm trước chỉ có kíp trực
tối thiểu. 07:14 sáng hôm sau, ca ngày phát hiện màn hình BMS không phản hồi:
thiết bị vẫn có điện, switch vẫn sáng đèn link, nhưng không thiết bị nào trả
lời yêu cầu BACnet nào.

SOC trích một bản bắt gói từ phân đoạn BMS. Việc của bạn: dựng lại chuyện gì
đã xảy ra.

## Mục tiêu học

- Đọc được danh sách thiết bị BACnet và nhận ra host không thuộc về mạng đó.
- Phân biệt **đã thử** mật khẩu và **đã vào được**.
- Hiểu `DeviceCommunicationControl` làm gì và vì sao nó nguy hiểm đến thế.
- Hiểu `out-of-service` — cách làm mù người vận hành mà không động đến cảm biến.

## Kiến thức tối thiểu

BACnet/IP chạy trên **UDP 47808**. Mọi thứ là một *object* có kiểu và số thứ
tự: `AO:10` là analog-output số 10, `BI:30` là binary-input số 30. Mỗi object
có các *property* đánh số; hai cái cần nhớ:

| Property | Ý nghĩa khi bị ghi |
|---|---|
| `present-value` (85) | giá trị thật: mở khoá cửa, tắt đèn, dừng quạt |
| `out-of-service` (81) | **ngắt object khỏi thế giới vật lý** — màn hình vẫn hiện số, nhưng đó không còn là số thật |

Lệnh ghi mang theo **priority** từ 1 đến 16, số nhỏ thắng. Ghi ở priority 8 là
"thao tác tay của operator".

`DeviceCommunicationControl` (dịch vụ số 17) bảo thiết bị **ngừng trả lời toàn
bộ mạng**. Thiết bị vẫn chạy, đèn link vẫn sáng, nhưng màn hình điều khiển
trắng xoá. Bảo vệ duy nhất là một mật khẩu tuỳ chọn, gửi dạng rõ, không giới
hạn số lần thử.

## Các bước

### Bước 1 — Nhìn tổng thể (10')

```bash
python3 $TK/tools/pcap-overview.py de/lab1_bms.pcap
```

Xem bảng *talkers*. Trong mạng điều khiển, lưu lượng khá cân bằng vì các thiết
bị hỏi nhau theo chu kỳ. Host nào gửi nhiều bất thường?

### Bước 2 — Kiểm kê thiết bị (10')

```bash
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --devices
```

Thiết bị BACnet tự giới thiệu bằng bản tin `i-Am` kèm object của nó
(`device:901` chẳng hạn). Cuối báo cáo có danh sách host **chỉ gửi yêu cầu, không
bao giờ trả lời, và không bao giờ tự giới thiệu**.

> Một bộ điều khiển toà nhà thì trả lời câu hỏi. Một công cụ thì chỉ hỏi.

### Bước 3 — Các lần thử mật khẩu (20')

```bash
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --dcc
```

Đọc kỹ cột `outcome`. `security/password-failure` là bị từ chối; `ok` là thiết
bị đã chấp nhận (trả về SimpleACK).

Bảng thứ hai đếm số lần theo cặp (nguồn, đích). **Cẩn thận:** bảng này gộp cả
`deviceCommunicationControl` và `reinitializeDevice`. Câu hỏi hỏi riêng DCC thì
phải đếm riêng.

### Bước 4 — Cái gì đã bị thay đổi (20')

```bash
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --writes
```

Đọc theo thứ tự thời gian. Mỗi zone bị tác động ba lần: một cửa, một đầu ra
chiếu sáng, một cảm biến.

### Bước 5 — Dọn dấu vết (10')

```bash
python3 $TK/tools/bacnet-triage.py de/lab1_bms.pcap --timeline | tail -20
```

Dịch vụ cuối cùng dùng với Building Controller là gì, và nó làm gì?

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời | Frame |
|---|---|---|---|
| 1.1 | IP của thiết bị không thuộc mạng BMS | | |
| 1.2 | Số lần thử **DCC** vào Building Controller (sai + đúng) | | |
| 1.3 | Mật khẩu DCC được chấp nhận | | |
| 1.4 | Ba mật khẩu bị từ chối (liệt kê) | | |
| 1.5 | Ba zone bị tác động, **theo đúng thứ tự thời gian** (ghi IP) | | |
| 1.6 | Các object bị ghi ở zone **đầu tiên** (dạng `AO:1,BI:2`) | | |
| 1.7 | Thuộc tính bị ghi lên cảm biến, và priority | | |
| 1.8 | Dịch vụ cuối cùng dùng với Building Controller | | |

Câu suy luận, trả lời bằng 2–3 câu:

> **1.9** Vì sao kẻ tấn công ghi `out-of-service` lên cảm biến thay vì chỉ ghi
> `present-value`? Hai cách khác nhau thế nào dưới góc nhìn người trực ca?

## Khi bí

<details>
<summary>Gợi ý 1 — không biết bắt đầu từ đâu</summary>

Chạy `pcap-overview.py` trước. Nó cho biết có bao nhiêu host và giao thức gì.
Sau đó mới dùng công cụ chuyên cho BACnet.
</details>

<details>
<summary>Gợi ý 2 — không phân biệt được thành công và thất bại</summary>

Cột `outcome` trong `--dcc`. `ok` nghĩa là thiết bị trả về SimpleACK — tức là
đã chấp nhận mật khẩu. Bất kỳ giá trị nào khác là từ chối hoặc không trả lời.
</details>

<details>
<summary>Gợi ý 3 — câu 1.5, không biết thứ tự</summary>

Sắp theo cột `frame` hoặc `time`, tăng dần. Frame number chính là thứ tự gói
tin trong file.
</details>

<details>
<summary>Gợi ý 4 — câu 1.6, định dạng object</summary>

Cột `abbr` trong `--writes` đã ở đúng dạng viết tắt kiểu Wireshark.
</details>

## Ý nghĩa thực tế

Toàn bộ vụ này không khai thác một lỗ hổng nào. Mọi lệnh đều là chức năng hợp
lệ của BACnet, dùng đúng như tài liệu mô tả. Thứ bị khai thác là **khả năng
định tuyến tới mạng BMS** và **một mật khẩu yếu**.

Biện pháp rút ra được — ghi vào bài làm nếu còn thời gian:

- BMS nằm VLAN riêng, chặn UDP/47808 ở biên, chỉ cho phép từ máy vận hành.
- Đặt mật khẩu DCC trên mọi thiết bị, và **cảnh báo với mọi lệnh DCC /
  ReinitializeDevice** — dùng hợp lệ thì hiếm và luôn có kế hoạch trước.
- Giám sát ghi vào `out-of-service` và ghi ở priority 1–2.
- Nơi thiết bị hỗ trợ: BACnet/SC (có TLS và danh tính thiết bị).

Đọc thêm: [`docs/bacnet-ip.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/bacnet-ip.md).

Lời giải theo phương pháp: [`loi-giai/lab1-bacnet.md`](loi-giai/lab1-bacnet.md).
