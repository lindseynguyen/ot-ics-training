# 0 · Chuẩn bị môi trường

Thời lượng: 30 phút. Làm trước khi vào bài, hoặc ngay đầu buổi 1.

## Yêu cầu

- Python **3.9 trở lên**. Không cần cài thêm thư viện nào.
- Một trình duyệt (cho giao diện đồ hoạ).
- Khoảng 50 MB trống.

Kiểm tra:

```bash
python3 --version
```

Nếu máy không có Python 3: Windows tải từ python.org (nhớ tick *Add to PATH*),
Ubuntu/Debian `sudo apt install python3`, macOS đã có sẵn.

## Hai repo, đặt cạnh nhau

Khoá học dùng **hai** kho mã nguồn tách biệt:

| Repo | Vai trò |
|---|---|
| [`ot-ics-training`](https://github.com/lindseynguyen/ot-ics-training) | tài liệu khoá học + bộ sinh đề (repo bạn đang đọc) |
| [`Ics-toolkit`](https://github.com/lindseynguyen/Ics-toolkit) | **công cụ phân tích** mà mọi lab sẽ gọi |

Tải cả hai về **cùng một thư mục cha**:

```bash
mkdir ~/lab && cd ~/lab
git clone https://github.com/lindseynguyen/Ics-toolkit
git clone https://github.com/lindseynguyen/ot-ics-training
cd ot-ics-training
```

Kết quả:

```
~/lab/
  Ics-toolkit/        công cụ
  ot-ics-training/    tài liệu + đề   ← làm bài ở đây
```

Không có internet thì giảng viên phát hai thư mục đã giải nén — cả hai đều
không tải gì về khi chạy.

## Đặt biến `$TK`

Mọi lệnh trong tài liệu đều gọi công cụ qua biến `$TK`. Đặt một lần cho mỗi
cửa sổ dòng lệnh:

```bash
# Linux / macOS — đứng trong thư mục ot-ics-training
export TK=../Ics-toolkit
```

```powershell
# Windows PowerShell
$TK = "..\Ics-toolkit"
```

Kiểm tra:

```bash
ls $TK/tools | head -3
```

Nếu báo không tìm thấy: bạn chưa đứng đúng thư mục, hoặc hai repo không nằm
cạnh nhau.

> Mỗi lần mở cửa sổ dòng lệnh mới phải đặt lại `$TK`. Quên bước này là nguyên
> nhân số một của lỗi "no such file" trong buổi học.

## Kiểm tra bộ công cụ hoạt động

```bash
python3 $TK/tests/make_fixtures.py fixtures/
bash $TK/tests/run_all.sh fixtures/
```

Dòng cuối phải là `all tools ran successfully`. Nếu không, dừng lại và gọi
giảng viên — đừng vào lab với môi trường hỏng.

`fixtures/` là bộ dữ liệu mẫu dùng chung cả lớp để làm quen. Bộ đề chấm điểm
là thư mục riêng do giảng viên phát.

## Nhận đề của mình

Giảng viên phát một thư mục dạng `de-1001/`. Mở `DE-BAI.txt` xem danh sách
hiện vật và mã đề — **ghi mã đề vào đầu bài làm**, vì đáp án của mỗi người
khác nhau.

Chép thư mục đề vào chỗ dễ gõ, ngay trong thư mục `ot-ics-training`:

```bash
cp -r /duong/dan/de-1001 ./de/
ls de/
```

## Chạy thử giao diện

```bash
python3 $TK/gui/serve.py --workspace de/
```

Trình duyệt mở `http://127.0.0.1:8765/`. Kéo `de/lab1_bms.pcap` vào trang.
Giao diện phải nhận ra đó là capture chứa BACnet/IP và đề xuất các bước.

Dừng bằng `Ctrl+C` trong cửa sổ dòng lệnh.

> Giao diện chỉ lắng nghe trên máy của bạn (127.0.0.1). Không có gì được gửi
> đi đâu cả. Chi tiết trong [`docs/gui-guide.md` của Ics-toolkit](https://github.com/lindseynguyen/Ics-toolkit/blob/main/docs/gui-guide.md).

## Chạy thử dòng lệnh

```bash
python3 $TK/tools/pcap-overview.py de/lab1_bms.pcap
```

Phải thấy bảng các host và dòng `47808/udp  BACnet/IP`.

## Quy ước trong tài liệu

- Lệnh viết dạng `python3 $TK/tools/<tên>.py <file>`; chạy từ thư mục
  `ot-ics-training`, với `$TK` đã đặt như trên.
- `de/` là thư mục đề của bạn; thay bằng đường dẫn thật.
- Trên Windows dùng PowerShell: cú pháp lệnh giống hệt, chỉ khác dấu gạch
  trong đường dẫn và cách đặt biến (`$TK = "..\Ics-toolkit"`).
- Chữ **in đậm** trong phần câu hỏi là nội dung phải điền vào bài làm.

## Mẫu bài làm

Tạo file `bai-lam-<mã đề>.md` và dùng bảng này cho mọi lab:

| Lab | Câu hỏi | Trả lời | Frame / dòng | Lệnh đã dùng |
|---|---|---|---|---|
| 1 | IP thiết bị lạ | | | |

Cột **Frame / dòng** và **Lệnh đã dùng** được tính điểm ngang với cột trả lời.
Lý do: trong một vụ việc thật, kết luận không kiểm chứng được thì không dùng
được.
