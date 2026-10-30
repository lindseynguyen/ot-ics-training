# Lời giải Lab 6 — dòng thời gian

## Trình tự giải

```bash
python3 $TK/tools/timeline.py de/*.pcap de/lab6_auth.log de/lab6_bash_history \
    --log-year <năm> --min-severity suspicious

python3 $TK/tools/timeline.py de/*.pcap de/lab6_auth.log de/lab6_bash_history \
    --log-year <năm> --min-severity impact          # danh sách ngắn

python3 $TK/tools/timeline.py de/*.pcap de/lab6_*.log de/lab6_bash_history \
    --log-year <năm> --gaps 300 --md bao-cao.md
```

## Bẫy `--log-year`

Đây là bẫy cố ý. Syslog không mang năm, nên công cụ lấy năm từ thời gian sửa
file — thường là năm hiện tại, trong khi dữ liệu lab có mốc khác.

Dấu hiệu: các dòng từ `auth.log` nằm tách hẳn khỏi các dòng từ pcap, cách nhau
đúng một năm. Để học viên tự nhận ra trong khoảng 5 phút, vì đây là lỗi họ sẽ
gặp lại trong công việc thật.

Năm đúng: xem `DE-BAI.txt`, hoặc đối chiếu khoảng thời gian do
`pcap-overview.py` in ra.

## 6.1 → 6.4 — Phía IT

Đọc từ `auth.log` và `bash_history`:

- hai lần `Failed password`, rồi một `Invalid user`, rồi **`Accepted password`**
  cho tài khoản dịch vụ — mẫu dò mật khẩu thành công;
- `useradd` tạo tài khoản mới, `usermod` thêm vào nhóm `sudo` — thiết lập chỗ
  đứng lâu dài;
- `curl` tải một script về `/tmp`;
- `nmap` quét các cổng OT.

## 6.5 — Sự kiện impact sớm nhất

Lấy từ bảng thứ hai (*events that touched the process or an account*), dòng
đầu tiên.

Dạy học viên thói quen: **tìm dòng impact sớm nhất, rồi đọc ngược lên**. Quyền
truy cập được lấy ở đâu đó phía trên, và mọi thứ giữa hai mốc đó là chuẩn bị.

## 6.6 — Hành động làm giảm khả năng quan sát

Trong kịch bản này có ít nhất ba, trải trên nhiều nguồn:

| Hành động | Nguồn |
|---|---|
| ép coil báo động về 0 | `lab2_modbus.pcap` |
| ghi `out-of-service` lên cảm biến | `lab1_bms.pcap` |
| `STOPDT` | `lab4_iec104.pcap` |
| dừng dịch vụ Historian Collector | `lab6_auth.log` |

Học viên chỉ cần hai, nhưng nếu nêu được rằng chúng đến từ **bốn nguồn khác
nhau** thì đó là dấu hiệu đã hiểu mục đích của lab: không nguồn nào một mình
kể được câu chuyện.

## 6.7 — Xoá dấu vết

`echo '' > ~/.bash_history` và `rm -f /var/log/auth.log.1`, cuối dòng thời
gian.

Điểm trớ trêu đáng chỉ ra cho lớp: chính lệnh xoá lịch sử lại **nằm trong
lịch sử**, vì file được ghi khi phiên kết thúc. Và bản `auth.log` hiện tại vẫn
còn — chỉ bản xoay vòng `.1` bị xoá.

## 6.8 — Bài viết

Mẫu một đoạn đạt yêu cầu (số liệu theo mã đề 101, học viên sẽ khác):

> Lúc 17:25:40 UTC, địa chỉ 172.27.30.247 đăng nhập thành công vào jump host
> bằng tài khoản `hmi_svc` sau hai lần sai mật khẩu (dòng 1-4, `lab6_auth.log`).
> Trong vòng một phút, một tài khoản cục bộ `maint` được tạo và thêm vào nhóm
> `sudo` (dòng 7-8). Một script được tải về `/tmp` từ chính địa chỉ đó (dòng 6,
> `lab6_bash_history`), sau đó là một lần quét các cổng 502, 102, 47808 và 2404
> trên dải mạng OT (dòng 8). Từ 17:26:40, địa chỉ 10.32.59.80 dò mật khẩu
> DeviceCommunicationControl trên bộ điều khiển BMS, thành công ở lần thứ năm
> (frame 20, `lab1_bms.pcap`), rồi lần lượt vô hiệu hoá ba zone và ghi
> `out-of-service` lên ba cảm biến (frame 22-44). Song song, 172.27.30.104 ép
> coil 13 về 0 và ghi setpoint 62.75 vào thanh ghi 4x44 (frame 27 và 29,
> `lab2_modbus.pcap`). Dịch vụ thu thập dữ liệu historian bị dừng lúc 17:46:40
> (dòng 10, `lab6_auth.log`). Cuối cùng, lịch sử lệnh và một bản log xoay vòng
> bị xoá lúc 17:48:30 (dòng 12-14).

Tiêu chí chấm: mỗi câu có mốc thời gian hoặc số frame/dòng; gọi theo IP và tài
khoản, không dùng từ "hacker"; thứ tự đúng; có nêu được cả việc **thất bại**
nếu học viên viết dài hơn.

## Thời gian dự kiến

35–45 phút, trong đó 10 phút đầu thường mất vào `--log-year`.
