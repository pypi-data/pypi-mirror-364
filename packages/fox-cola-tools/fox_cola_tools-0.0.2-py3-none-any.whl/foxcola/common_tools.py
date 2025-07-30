from datetime import datetime
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.backends import default_backend

from conf import CUSTOM_KEY as custom_key
from conf import CUSTOM_IV as custom_iv


backend = default_backend()


class CommonTools:
    # datetime.datetime 转换成 时间戳
    @staticmethod
    def datetime_conversion_timestamp(time: datetime) -> datetime.timestamp:
        """
        :type time: datetime
        :return: <class 'int'>
        """
        return int(time.timestamp())

    # 时间格式字符串 转换成 datetime.datetime
    @staticmethod
    def time_str_conversion_datetime(time_str: str) -> datetime:
        """
        :type time_str: str
        :param time_str: 2025-06-15 00:00:00
        :return: <class 'datetime.datetime'>
        """
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    # 时间戳 转换成 时间格式字符串
    @staticmethod
    def timestamp_conversion_time_str(timestamp: datetime.timestamp) -> str:
        """
        :type timestamp: datetime.timestamp
        :param timestamp:
        :return: <class 'str'>
        """
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # 时间戳 转换为指定时区的 时间格式字符串
    @staticmethod
    def get_timestamp(zone_str: str, timestamp: datetime.timestamp) -> str:
        """
        :param timestamp: datetime.timestamp
        :type zone_str: str
        :param zone_str: 指定的时区 Asia/Shanghai
        :return: <class 'str'>
        """
        zone = ZoneInfo(zone_str)
        return datetime.fromtimestamp(timestamp, tz=zone).strftime('%Y-%m-%d %H:%M:%S')

    # 密钥派生函数（确保任意长度的字符串都能生成32字节密钥）
    @classmethod
    def derive_key(cls, key_str: str, salt: bytes = b'') -> bytes:
        """将任意字符串转换为32字节AES密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )
        return kdf.derive(key_str.encode('utf-8'))

    # 处理IV（确保任意长度的字符串都能生成16字节IV）
    @classmethod
    def process_iv(cls, iv_str: str) -> bytes:
        """将字符串转换为16字节IV"""
        # 使用SHA256哈希并截取前16字节
        digest = hashes.Hash(hashes.SHA256(), backend=backend)
        digest.update(iv_str.encode('utf-8'))
        return digest.finalize()[:16]

    # 加密函数 - 返回无填充的Base64字符串
    @classmethod
    def encrypt(cls, data: str) -> str:
        key = cls.derive_key(custom_key)
        iv = cls.process_iv(custom_iv)

        # 填充数据
        adder = padding.PKCS7(128).padder()
        padded_data = adder.update(data.encode('utf-8')) + adder.finalize()

        # 加密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded_data) + encryptor.finalize()

        # URL安全的Base64编码并移除填充字符'='
        base64_str = urlsafe_b64encode(ct).decode('utf-8')
        return base64_str.rstrip('=')

    # 解密函数 - 处理无填充的Base64字符串
    @classmethod
    def decrypt(cls, encrypted_data: str) -> str:
        key = cls.derive_key(custom_key)
        iv = cls.process_iv(custom_iv)

        # 添加Base64填充字符（如果需要）
        missing_padding = len(encrypted_data) % 4
        if missing_padding:
            encrypted_data += '=' * (4 - missing_padding)

        # 解码Base64
        ct = urlsafe_b64decode(encrypted_data)

        # 解密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decrypt = cipher.decryptor()
        pt = decrypt.update(ct) + decrypt.finalize()

        # 去除填充
        unparsed = padding.PKCS7(128).unpadder()
        data = unparsed.update(pt) + unparsed.finalize()

        return data.decode('utf-8')
