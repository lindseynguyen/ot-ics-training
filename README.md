# Đào tạo phân tích hiện vật OT/ICS

Khoá đào tạo nội bộ **2 buổi (~8 giờ)** cho người **chưa có kinh nghiệm OT**:
tám bài thực hành trên gói tin, log và firmware mô phỏng, có lời giải cho
giảng viên và bộ sinh đề riêng cho từng học viên.

Mục tiêu sau khoá: học viên cầm một bộ hiện vật và tự trả lời được bốn câu hỏi
của một vụ việc OT — *ai đã nói chuyện, đọc hay ghi, thiết bị có chấp nhận
không, và theo thứ tự nào* — rồi viết thành báo cáo có số frame kèm theo.

> Toàn bộ dữ liệu thực hành là **mô phỏng**. Không có gói tin thật, không có
> thiết bị thật nào bị tác động, không chứa thông tin của tổ chức nào.

---

## Quan hệ với repo công cụ

Repo này **chỉ chứa tài liệu và bộ sinh đề**. Công cụ phân tích nằm ở một repo
riêng:

| Repo | Vai trò |
|---|---|
| **ot-ics-training** (repo này) | giáo án, 8 lab, lời giải, bài kiểm tra, bộ sinh đề |
| **[Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit)** | công cụ phân tích mà mọi lab gọi tới |

Tách ra vì hai thứ có vòng đời khác nhau: công cụ là mã nguồn mở dùng chung,
tài liệu là nội dung đào tạo tiếng Việt. Không có code nào bị trùng lặp giữa
hai repo.

```bash
mkdir ~/lab && cd ~/lab
git clone https://github.com/lindseynguyen/Ics-toolkit
git clone https://github.com/lindseynguyen/ot-ics-training
cd ot-ics-training
export TK=../Ics-toolkit          # Windows: $TK = "..\Ics-toolkit"
```

Chi tiết trong [`00-chuan-bi.md`](00-chuan-bi.md).

---

## Nội dung

### Buổi 1 — nền tảng và hai giao thức phổ biến (4h)

| Thời lượng | Nội dung | Tài liệu |
|---|---|---|
| 30' | Chuẩn bị môi trường, sinh đề, chạy thử | [`00-chuan-bi.md`](00-chuan-bi.md) |
| 60' | OT khác IT ở đâu; PLC/HMI/SCADA; vì sao giao thức không xác thực | [`01-nen-tang-ot.md`](01-nen-tang-ot.md) |
| 75' | **Lab 1** — BACnet/IP: dò mật khẩu, vô hiệu hoá thiết bị, làm mù cảm biến | [`02-lab1-bacnet.md`](02-lab1-bacnet.md) |
| 60' | **Lab 2** — Modbus/TCP: quét, ép coil, sửa setpoint, số thực 2 thanh ghi | [`03-lab2-modbus.md`](03-lab2-modbus.md) |
| 20' | Tổng kết, chữa bài | |

### Buổi 2 — giao thức sâu hơn, hiện vật nhị phân, sản phẩm đầu ra (4h)

| Thời lượng | Nội dung | Tài liệu |
|---|---|---|
| 60' | **Lab 3** — S7comm: fingerprint, tải logic, CPU STOP bị từ chối, ghi tag | [`04-lab3-s7comm.md`](04-lab3-s7comm.md) |
| 45' | **Lab 4** — IEC-104: select-before-operate, lệnh bị từ chối, STOPDT | [`05-lab4-iec104.md`](05-lab4-iec104.md) |
| 30' | **Lab 5** — thông tin đăng nhập dạng rõ, TDS | [`06-lab5-cleartext.md`](06-lab5-cleartext.md) |
| 45' | **Lab 6** — timeline đa nguồn: pcap + auth.log + bash history | [`07-lab6-timeline.md`](07-lab6-timeline.md) |
| 45' | **Lab 7** — firmware và HMI 16-bit: strings, hex, bin-diff | [`08-lab7-firmware.md`](08-lab7-firmware.md) |
| 30' | **Lab 8** — biến phát hiện thành rule Suricata/Zeek/Sigma | [`09-lab8-detection.md`](09-lab8-detection.md) |
| 30' | Bài kiểm tra cuối khoá | [`10-bai-kiem-tra.md`](10-bai-kiem-tra.md) |

Rút xuống 1 buổi: giữ `01`, Lab 1, Lab 2, Lab 6. Kéo lên 4 buổi: thêm thời
gian cho Lab 3, Lab 7, Lab 8 và cho học viên viết báo cáo hoàn chỉnh.

---

## Sinh đề

Mỗi học viên một mã đề riêng: IP, mật khẩu, tên zone, setpoint, mốc thời gian
đều khác nhau, nên không chép được của nhau.

```bash
# một bộ đề
python3 tao-de/make_lab.py --seed 101 --out lab-101/

# cả lớp, kèm đáp án và bảng chấm
printf 'Nguyen Van A\nTran Thi B\n' > hocvien.txt
python3 tao-de/make_lab.py --class-list hocvien.txt --out lop-t11/ \
    --dap-an --tracking --json
```

Kết quả:

```
lop-t11/
  de-1001/   11 hiện vật + DE-BAI.txt   ← phát cho học viên
  de-1002/   …
  dap-an-1001.md …                       ← giữ lại
  bang-theo-doi.csv                      ← bảng chấm cả lớp
```

Cùng một seed luôn sinh ra đúng bộ dữ liệu đó, nên không cần lưu trữ lâu dài —
giữ danh sách mã đề là tái tạo được.

Bộ sinh đề **không cần** repo công cụ: nó tự dựng gói tin
(`tao-de/pcap_builder.py`). Chỉ khi *phân tích* mới cần tới Ics-toolkit.

## Kiểm chứng đáp án

Một bộ đề mà đáp án sai thì tệ hơn không có. Script này sinh vài mã đề, chạy
**chính các công cụ học viên sẽ chạy**, rồi đối chiếu:

```bash
python3 tao-de/kiem-tra-dap-an.py
python3 tao-de/kiem-tra-dap-an.py 1001 1002 1003
python3 tao-de/kiem-tra-dap-an.py --toolkit ~/lab/Ics-toolkit
```

---

## Dành cho giảng viên

- [`huong-dan-giang-vien.md`](huong-dan-giang-vien.md) — giáo án chi tiết,
  bảng "lớp luôn vướng ở đâu", cách chấm, cách xử lý lớp lệch trình độ.
- [`loi-giai/`](loi-giai/) — lời giải **theo phương pháp**: từng bước, từng
  lệnh, cách đọc kết quả. Dùng được với mọi mã đề.
- Đáp án **cụ thể theo mã đề** sinh bằng `--dap-an`, không nằm sẵn trong repo.

> Thư mục `loi-giai/` nằm công khai trong repo. Nếu lớp của bạn tự tìm được
> repo này, hãy phát đề và chấm trước khi nhắc tới nó — hoặc giữ repo ở chế độ
> private cho tới sau khoá.

## Nguyên tắc sư phạm

1. **Hỏi câu hỏi của người trực ca, không hỏi câu hỏi của đề thi.** Mỗi lab
   kết thúc bằng một bảng phải điền: thời gian, nguồn, đích, hành động, kết
   quả, số frame.
2. **Phân biệt *đã thử* và *đã thành công*.** Kỹ năng quan trọng nhất, và là
   chỗ học viên mới sai nhiều nhất.
3. **GUI để bắt đầu, CLI để kết thúc.** Lab 1-2 cho phép dùng giao diện; từ
   Lab 3 yêu cầu gõ lệnh, vì lệnh mới là thứ dán được vào báo cáo.
4. **Mỗi phát hiện phải kèm số frame.** Không có số frame thì không phải phát
   hiện, chỉ là phỏng đoán.

## Giấy phép

MIT — xem [LICENSE](LICENSE). Dùng lại, sửa đổi và dạy lại thoải mái; nếu thấy
hữu ích thì ghi nguồn giúp.
