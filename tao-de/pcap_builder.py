#!/usr/bin/env python3
"""Dựng gói tin thủ công cho bộ đề thực hành.

Mỗi trường trong gói tin được ghi tường minh ở đây, nên giá trị của nó luôn
biết trước - đó là lý do đáp án của bộ đề luôn khớp tuyệt đối với kết quả mà
công cụ phân tích in ra.

Không có dữ liệu thật trong module này. Không gói tin nào được gửi đi đâu cả;
tất cả chỉ được ghi vào file .pcap.
"""
from __future__ import annotations

import struct


# ---------------------------------------------------------------- pcap writer
class PcapWriter:
    def __init__(self, path: str, linktype: int = 1):
        self.count = 0          # frame number of the packet written last
        self.fh = open(path, "wb")
        self.fh.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 262144, linktype))
        self.t = 1700000000.0

    def close(self) -> None:
        self.fh.close()

    def _write(self, frame: bytes, dt: float = 0.01) -> None:
        self.t += dt
        self.count += 1
        sec = int(self.t)
        usec = int(round((self.t - sec) * 1e6))
        self.fh.write(struct.pack("<IIII", sec, usec, len(frame), len(frame)))
        self.fh.write(frame)

    @staticmethod
    def _ip(src: str, dst: str, proto: int, payload: bytes) -> bytes:
        total = 20 + len(payload)
        hdr = struct.pack(">BBHHHBBH4s4s", 0x45, 0, total, 0x1234, 0, 64, proto, 0,
                          bytes(int(x) for x in src.split(".")),
                          bytes(int(x) for x in dst.split(".")))
        return hdr + payload

    def udp(self, src: str, dst: str, sport: int, dport: int, data: bytes,
            dt: float = 0.01) -> None:
        udp = struct.pack(">HHHH", sport, dport, 8 + len(data), 0) + data
        frame = (b"\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x08\x00"
                 + self._ip(src, dst, 17, udp))
        self._write(frame, dt)

    def tcp(self, src: str, dst: str, sport: int, dport: int, data: bytes,
            seq: int = 1, flags: int = 0x18, dt: float = 0.01) -> None:
        tcp = struct.pack(">HHIIBBHHH", sport, dport, seq, 1, 0x50, flags,
                          8192, 0, 0) + data
        frame = (b"\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x02\x08\x00"
                 + self._ip(src, dst, 6, tcp))
        self._write(frame, dt)


# ------------------------------------------------------------------- BACnet
def bvlc(apdu: bytes, func: int = 0x0A) -> bytes:
    npdu = b"\x01\x04" + apdu
    return struct.pack(">BBH", 0x81, func, 4 + len(npdu)) + npdu


def objid(otype: int, inst: int) -> bytes:
    return struct.pack(">I", (otype << 22) | inst)


def ctx(num: int, data: bytes) -> bytes:
    return bytes([(num << 4) | 0x08 | min(len(data), 5)]) + data


def tpkt(cotp_payload: bytes) -> bytes:
    cotp = b"\x02\xf0\x80" + cotp_payload
    return struct.pack(">BBH", 0x03, 0x00, 4 + len(cotp)) + cotp


def s7_job(pduref: int, param: bytes, data: bytes = b"") -> bytes:
    hdr = struct.pack(">BBHHHH", 0x32, 0x01, 0, pduref, len(param), len(data))
    return tpkt(hdr + param + data)


def s7_ack(pduref: int, param: bytes, data: bytes = b"", err: int = 0) -> bytes:
    hdr = struct.pack(">BBHHHHBB", 0x32, 0x03, 0, pduref, len(param), len(data),
                      (err >> 8) & 0xFF, err & 0xFF)
    return tpkt(hdr + param + data)


def s7_userdata(pduref: int, grp: int, sub: int, data: bytes) -> bytes:
    param = b"\x00\x01\x12\x04\x11" + bytes([(grp & 0x0F) | 0x40, sub, 0x00])
    hdr = struct.pack(">BBHHHH", 0x32, 0x07, 0, pduref, len(param), len(data))
    return tpkt(hdr + param + data)


def mbap(tid: int, unit: int, pdu: bytes) -> bytes:
    return struct.pack(">HHHB", tid, 0, len(pdu) + 1, unit) + pdu


def apdu(payload: bytes) -> bytes:
    return struct.pack(">BB", 0x68, len(payload)) + payload


def i_frame(tx: int, rx: int, asdu: bytes) -> bytes:
    ctrl = struct.pack("<HH", (tx << 1) & 0xFFFE, (rx << 1) & 0xFFFE)
    return apdu(ctrl + asdu)


def asdu(type_id: int, cot: int, ca: int, objects: bytes, num: int = 1,
         sq: bool = False, negative: bool = False) -> bytes:
    vsq = (0x80 if sq else 0) | (num & 0x7F)
    c = cot | (0x40 if negative else 0)
    return struct.pack("<BBBBH", type_id, vsq, c, 0, ca) + objects


def io(ioa: int, payload: bytes) -> bytes:
    return ioa.to_bytes(3, "little") + payload


def dnp3_crc(data: bytes) -> bytes:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA6BC if crc & 1 else crc >> 1
    return struct.pack("<H", (~crc) & 0xFFFF)


def dnp3_frame(src: int, dst: int, app: bytes) -> bytes:
    body = b"\xc0" + app                     # transport header FIR|FIN seq 0
    ln = 5 + len(body)
    head = b"\x05\x64" + bytes([ln, 0xC4]) + struct.pack("<HH", dst, src)
    out = head + dnp3_crc(head)
    for i in range(0, len(body), 16):
        chunk = body[i:i + 16]
        out += chunk + dnp3_crc(chunk)
    return out
