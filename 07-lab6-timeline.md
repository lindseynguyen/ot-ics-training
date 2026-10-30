# Lab 6 · Dựng một dòng thời gian từ nhiều nguồn

**Thời lượng:** 45 phút · **Hiện vật:** tất cả pcap + `lab6_auth.log` +
`lab6_bash_history` · **Mức:** trung bình

## Bối cảnh

Đến đây bạn đã có năm báo cáo rời rạc. Ban lãnh đạo không đọc năm báo cáo —
họ hỏi một câu: **chuyện gì đã xảy ra, theo thứ tự nào?**

Một bản bắt gói trả lời "có gì trên đường truyền". Một file log trả lời "có gì
trên máy chủ". Không cái nào trả lời được câu hỏi trên, vì một vụ xâm nhập đi
qua cả hai.

## Mục tiêu học

- Gộp pcap và log thành một dòng thời gian UTC duy nhất.
- Đọc dòng thời gian theo cách của người xử lý sự cố: tìm sự kiện *impact* đầu
  tiên rồi đọc ngược lên.
- Nhận ra mẫu **làm im tiếng trước, ra tay sau**.
- Biết các bẫy đồng hồ, đặc biệt là syslog không có năm.

## Kiến thức tối thiểu

`timeline.py` đọc:

| Nguồn | Lấy ra cái gì |
|---|---|
| pcap | các sự kiện giao thức **đáng kể** (không dump toàn bộ gói) |
| syslog / auth.log | đăng nhập thành công và thất bại, sudo, tạo tài khoản, dừng dịch vụ |
| bash history | mọi lệnh, có thời gian nếu file được ghi với `HISTTIMEFORMAT` |
| CSV | bất kỳ cột nào phân tích được thành thời gian |

Bốn mức severity: `context` → `recon` → `suspicious` → `impact`.
`impact` nghĩa là **có cái gì đó đã bị thay đổi** — một giá trị, một tài
khoản, một kênh báo cáo — chứ không phải "đã chứng minh có thiệt hại".

**Syslog không có năm.** Công cụ lấy năm từ thời gian sửa file; nếu sai, các
sự kiện log sẽ nằm cách các sự kiện pcap cả năm. Sửa bằng `--log-year`.

## Các bước

### Bước 1 — Dựng dòng thời gian (10')

```bash
python3 $TK/tools/timeline.py de/*.pcap de/lab6_auth.log de/lab6_bash_history \
    --log-year <năm trong DE-BAI.txt> --min-severity suspicious
```

Nếu các sự kiện log nằm lệch hẳn so với pcap: bạn đặt sai `--log-year`.

### Bước 2 — Đọc ngược từ sự kiện impact đầu tiên (15')

Bảng thứ hai (*events that touched the process or an account*) là danh sách
ngắn đáng quan tâm.

Tìm dòng `impact` **sớm nhất**, rồi đọc các dòng ngay **phía trên** nó: đó
thường là nơi kẻ tấn công có được quyền truy cập.

### Bước 3 — Tìm mẫu làm im tiếng (10')

Giữa lúc có quyền và lúc ra tay, tìm những hành động làm giảm khả năng quan
sát:

- ép coil báo động về 0 (Lab 2);
- ghi `out-of-service` lên cảm biến (Lab 1);
- `STOPDT` (Lab 4);
- dừng dịch vụ historian (log);
- `disable-unsolicited` (DNP3).

### Bước 4 — Khoảng lặng (5')

```bash
python3 $TK/tools/timeline.py de/*.pcap de/lab6_*.log de/lab6_bash_history \
    --log-year <năm> --gaps 300
```

Traffic điều khiển có chu kỳ. Một khoảng im lặng dài nghĩa là: capture dừng,
thiết bị ngừng trả lời, hoặc báo cáo đã bị chặn.

### Bước 5 — Xuất báo cáo (5')

```bash
python3 $TK/tools/timeline.py de/*.pcap de/lab6_auth.log de/lab6_bash_history \
    --log-year <năm> --md bao-cao-<mã đề>.md
```

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời | Frame / dòng |
|---|---|---|---|
| 6.1 | IP tấn công phía IT | | |
| 6.2 | Tài khoản dịch vụ bị chiếm, và cách chiếm | | |
| 6.3 | Tài khoản mới được tạo, và nhóm được thêm vào | | |
| 6.4 | Công cụ được tải về, từ đâu | | |
| 6.5 | Sự kiện `impact` **sớm nhất** trong toàn bộ vụ việc | | |
| 6.6 | Hai hành động làm giảm khả năng quan sát, kèm thời điểm | | |
| 6.7 | Hành động xoá dấu vết, và thời điểm | | |

Bài viết (chấm riêng):

> **6.8** Viết **sáu đến tám câu** tóm tắt vụ việc theo thứ tự thời gian, kiểu
> báo cáo gửi trưởng ca. Mỗi câu phải kèm số frame hoặc số dòng. Không dùng từ
> "hacker"; gọi theo IP và tài khoản.

## Khi bí

<details>
<summary>Gợi ý 1 — log và pcap lệch nhau cả năm</summary>

Sai `--log-year`. Mở `lab6_auth.log`, xem tháng/ngày, đối chiếu với thời gian
trong pcap (`pcap-overview.py` in ra khoảng thời gian).
</details>

<details>
<summary>Gợi ý 2 — quá nhiều dòng</summary>

Nâng ngưỡng: `--min-severity impact`. Khi đã nắm bộ khung thì hạ xuống
`suspicious` để điền chi tiết.
</details>

<details>
<summary>Gợi ý 3 — không tìm thấy lệnh trong bash history</summary>

Các dòng `#1762000000` là mốc thời gian, dòng tiếp theo mới là lệnh. Công cụ
đã ghép sẵn.
</details>

## Ý nghĩa thực tế

Dòng thời gian là sản phẩm cuối cùng của phân tích, và cũng là đầu vào của ba
việc khác: báo cáo sự cố, quy tắc phát hiện (Lab 8), và bài học rút kinh
nghiệm.

Hai điều cần nhớ khi làm thật:

- **Đồng hồ các nguồn hiếm khi khớp nhau.** PLC, jump host và SIEM có thể lệch
  hàng giờ. Kiểm tra một sự kiện đã biết ở hai nguồn trước khi tin vào thứ tự.
- **Đồng bộ đồng hồ là một chức năng của giao thức.** IEC-104 và DNP3 đặt được
  đồng hồ thiết bị, nên dấu thời gian từ thiết bị hiện trường chỉ đáng tin
  bằng cái master đã đặt nó.

Đọc thêm: [`docs/timeline.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/timeline.md).

Lời giải theo phương pháp: [`loi-giai/lab6-timeline.md`](loi-giai/lab6-timeline.md).
