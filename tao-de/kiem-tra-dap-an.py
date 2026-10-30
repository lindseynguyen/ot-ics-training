#!/usr/bin/env python3
"""Kiểm tra bộ đề: đáp án sinh ra có khớp với hiện vật không.

Một bộ đề mà đáp án sai thì tệ hơn không có bộ đề nào, nên script này sinh một
vài mã đề, chạy **chính các công cụ mà học viên sẽ chạy** trong repo
Ics-toolkit, rồi đối chiếu kết quả với giá trị đã dùng để dựng artefact.

    python3 tao-de/kiem-tra-dap-an.py                     # 3 mã đề mặc định
    python3 tao-de/kiem-tra-dap-an.py 7 42 101
    python3 tao-de/kiem-tra-dap-an.py --toolkit ~/Ics-toolkit

Mặc định tìm bộ công cụ ở ../Ics-toolkit, hoặc theo biến môi trường
ICS_TOOLKIT.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from make_lab import build  # noqa: E402


def find_toolkit(explicit: str = "") -> str:
    """Tìm thư mục repo Ics-toolkit chứa các công cụ phân tích."""
    for cand in (explicit, os.environ.get("ICS_TOOLKIT", ""),
                 os.path.join(os.path.dirname(REPO), "Ics-toolkit"),
                 os.path.join(os.path.dirname(REPO), "ics-toolkit"),
                 os.path.join(REPO, "..", "Ics-toolkit")):
        if cand and os.path.isdir(os.path.join(cand, "tools")):
            return os.path.abspath(cand)
    raise SystemExit(
        "Không tìm thấy repo Ics-toolkit.\n"
        "Clone nó cạnh repo này:\n"
        "    git clone https://github.com/lindseynguyen/Ics-toolkit\n"
        "hoặc chỉ đường dẫn: --toolkit /duong/dan/Ics-toolkit")


TOOLKIT = ""


def run(tool: str, *args: str) -> str:
    """Chạy một công cụ; --quiet-size chỉ có ở các công cụ đọc capture."""
    base = [sys.executable, os.path.join(TOOLKIT, "tools", tool), *args]
    out = subprocess.run(base + ["--quiet-size"], capture_output=True,
                         text=True, cwd=TOOLKIT)
    if out.returncode != 0:
        out = subprocess.run(base, capture_output=True, text=True, cwd=TOOLKIT)
    return out.stdout + out.stderr


def check(seed: int) -> list:
    fails = []
    tmp = tempfile.mkdtemp(prefix=f"lab{seed}-")
    try:
        info = build(seed, tmp)
        v = info["values"]

        def expect(label: str, needle: str, text: str) -> None:
            if needle not in text:
                fails.append(f"[seed {seed}] {label}: không thấy {needle!r}")

        out = run("bacnet-triage.py", os.path.join(tmp, "lab1_bms.pcap"), "--dcc")
        expect("mật khẩu DCC đúng", repr(v["dcc_password"]), out)
        expect("IP tấn công BACnet", v["attacker_ot"], out)
        for pw in v["dcc_wrong"]:
            expect("mật khẩu sai", repr(pw), out)
        if out.count("security/password-failure") != len(v["dcc_wrong"]):
            fails.append(f"[seed {seed}] số lần từ chối DCC không khớp")

        out = run("bacnet-triage.py", os.path.join(tmp, "lab1_bms.pcap"), "--writes")
        expect("object cửa zone 1", f"BO:{v['door_objects'][0]}", out)
        expect("out-of-service", "out-of-service", out)

        out = run("modbus-triage.py", os.path.join(tmp, "lab2_modbus.pcap"), "--writes")
        expect("coil báo động", f"coil {v['alarm_coil']}", out)
        expect("thanh ghi setpoint", f"hreg {v['setpoint_reg']}", out)

        out = run("modbus-triage.py", os.path.join(tmp, "lab2_modbus.pcap"), "--floats")
        expect("giá trị setpoint", str(v["new_setpoint"]), out)

        out = run("s7-triage.py", os.path.join(tmp, "lab3_s7.pcap"), "--szl")
        for szl in v["szl_ids"]:
            expect("SZL id", f"0x{szl:04x}", out)

        out = run("s7-triage.py", os.path.join(tmp, "lab3_s7.pcap"), "--blocks")
        for _code, _num, name in v["blocks"]:
            expect("khối logic", name, out)

        out = run("s7-triage.py", os.path.join(tmp, "lab3_s7.pcap"), "--writes")
        expect("tag bị ghi", f"DB{v['db_number']}.DBX{v['db_offset']}.0", out)
        expect("giá trị clo mới", str(v["chlorine_new"]), out)

        out = run("s7-triage.py", os.path.join(tmp, "lab3_s7.pcap"), "--control")
        if "class 0x81" not in out:
            fails.append(f"[seed {seed}] CPU STOP phải bị từ chối nhưng không thấy lỗi")

        out = run("iec104-triage.py", os.path.join(tmp, "lab4_iec104.pcap"), "--sbo")
        expect("IOA execute-không-select", str(v["ioa_valve"]), out)
        expect("IOA select treo", str(v["ioa_valve"] + 1), out)

        out = run("cleartext-creds.py", os.path.join(tmp, "lab5_dmz.pcap"))
        expect("mật khẩu SQL", v["sql_password"], out)
        expect("mật khẩu FTP", v["ftp_password"], out)
        expect("SNMP community", v["snmp_community"], out)

        out = run("timeline.py", os.path.join(tmp, "lab6_auth.log"),
                  os.path.join(tmp, "lab6_bash_history"), "--min-severity", "impact")
        expect("tài khoản mới", v["new_account"], out)
        expect("dịch vụ bị dừng", "stopped", out.lower())

        out = run("bin-diff.py", os.path.join(tmp, "lab7_rig_v1.gb"),
                  os.path.join(tmp, "lab7_rig_v2.gb"))
        # bin-diff in số thực theo %g, nên 8.0 hiển thị là "8"
        expect("hằng số firmware cũ", f"{v['rom_old_limit']:.6g}", out)
        expect("hằng số firmware mới", f"{v['rom_new_limit']:.6g}", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return fails


def main() -> int:
    global TOOLKIT
    args = sys.argv[1:]
    explicit = ""
    if "--toolkit" in args:
        i = args.index("--toolkit")
        explicit = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
    TOOLKIT = find_toolkit(explicit)
    print(f"bộ công cụ: {TOOLKIT}\n")
    seeds = [int(x) for x in args] or [7, 42, 101]
    all_fails = []
    for seed in seeds:
        fails = check(seed)
        print(f"mã đề {seed}: {'OK' if not fails else str(len(fails)) + ' sai lệch'}")
        all_fails += fails
    if all_fails:
        print()
        for f in all_fails:
            print("  -", f)
        return 1
    print("\nđáp án của mọi mã đề đều khớp với hiện vật")
    return 0


if __name__ == "__main__":
    sys.exit(main())
