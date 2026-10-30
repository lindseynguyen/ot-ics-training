# Bài kiểm tra cuối khoá

**Thời lượng:** 30 phút làm bài + 15 phút chữa · **Hình thức:** mở tài liệu,
mở công cụ, cấm trao đổi.

Mỗi học viên làm trên **mã đề của chính mình**. Đề khác nhau nên đáp án khác
nhau — chép của nhau sẽ sai ngay câu đầu.

## Phần A — Tình huống (60 điểm)

> 06:40 sáng, trực ca gọi: màn hình BMS trắng, một số cảm biến hiện giá trị
> "đứng im" suốt đêm, và bộ phận vận hành báo liều clo sáng nay cao bất
> thường. Bạn được giao toàn bộ hiện vật trong thư mục đề của mình và có 30
> phút để trả lời ban chỉ huy.

Nộp một bảng theo đúng mẫu sau. **Mỗi dòng không có frame/dòng số thì không
tính điểm.**

| # | Câu hỏi | Trả lời | Frame / dòng | Lệnh đã dùng |
|---|---|---|---|---|
| A1 | Điểm truy cập đầu tiên vào hệ thống (IP, tài khoản, cách vào) | | | |
| A2 | Thời điểm sớm nhất có hành động **thay đổi** thứ gì đó (UTC) | | | |
| A3 | Mật khẩu BACnet được chấp nhận và số lần thử trước đó | | | |
| A4 | Ba hành động làm giảm khả năng quan sát của người vận hành | | | |
| A5 | Giá trị quá trình bị thay đổi: tag nào, từ bao nhiêu sang bao nhiêu | | | |
| A6 | Lệnh nào kẻ tấn công **đã thử nhưng thất bại**, vì sao thất bại | | | |
| A7 | Bằng chứng xoá dấu vết | | | |

## Phần B — Suy luận (25 điểm)

Trả lời ngắn, 3–5 câu mỗi ý.

> **B1 (10đ)** Sắp xếp năm giai đoạn sau theo đúng thứ tự xảy ra trong vụ
> việc của bạn, kèm mốc thời gian cho từng giai đoạn: thu thập thông tin;
> truy cập ban đầu; làm tê liệt phản hồi; làm sai lệch điều khiển; xoá dấu
> vết.

> **B2 (8đ)** Trong số những thay đổi bạn tìm được, cái nào khó bị phát hiện
> nhất bởi người trực ca, và vì sao?

> **B3 (7đ)** Nếu chỉ được triển khai **một** biện pháp kỹ thuật trong tuần
> tới để vụ việc này không lặp lại, bạn chọn gì? Lập luận bằng dữ liệu trong
> đề, không bằng nguyên tắc chung.

## Phần C — Sản phẩm (15 điểm)

Nộp kèm hai file:

1. `bao-cao-<mã đề>.md` — dòng thời gian xuất từ công cụ:

   ```bash
   python3 $TK/tools/timeline.py de/*.pcap de/lab6_auth.log de/lab6_bash_history \
       --log-year <năm> --min-severity suspicious --md bao-cao-<mã đề>.md
   ```

2. `rules-<mã đề>/` — bộ quy tắc phát hiện, kèm **một câu** nói rõ bạn đã sửa
   gì trong allow-list so với bản sinh tự động, và vì sao.

## Thang điểm

| Phần | Điểm | Ghi chú |
|---|---|---|
| A | 60 | mỗi câu ~8–9đ; thiếu frame/dòng trừ 3đ mỗi câu |
| B | 25 | chấm theo lập luận, không theo từ khoá |
| C | 15 | 8đ cho timeline, 7đ cho rule + giải thích |
| Thưởng | +5 | làm toàn bộ bằng dòng lệnh, không dùng GUI |

**Đạt:** từ 60/100. **Khá:** 75. **Giỏi:** 85 và trả lời đúng A6 (phân biệt
*đã thử* và *đã thành công*).

## Lỗi bị trừ điểm nặng

- Viết "PLC bị tấn công" mà không nói rõ lệnh nào thành công, lệnh nào bị từ
  chối.
- Nhầm chiều "download": nói kẻ tấn công *lấy* logic ra, trong khi thực tế là
  *đẩy* logic vào.
- Kết luận mà không có số frame.
- Dùng giá trị số thực sai thứ tự từ (ví dụ nói setpoint là `1.4e-42`).
- Gộp `deviceCommunicationControl` và `reinitializeDevice` thành một con số
  khi đếm số lần thử mật khẩu.
