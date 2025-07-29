#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__version__ = (0, 0, 3)
__all__ = ["encode", "signature", "make_signed_headers"]
__license__ = "GPLv3 <https://www.gnu.org/licenses/gpl-3.0.txt>"

from collections.abc import Buffer, ItemsView, Iterable, Mapping
from itertools import pairwise
from typing import Self
from urllib.parse import urlencode


def u32_truncate(n: int, /) -> int:
    "把数字转换为 unsigned int 32 bit，并去掉溢出的位"
    return n & ((1 << 32) - 1)


def i32_truncate(n: int, /) -> int:
    "把数字转换为 signed int 32 bit，并去掉溢出的位"
    n &= (1 << 32) - 1
    if n >= 1 << (32 - 1):
        n -= (1 << 32)
    return n


class i32(int):
    """把数字当作 signed int 32 bit 进行操作
    """
    def __new__(cls, n, /):
        if not isinstance(n, int) or isinstance(n, i32):
            return n
        return super().__new__(cls, n)

    def __abs__(self, /):
        if self < 0:
            return -self
        else:
            return self

    def __add__(self, other, /):
        return type(self)(super().__add__(other))

    def __and__(self, other, /):
        return type(self)(i32_truncate(super().__and__(other)))

    def __ceil__(self, /):
        return self

    def __divmod__(self, other, /):
        q, r = super().__divmod__(other)
        return type(self)(q), type(self)(r)

    def __floor__(self, /):
        return self

    def __floordiv__(self, other, /):
        return type(self)(super().__floordiv__(other))

    def __invert__(self, /):
        return type(self)(i32_truncate(super().__invert__()))

    def __lshift__(self, offset, /):
        return type(self)(i32_truncate(super().__lshift__(offset)))

    def __mod__(self, other, /):
        return type(self)(super().__mod__(other))

    def __mul__(self, other, /):
        return type(self)(super().__mul__(other))

    def __neg__(self, /):
        return type(self)(super().__neg__())

    def __or__(self, other, /):
        return type(self)(i32_truncate(super().__or__(other)))

    def __pos__(self, /):
        return self

    def __pow__(self, n, /): # type: ignore
        r = super().__pow__(n)
        if isinstance(r, int):
            return type(self)(r)
        return r

    def __round__(self, n=0, /) -> Self:
        return self

    def __rshift__(self, offset, /):
        return type(self)(i32_truncate(super().__rshift__(offset)))

    def __sub__(self, other, /):
        return type(self)(super().__sub__(other))

    def __trunc__(self, /):
        return self

    def __xor__(self, other, /):
        return type(self)(super().__xor__(other))

    __radd__ = __add__
    __rand__ = __and__
    __rmul__ = __mul__
    __ror__ = __or__
    __rxor__ = __xor__

    def rshift(self, offset=0, /):
        """无符号右移位运算符
        """
        return type(self)((int(self) & 0xFFFFFFFF) >> offset)

    def truncate(self, /):
        return type(self)(i32_truncate(int(self)))


# NOTE: i32 下的 0
_0 = i32(0)

from_bytes = int.from_bytes
to_bytes = int.to_bytes


def i32_list_ensure_index(ls: list[i32], idx: int, /):
    "确保 i32 列表的索引值可用（即至少长度为 ``idx+1``，不足的用 ``i32(0)`` 填充）"
    ln = len(ls)
    if ln == idx:
        ls.append(_0)
    elif ln < idx:
        ls += (_0,) * (idx + 1 - ln)


def i32_list_ensure_get(ls: list[i32], idx: int, /):
    "确保 i32 列表的索引值能返回值，如果长度不够，直接返回 ``i32(0)``"
    try:
        return ls[idx]
    except IndexError:
        return _0


def bytes_to_words(b: Buffer, /) -> list[i32]:
    "把字节数组转换为 i32 列表"
    if not isinstance(b, (bytes, bytearray, memoryview)):
        b = memoryview(b)
    ls = [
        i32(from_bytes(b[i:j], signed=True))
        for i, j in pairwise(range(0, len(b) + 4, 4))
    ]
    if b and (r := len(b) % 4):
        ls[-1] <<= (4 - r) << 3
    return ls


def words_to_bytes(ls: list[i32]) -> bytearray:
    "把 i32 列表转换为字节数组"
    b = bytearray()
    for i in ls:
        b += to_bytes(i.truncate(), 4, signed=True)
    return b


def rotl(i: i32, offset: int, /) -> i32:
    "左旋转 rotate left，即对数字进行循环左移"
    return i << offset | i.rshift(32 - offset)


def endian(ls: list[i32], /) -> list[i32]:
    "改变 i32 列表中每个数字的字节序，big -> little"
    return [
        #rotl(i, 8) & 0xff00ff | rotl(i, 24) & 0xff00ff00
        i32(from_bytes(to_bytes(i, 4), "little"))
        for i in ls
    ]


def encode(data: Buffer | str, /) -> bytearray:
    "用数据计算签名"
    def p(e, t, n, r, i, o, a, /):
        u = e + (t & n | ~t & r) + i.rshift(0) + a
        return (u << o | u.rshift(32 - o)) + t
    def v(e, t, n, r, i, o, a, /):
        u = e + (t & r | n & ~r) + i.rshift(0) + a
        return (u << o | u.rshift(32 - o)) + t
    def m(e, t, n, r, i, o, a, /):
        u = e + (t ^ n ^ r) + i.rshift(0) + a
        return (u << o | u.rshift(32 - o)) + t
    def y(e, t, n, r, i, o, a, /):
        u = e + (n ^ (t | ~r)) + i.rshift(0) + a
        return (u << o | u.rshift(32 - o)) + t
    if isinstance(data, str):
        data = bytes(data, "utf-8")
    elif not isinstance(data, (bytes, bytearray, memoryview)):
        data = memoryview(data)
    u = bytes_to_words(data)
    c = i32(len(data)) << 3
    s = i32(1732584193)
    l = i32(-271733879)
    f = i32(-1732584194)
    d = i32(271733878)
    for h in range(len(u)):
        u[h] = 16711935 & (u[h] << 8 | u[h].rshift(24)) | 4278255360 & (u[h] << 24 | u[h].rshift(8))
    idx = c.rshift(5)
    i32_list_ensure_index(u, idx)
    u[idx] |= i32(128) << c % 32
    idx = 14 + ((c + 64).rshift(9) << 4)
    i32_list_ensure_index(u, idx)
    u[idx] = c
    for h in map(i32, range(0, len(u), 16)):
        b = s
        g = l
        _ = f
        w = d
        s = p(s, l, f, d, i32_list_ensure_get(u, h + 0), i32(7), i32(-680876936))
        d = p(d, s, l, f, i32_list_ensure_get(u, h + 1), i32(12), i32(-389564586))
        f = p(f, d, s, l, i32_list_ensure_get(u, h + 2), i32(17), i32(606105819))
        l = p(l, f, d, s, i32_list_ensure_get(u, h + 3), i32(22), i32(-1044525330))
        s = p(s, l, f, d, i32_list_ensure_get(u, h + 4), i32(7), i32(-176418897))
        d = p(d, s, l, f, i32_list_ensure_get(u, h + 5), i32(12), i32(1200080426))
        f = p(f, d, s, l, i32_list_ensure_get(u, h + 6), i32(17), i32(-1473231341))
        l = p(l, f, d, s, i32_list_ensure_get(u, h + 7), i32(22), i32(-45705983))
        s = p(s, l, f, d, i32_list_ensure_get(u, h + 8), i32(7), i32(1770035416))
        d = p(d, s, l, f, i32_list_ensure_get(u, h + 9), i32(12), i32(-1958414417))
        f = p(f, d, s, l, i32_list_ensure_get(u, h + 10), i32(17), i32(-42063))
        l = p(l, f, d, s, i32_list_ensure_get(u, h + 11), i32(22), i32(-1990404162))
        s = p(s, l, f, d, i32_list_ensure_get(u, h + 12), i32(7), i32(1804603682))
        d = p(d, s, l, f, i32_list_ensure_get(u, h + 13), i32(12), i32(-40341101))
        f = p(f, d, s, l, i32_list_ensure_get(u, h + 14), i32(17), i32(-1502002290))
        l = p(l, f, d, s, i32_list_ensure_get(u, h + 15), i32(22), i32(1236535329))
        s = v(s, l, f, d, i32_list_ensure_get(u, h + 1), i32(5), i32(-165796510))
        d = v(d, s, l, f, i32_list_ensure_get(u, h + 6), i32(9), i32(-1069501632))
        f = v(f, d, s, l, i32_list_ensure_get(u, h + 11), i32(14), i32(643717713))
        l = v(l, f, d, s, i32_list_ensure_get(u, h + 0), i32(20), i32(-373897302))
        s = v(s, l, f, d, i32_list_ensure_get(u, h + 5), i32(5), i32(-701558691))
        d = v(d, s, l, f, i32_list_ensure_get(u, h + 10), i32(9), i32(38016083))
        f = v(f, d, s, l, i32_list_ensure_get(u, h + 15), i32(14), i32(-660478335))
        l = v(l, f, d, s, i32_list_ensure_get(u, h + 4), i32(20), i32(-405537848))
        s = v(s, l, f, d, i32_list_ensure_get(u, h + 9), i32(5), i32(568446438))
        d = v(d, s, l, f, i32_list_ensure_get(u, h + 14), i32(9), i32(-1019803690))
        f = v(f, d, s, l, i32_list_ensure_get(u, h + 3), i32(14), i32(-187363961))
        l = v(l, f, d, s, i32_list_ensure_get(u, h + 8), i32(20), i32(1163531501))
        s = v(s, l, f, d, i32_list_ensure_get(u, h + 13), i32(5), i32(-1444681467))
        d = v(d, s, l, f, i32_list_ensure_get(u, h + 2), i32(9), i32(-51403784))
        f = v(f, d, s, l, i32_list_ensure_get(u, h + 7), i32(14), i32(1735328473))
        l = v(l, f, d, s, i32_list_ensure_get(u, h + 12), i32(20), i32(-1926607734))
        s = m(s, l, f, d, i32_list_ensure_get(u, h + 5), i32(4), i32(-378558))
        d = m(d, s, l, f, i32_list_ensure_get(u, h + 8), i32(11), i32(-2022574463))
        f = m(f, d, s, l, i32_list_ensure_get(u, h + 11), i32(16), i32(1839030562))
        l = m(l, f, d, s, i32_list_ensure_get(u, h + 14), i32(23), i32(-35309556))
        s = m(s, l, f, d, i32_list_ensure_get(u, h + 1), i32(4), i32(-1530992060))
        d = m(d, s, l, f, i32_list_ensure_get(u, h + 4), i32(11), i32(1272893353))
        f = m(f, d, s, l, i32_list_ensure_get(u, h + 7), i32(16), i32(-155497632))
        l = m(l, f, d, s, i32_list_ensure_get(u, h + 10), i32(23), i32(-1094730640))
        s = m(s, l, f, d, i32_list_ensure_get(u, h + 13), i32(4), i32(681279174))
        d = m(d, s, l, f, i32_list_ensure_get(u, h + 0), i32(11), i32(-358537222))
        f = m(f, d, s, l, i32_list_ensure_get(u, h + 3), i32(16), i32(-722521979))
        l = m(l, f, d, s, i32_list_ensure_get(u, h + 6), i32(23), i32(76029189))
        s = m(s, l, f, d, i32_list_ensure_get(u, h + 9), i32(4), i32(-640364487))
        d = m(d, s, l, f, i32_list_ensure_get(u, h + 12), i32(11), i32(-421815835))
        f = m(f, d, s, l, i32_list_ensure_get(u, h + 15), i32(16), i32(530742520))
        l = m(l, f, d, s, i32_list_ensure_get(u, h + 2), i32(23), i32(-995338651))
        s = y(s, l, f, d, i32_list_ensure_get(u, h + 0), i32(6), i32(-198630844))
        d = y(d, s, l, f, i32_list_ensure_get(u, h + 7), i32(10), i32(1126891415))
        f = y(f, d, s, l, i32_list_ensure_get(u, h + 14), i32(15), i32(-1416354905))
        l = y(l, f, d, s, i32_list_ensure_get(u, h + 5), i32(21), i32(-57434055))
        s = y(s, l, f, d, i32_list_ensure_get(u, h + 12), i32(6), i32(1700485571))
        d = y(d, s, l, f, i32_list_ensure_get(u, h + 3), i32(10), i32(-1894986606))
        f = y(f, d, s, l, i32_list_ensure_get(u, h + 10), i32(15), i32(-1051523))
        l = y(l, f, d, s, i32_list_ensure_get(u, h + 1), i32(21), i32(-2054922799))
        s = y(s, l, f, d, i32_list_ensure_get(u, h + 8), i32(6), i32(1873313359))
        d = y(d, s, l, f, i32_list_ensure_get(u, h + 15), i32(10), i32(-30611744))
        f = y(f, d, s, l, i32_list_ensure_get(u, h + 6), i32(15), i32(-1560198380))
        l = y(l, f, d, s, i32_list_ensure_get(u, h + 13), i32(21), i32(1309151649))
        s = y(s, l, f, d, i32_list_ensure_get(u, h + 4), i32(6), i32(-145523070))
        d = y(d, s, l, f, i32_list_ensure_get(u, h + 11), i32(10), i32(-1120210379))
        f = y(f, d, s, l, i32_list_ensure_get(u, h + 2), i32(15), i32(718787259))
        l = y(l, f, d, s, i32_list_ensure_get(u, h + 9), i32(21), i32(-343485551))
        s = (s + b).rshift(0)
        l = (l + g).rshift(0)
        f = (f + _).rshift(0)
        d = (d + w).rshift(0)
    return words_to_bytes(endian([s, l, f, d]))


def signature(
    payload: ( Buffer | str | Mapping[str, str] | Mapping[bytes, bytes] | 
               Iterable[tuple[str, str]] | Iterable[tuple[bytes, bytes]] ), 
    /, 
) -> str:
    "用请求参数计算签名，最后返回 16 进制表示"
    if not isinstance(payload, (Buffer, str)):
        if isinstance(payload, Mapping):
            params: list = list(ItemsView(payload))
        elif isinstance(payload, list):
            params = payload
        else:
            params = list(payload)
        params.sort()
        payload = urlencode(params)
    return encode(payload).hex()


def make_signed_headers(
    auth_headers: str | Mapping[str, str] | Iterable[tuple[str, str]], 
    payload: None | Mapping[str, str] = None, 
    headers: None | Mapping[str, str] | Iterable[tuple[str, str]] = None, 
) -> dict[str, str]:
    """制作携带签名的请求头

    :param auth_headers: 请求头中和产生签名有关的字段（大小写敏感），如果为 str，则视为 "AccessToken"
    :param payload: 请求参数
    :param headers: 其它的请求头字段

    :return: 加上签名的请求头字典
    """
    if isinstance(auth_headers, str):
        auth_headers = {"AccessToken": auth_headers}
    else:
        auth_headers = dict(auth_headers)
    auth_headers["Timestamp"] = auth_headers.get("Timestamp") or "0"
    return dict(
        headers or (), 
        **auth_headers, 
        **{
            "Sign-Type": "1", 
            "Signature": signature({
                **auth_headers, 
                **(payload or {}), 
            }), 
        }, 
    )

