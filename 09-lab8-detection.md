# Lab 8 · Biến phát hiện thành quy tắc giám sát

**Thời lượng:** 30 phút · **Hiện vật:** các pcap đã phân tích · **Mức:** trung bình

## Bối cảnh

Phân tích trả lời *đã xảy ra chuyện gì*. Quy tắc phát hiện trả lời *lần sau
xảy ra thì có biết không*. Lab này đi nốt đoạn còn lại.

## Mục tiêu học

- Hiểu cách suy ra danh sách host hợp lệ từ chính bản bắt gói.
- Biết vì sao **không được** để host đã có hành vi xấu vào allow-list.
- Biết những gì phải kiểm tra trước khi đưa một rule vào vận hành.
- Hiểu vì sao trong OT thì bắt đầu bằng chế độ cảnh báo, không phải chặn.

## Các bước

### Bước 1 — Sinh bộ rule (10')

```bash
python3 $TK/tools/make-rules.py de/lab1_bms.pcap de/lab2_modbus.pcap \
    de/lab3_s7.pcap --out rules-<mã đề>/
```

Đọc phần tóm tắt in ra màn hình trước:

- **devices**: host trả lời yêu cầu — tức là thiết bị thật;
- **approved clients**: host gửi yêu cầu và **không** hành xử như công cụ;
- danh sách bị loại trừ: host đã quét hoặc đã ra lệnh nguy hiểm.

### Bước 2 — Đọc rule Suricata (10')

```bash
head -40 rules-<mã đề>/ot-rules.rules
```

Mỗi rule có một dòng chú thích phía trên giải thích vì sao nó tồn tại. Chọn
một rule và trả lời: nó khớp cái gì, ở offset nào, và vì sao offset đó đúng?

Kiểm chứng offset:

```bash
python3 $TK/tests/check_rule_offsets.py fixtures/
```

> Một rule không bao giờ khớp còn tệ hơn không có rule, vì nó tạo cảm giác an
> toàn giả.

### Bước 3 — Đọc README do công cụ sinh ra (5')

```bash
cat rules-<mã đề>/README.md
```

Đây là phần quan trọng nhất của lab. Nó liệt kê đúng những gì cần kiểm tra
trước khi triển khai.

### Bước 4 — Phần Sigma (5')

```bash
head -40 rules-<mã đề>/sigma/ot-host-rules.yml
```

Các rule phía host: tạo tài khoản, xoá log, chạy công cụ tấn công, dừng dịch
vụ giám sát. Chúng bắt những gì bạn đã thấy ở Lab 6.

## Câu hỏi — điền vào bài làm

| # | Câu hỏi | Trả lời |
|---|---|---|
| 8.1 | Những IP nào được xếp là *devices* cho BACnet | |
| 8.2 | IP nào bị **loại khỏi** allow-list, vì sao | |
| 8.3 | Chọn một rule Suricata và giải thích nó khớp cái gì | |
| 8.4 | Vì sao rule vẫn được sinh cho cả thao tác **chưa** xảy ra trong capture | |
| 8.5 | Ba việc phải làm trước khi triển khai (theo README) | |

Câu suy luận:

> **8.6** Giả sử bạn đưa capture của Lab 1 vào và sinh rule, nhưng công cụ
> **không** loại IP tấn công ra khỏi allow-list. Hậu quả là gì?

> **8.7** Vì sao trong mạng OT nên chạy IDS ở chế độ cảnh báo (alert) trước,
> thay vì chặn (drop)? Nêu một tình huống cụ thể.

## Khi bí

<details>
<summary>Gợi ý 1 — không hiểu cú pháp Suricata</summary>

Đọc từ trái sang: `alert <giao thức> <nguồn> <cổng> -> <đích> <cổng> (msg:...;
content:"|..|"; offset:N; ...)`. `content` là chuỗi byte phải khớp,
`offset`/`depth` nói khớp ở đâu.
</details>

<details>
<summary>Gợi ý 2 — câu 8.4</summary>

Nghĩ về mục đích của việc giám sát: bắt cái **chưa** xảy ra. Nếu chỉ sinh rule
cho những gì đã xảy ra thì lần sau kẻ tấn công đổi kỹ thuật là mất dấu.
</details>

## Ý nghĩa thực tế

Nhắc lại bốn điều trong README sinh kèm, vì đây là phần học viên hay bỏ qua:

1. **Kiểm tra danh sách host** với sổ tài sản. Thiết bị im lặng hôm đó sẽ bị
   thiếu; laptop bảo trì cắm vào hôm đó sẽ bị coi là hợp lệ.
2. **Đo lại ngưỡng** cho các rule phát hiện quét, dựa trên tần suất hỏi vòng
   thật của hệ thống.
3. **Chạy thử với capture sạch.** `suricata -r baseline.pcap -S ot-rules.rules`
   phải im lặng. Nếu không, sửa rule chứ đừng sửa baseline.
4. **Bắt đầu bằng alert.** Trong OT, chặn nhầm một gói điều khiển có thể gây
   hậu quả ngang với chính cuộc tấn công.

Đọc thêm: [`docs/detection-rules.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/detection-rules.md).

Lời giải theo phương pháp: [`loi-giai/lab8-detection.md`](loi-giai/lab8-detection.md).
