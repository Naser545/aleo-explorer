import socket

from .traits import *


class Bech32m:

    def __init__(self, data, prefix):
        if not isinstance(data, bytes):
            raise TypeError("can only initialize type with bytes")
        if not isinstance(prefix, str):
            raise TypeError("only str prefix is supported")
        self.data = data
        self.prefix = prefix

    def __str__(self):
        return aleo.bech32_encode(self.prefix, self.data)

    def __repr__(self):
        return str(self)


class u8(Int):
    size = 1
    min = 0
    max = 255

    def dump(self) -> bytes:
        return struct.pack("<B", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<B", data.read(1))[0])
        return self


class u16(Int):
    size = 2
    min = 0
    max = 65535

    def dump(self) -> bytes:
        return struct.pack("<H", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<H", data.read(2))[0])
        return self


class u32(Int):
    size = 4
    min = 0
    max = 4294967295

    def dump(self) -> bytes:
        return struct.pack("<I", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<I", data.read(4))[0])
        return self


class u64(Int):
    size = 8
    min = 0
    max = 18446744073709551615

    def dump(self) -> bytes:
        return struct.pack("<Q", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<Q", data.read(8))[0])
        return self

# Obviously we only support 64bit
usize = u64

class u128(Int):
    size = 16
    min = 0
    max = 340282366920938463463374607431768211455

    def dump(self) -> bytes:
        return struct.pack("<QQ", self & 0xFFFF_FFFF_FFFF_FFFF, self >> 64)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        lo, hi = struct.unpack("<QQ", data.read(16))
        self = cls((hi << 64) | lo)
        return self


class i8(Int):
    size = 1
    min = -128
    max = 127

    def dump(self) -> bytes:
        return struct.pack("<b", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<b", data.read(1))[0])
        return self


class i16(Int):
    size = 2
    min = -32768
    max = 32767

    def dump(self) -> bytes:
        return struct.pack("<h", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<h", data.read(2))[0])
        return self


class i32(Int):
    size = 4
    min = -2147483648
    max = 2147483647

    def dump(self) -> bytes:
        return struct.pack("<i", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<i", data.read(4))[0])
        return self


class i64(Int):
    size = 8
    min = -9223372036854775808
    max = 9223372036854775807

    def dump(self) -> bytes:
        return struct.pack("<q", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        self = cls(struct.unpack("<q", data.read(8))[0])
        return self


class i128(Int):
    size = 16
    min = -170141183460469231731687303715884105728
    max = 170141183460469231731687303715884105727

    def dump(self) -> bytes:
        return struct.pack("<qq", self & 0xFFFF_FFFF_FFFF_FFFF, self >> 64)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        lo, hi = struct.unpack("<qq", data.read(16))
        self = cls((hi << 64) | lo)
        return self


class bool_(Int):
    # Really don't want to make a proper bool, reusing Int is good enough for most usages

    size = 1

    def __init__(self, value=False):
        if not isinstance(value, bool):
            raise TypeError("value must be bool")
        self.value = value

    def dump(self) -> bytes:
        return struct.pack("<B", self)

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        value = struct.unpack("<B", data.read(1))[0]
        if value == 0:
            value = False
        elif value == 1:
            value = True
        else:
            breakpoint()
            raise ValueError("invalid value for bool")
        self = cls(value)
        return self

    @classmethod
    def loads(cls, data: str):
        if data.lower() == "true":
            return cls(True)
        if data.lower() == "false":
            return cls()
        raise ValueError("invalid value for bool")

    def __str__(self):
        if self:
            return "true"
        return "false"

    def __repr__(self):
        if self:
            return "True"
        return "False"

    def __invert__(self):
        return bool_(not self)

    def __and__(self, other):
        if isinstance(other, bool):
            return bool_(self.value and other)
        return bool_(self.value and other.value)

    def __or__(self, other):
        if isinstance(other, bool):
            return bool_(self.value or other)
        return bool_(self.value or other.value)



class SocketAddr(Deserialize):
    def __init__(self, *, ip: int, port: int):
        if not isinstance(ip, int):
            raise TypeError("ip must be int")
        if not isinstance(port, int):
            raise TypeError("port must be int")
        if ip < 0 or ip > 4294967295:
            raise ValueError("ip must be between 0 and 4294967295")
        if port < 0 or port > 65535:
            raise ValueError("port must be between 0 and 65535")
        self.ip = ip
        self.port = port

    @classmethod
    # @type_check
    def load(cls, data: BytesIO):
        data.read(4)
        ip = u32.load(data)
        port = u16.load(data)
        return cls(ip=ip, port=port)

    def __str__(self):
        return ":".join(self.ip_port())

    def ip_port(self):
        return socket.inet_ntoa(struct.pack('<L', self.ip)), self.port