# Lời giải Lab 8 — quy tắc phát hiện

## Trình tự giải

```bash
python3 $TK/tools/make-rules.py de/lab1_bms.pcap de/lab2_modbus.pcap \
    de/lab3_s7.pcap --out rules-<mã đề>/
cat rules-<mã đề>/README.md
head -40 rules-<mã đề>/ot-rules.rules
head -40 rules-<mã đề>/sigma/ot-host-rules.yml
python3 $TK/tests/check_rule_offsets.py fixtures/
```

## 8.1 / 8.2 — Cách suy ra danh sách host

Công cụ phân loại theo hành vi, không theo địa chỉ:

- **device** = host **trả lời** yêu cầu (gửi ack, response, hoặc `i-Am`);
- **client** = host **gửi** yêu cầu;
- **bị loại trừ** = host đã quét, hoặc đã phát các lệnh nguy hiểm (DCC,
  reinitialize, CPU STOP, ghi Modbus).

Lý do loại trừ phải nói rõ cho lớp: nếu xây allow-list từ một capture có chứa
cuộc tấn công mà không loại kẻ tấn công ra, thì **rule sẽ hợp pháp hoá chính
kẻ tấn công** — lần sau nó làm lại, không có cảnh báo nào. Đó là nội dung câu
8.6.

## 8.3 — Đọc một rule

Ví dụ rule DCC:

```
alert udp !$BACNET_CLIENTS any -> $BACNET_DEVICES 47808 (
    msg:"OT BACnet DeviceCommunicationControl from a host outside the allow-list";
    content:"|81|"; offset:0; depth:1;      # byte đầu của BVLC
    content:"|01|"; offset:4; depth:1;      # phiên bản NPDU
    content:"|00|"; offset:6; depth:1;      # APDU: confirmed-request
    content:"|11|"; offset:9; depth:1;      # service choice 17 = DCC
    ...)
```

Đọc từ trái sang: cảnh báo khi **udp**, nguồn **không nằm trong** danh sách
client hợp lệ, đích là thiết bị BACnet cổng 47808, và payload có đúng bốn byte
đó ở đúng bốn vị trí đó.

Học viên nên trả lời được: `offset:9` là vị trí của mã dịch vụ trong APDU khi
bản tin không bị phân mảnh và không có header định tuyến BACnet.

## Vì sao phải kiểm chứng offset

`$TK/tests/check_rule_offsets.py` đối chiếu từng offset với lưu lượng thật. Nói
thẳng với lớp: **một rule không bao giờ khớp thì tệ hơn không có rule**, vì nó
tạo cảm giác đã được giám sát. Đây là lỗi rất hay gặp khi người ta chép rule
từ internet về mà không thử.

## 8.4 — Vì sao sinh rule cho cả thao tác chưa xảy ra

Mục đích của giám sát là bắt cái **chưa** xảy ra. Nếu chỉ viết rule cho những
gì đã thấy trong một capture, thì lần sau kẻ tấn công dùng kỹ thuật khác trong
cùng giao thức là mất dấu hoàn toàn.

`--only-observed` tồn tại cho trường hợp cần bộ rule hẹp, ví dụ khi hệ thống
IDS đã quá tải.

## 8.5 — Bốn việc phải làm trước khi triển khai

Lấy từ README sinh kèm:

1. Đối chiếu danh sách host với **sổ tài sản** — thiết bị im lặng hôm đó bị
   thiếu, laptop bảo trì hôm đó bị coi là hợp lệ.
2. **Đo lại ngưỡng** phát hiện quét theo tần suất hỏi vòng thật.
3. **Chạy thử với capture sạch**; nếu có cảnh báo thì sửa rule, không sửa
   baseline.
4. **Bắt đầu bằng alert, không phải drop.**

## 8.7 — Vì sao alert trước, drop sau

Tình huống cụ thể để lớp thảo luận: một rule chặn Modbus function 6 từ host
không nằm trong allow-list. Trong kỳ bảo trì, kỹ sư dùng laptop mới chưa kịp
cập nhật danh sách. IDS chặn lệnh ghi; thiết bị không nhận được lệnh dừng;
hoặc tệ hơn, HMI treo vì timeout giữa lúc đang thao tác.

Trong IT, chặn nhầm một gói nghĩa là một kết nối hỏng. Trong OT, nó có thể
nghĩa là một thao tác vận hành không hoàn tất. Quyết định chuyển sang chặn là
quyết định của người chịu trách nhiệm về quá trình, không phải của người viết
rule.

## Thời gian dự kiến

25–30 phút. Nếu thiếu giờ, giảng viên chạy demo và lớp chỉ đọc README sinh kèm.
