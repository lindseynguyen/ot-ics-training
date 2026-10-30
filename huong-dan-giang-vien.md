# Hướng dẫn giảng viên

Tài liệu này chỉ dành cho người đứng lớp. Không phát cho học viên.

## Chuẩn bị trước buổi học

**Trước một tuần**

- Gửi học viên yêu cầu cài Python 3.9+ và kiểm tra bằng `python3 --version`.
- Chuẩn bị phương án offline: một bản `.zip` của repo và bản cài Python, vì
  lớp hay thiếu quyền cài phần mềm hoặc thiếu internet.

**Trước một ngày**

```bash
printf 'Nguyen Van A\nTran Thi B\n...' > hocvien.txt
python3 tao-de/make_lab.py --class-list hocvien.txt --out lop-<thang>/ --dap-an
```

Kết quả: mỗi học viên một thư mục `de-10NN/` và một file `dap-an-10NN.md` cho
bạn. **Chỉ phát thư mục đề.**

Tự chạy thử một mã đề từ đầu đến cuối. Mất khoảng 40 phút và sẽ cho bạn thấy
trước những chỗ lớp sẽ vướng.

**Đầu buổi**

Chạy trước mặt lớp:

```bash
python3 $TK/tests/make_fixtures.py fixtures/
bash $TK/tests/run_all.sh fixtures/
```

Nếu máy ai đó không ra `all tools ran successfully`, xử lý ngay — đừng để họ
vào lab với môi trường hỏng, vì sau đó mọi lỗi đều bị quy cho công cụ.

## Nhịp độ

| | Nội dung | Phút |
|---|---|---|
| Buổi 1 | chuẩn bị | 30 |
| | lý thuyết nền tảng | 60 |
| | Lab 1 (BACnet) | 75 |
| | Lab 2 (Modbus) | 60 |
| | chữa bài + tổng kết | 20 |
| Buổi 2 | Lab 3 (S7comm) | 60 |
| | Lab 4 (IEC-104) | 45 |
| | Lab 5 (cleartext) | 30 |
| | Lab 6 (timeline) | 45 |
| | Lab 7 (firmware) | 45 |
| | Lab 8 (detection) | 30 |
| | kiểm tra + chữa | 45 |

Nếu chậm tiến độ: cắt Lab 5 (ngắn, có thể giao về nhà) và rút Lab 8 xuống còn
phần demo của giảng viên. **Không cắt Lab 6** — đó là bài gắn kết cả khoá.

## Những chỗ lớp luôn vướng

| Vướng ở đâu | Dấu hiệu | Cách xử lý |
|---|---|---|
| Đường dẫn file | "no such file" | Yêu cầu `cd` vào thư mục repo và dùng `ls de/` trước khi chạy |
| Không phân biệt thử/thành công | Trả lời "đã dừng được PLC" ở Lab 3 | Dừng cả lớp, chiếu cột `error`, giải thích ack-data. Đây là điểm quan trọng nhất của khoá |
| Đếm nhầm số lần thử DCC | Trả lời 6 thay vì 5 | Chỉ ra bảng tổng hợp gộp cả `reinitializeDevice` |
| Chiều "download" | Nói kẻ tấn công tải logic *về* | Nhắc lại quy ước Siemens: download = xuống PLC |
| Thứ tự từ của số thực | Setpoint ra `1.4e-42` | Chỉ hai cột trong `--floats`, hỏi "giá trị nào hợp lý cho một bể nước?" |
| `--log-year` ở Lab 6 | Log lệch pcap cả năm | Đây là bẫy cố ý. Để họ tự phát hiện 5 phút rồi mới gợi ý |
| Trả lời không kèm frame | Bảng thiếu cột | Nhắc ngay từ Lab 1, trừ điểm từ Lab 2 |

## Lớp lệch trình độ

Luôn có 2–3 người xong sớm. Giao thêm:

- Lab 4 mở rộng DNP3 đầy đủ, kèm giải thích CROB.
- Tự viết một rule Suricata **bằng tay** cho một thao tác chưa có trong bộ
  sinh tự động, rồi kiểm chứng offset bằng `$TK/tests/check_rule_offsets.py`.
- Chạy `tools/triage-plan.py` trên toàn bộ thư mục đề và nhận xét: công cụ đề
  xuất thiếu bước nào?

Người chậm: cho dùng GUI đến hết Lab 4, nhưng bắt buộc chép câu lệnh hiển thị
trong giao diện vào bài làm.

## Cách chấm

Chấm theo `dap-an-<mã đề>.md` sinh kèm. Nguyên tắc:

- **Đúng giá trị nhưng không có frame: trừ 2–3 điểm.** Trong vụ việc thật,
  kết luận không kiểm chứng được thì không dùng được.
- **Câu "có thành công không" tính điểm cao hơn câu giá trị.** Một học viên
  trả lời sai giá trị nhưng phân biệt đúng thử/thành công vẫn hiểu việc; ngược
  lại thì không.
- **Phần suy luận chấm theo lập luận**, không theo việc có nhắc đúng từ khoá.
  Một lập luận sai nhưng dựa trên dữ liệu trong đề vẫn hơn một câu đúng chép
  từ tài liệu.

## Nếu lớp hỏi những câu này

**"Công cụ này có chạy được trên hệ thống thật của mình không?"**
Có, nhưng chỉ để **đọc** file bắt gói và file đã trích xuất. Nó không gửi gói
tin tới thiết bị, không quét, không thay đổi gì. Bắt gói trên hệ thống thật
phải xin phép và phải dùng cổng mirror/TAP, không cắm thẳng vào mạng điều
khiển.

**"Sao không dùng Wireshark?"**
Vẫn nên dùng Wireshark để xem chi tiết một gói. Bộ công cụ này trả lời câu hỏi
khác: trong 40.000 gói thì **mười hai việc đáng quan tâm là gì**, dưới dạng
bảng dán được vào báo cáo. `docs/workflow.md` có sẵn các display filter tương
đương.

**"Dữ liệu lab có thật không?"**
Không. Toàn bộ do `tao-de/make_lab.py` dựng, từng trường đều biết trước. Đó cũng là
lý do đáp án luôn khớp tuyệt đối.

**"Học xong thì làm được gì ở đơn vị?"**
Ba việc, theo thứ tự dễ đến khó: đọc được một bản bắt gói OT khi có sự cố;
dựng được dòng thời gian từ nhiều nguồn cho báo cáo; đề xuất được quy tắc
giám sát dựa trên hành vi thật thay vì danh sách chung chung.

## Sau khoá

- Thu lại bài làm, chấm theo đáp án, gửi lại kèm nhận xét từng người.
- Giữ `dap-an-*.md` để lần sau dùng lại đề cũ cho lớp khác (seed khác nhau thì
  đề khác nhau, nên không sợ lộ).
- Gợi ý cho học viên khá: đọc tiếp `docs/attack-mapping.md` và
  `docs/defense-notes.md`, rồi thử áp dụng vào một phân đoạn thật của đơn vị.
