from __future__ import annotations

import base64
import math
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class Griffinere:
    key: str
    alphabet: str | None = None

    _alphabet: List[str] = field(init=False, repr=False)
    _alphabet_length: int = field(init=False, repr=False)
    _alphabet_position_map: Dict[str, int] = field(init=False, repr=False)
    _key_chars: List[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        default_alphabet = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
        )
        alphabet_str = self.alphabet or default_alphabet
        self._alphabet = self._validate_alphabet(alphabet_str, self.key)
        self._alphabet_length = len(self._alphabet)
        self._alphabet_position_map = {ch: idx for idx, ch in enumerate(self._alphabet)}
        self._key_chars = list(self.key)

    def encrypt_string(self, plain_text: str, minimum_response_length: int | None = None) -> str:
        if not plain_text or plain_text.isspace():
            return ""
        if minimum_response_length is None:
            return self._encrypt_segments(plain_text)
        if minimum_response_length < 1:
            raise ValueError("minimum_response_length must be greater than zero")
        need_to_add = minimum_response_length - len(plain_text)
        if need_to_add <= 0:
            return self._encrypt_segments(plain_text)
        pull_from_front = math.ceil(need_to_add / 1.25)
        pull_from_back = need_to_add - pull_from_front
        contiguous = plain_text.replace(" ", "") or plain_text
        string_to_front = self._cycle_take(contiguous, pull_from_front, True)
        string_to_back = self._cycle_take(contiguous, pull_from_back, False)
        fragments_front = f"{self._encrypt_segments(string_to_front[::-1])}." if string_to_front else ""
        fragments_back = f".{self._encrypt_segments(string_to_back)}" if string_to_back else ""
        core = self._encrypt_segments(plain_text)
        return f"{fragments_front}{core}{fragments_back}"

    def decrypt_string(self, cipher_text: str) -> str:
        if not cipher_text or cipher_text.isspace():
            return ""
        if "." in cipher_text:
            parts = cipher_text.split(".")
            if len(parts) > 2:
                cipher_text = parts[1]
        return self._decrypt_segments(cipher_text)

    @staticmethod
    def _validate_alphabet(alphabet: str, key: str) -> List[str]:
        if "." in alphabet:
            raise ValueError("Alphabet must not contain '.'")
        unique: List[str] = []
        seen = set()
        for ch in alphabet:
            if ch in seen:
                raise ValueError(f"Duplicate character '{ch}' in provided alphabet.")
            seen.add(ch)
            unique.append(ch)
        for ch in key:
            if ch not in seen:
                raise ValueError(f"Alphabet does not contain the character '{ch}' supplied in the key.")
        return unique

    @staticmethod
    def _cycle_take(source: str, count: int, front: bool) -> str:
        if count <= 0 or not source:
            return ""
        result: List[str] = []
        length = len(source)
        idx = 0
        while len(result) < count:
            result.append(source[idx % length] if front else source[-1 - (idx % length)])
            idx += 1
        return "".join(result)

    def _encrypt_segments(self, text: str) -> str:
        return " ".join(self._encrypt_word(word) if word else "" for word in text.split(" "))

    def _decrypt_segments(self, text: str) -> str:
        return " ".join(self._decrypt_word(word) if word else "" for word in text.split(" "))

    def _encrypt_word(self, word: str) -> str:
        segment_chars = self._to_base64_char_list(word)
        key_chars = self._get_key(segment_chars)
        encrypted = [self._shift_positive(kc, sc) for kc, sc in zip(key_chars, segment_chars)]
        return "".join(encrypted)

    def _decrypt_word(self, word: str) -> str:
        segment_chars = list(word)
        key_chars = self._get_key(segment_chars)
        decrypted = [self._shift_negative(kc, sc) for kc, sc in zip(key_chars, segment_chars)]
        return self._from_base64_char_list(decrypted)

    def _shift_positive(self, key_char: str, text_char: str) -> str:
        key_pos = self._alphabet_position_map.get(key_char)
        text_pos = self._alphabet_position_map.get(text_char)
        if key_pos is None or text_pos is None:
            return text_char
        return self._alphabet[(key_pos + text_pos) % self._alphabet_length]

    def _shift_negative(self, key_char: str, text_char: str) -> str:
        key_pos = self._alphabet_position_map.get(key_char)
        text_pos = self._alphabet_position_map.get(text_char)
        if key_pos is None or text_pos is None:
            return text_char
        return self._alphabet[(text_pos - key_pos + self._alphabet_length) % self._alphabet_length]

    def _get_key(self, segment: List[str]) -> List[str]:
        if not segment:
            return []
        key = list(self._key_chars)
        while len(key) < len(segment):
            key.extend(self._key_chars)
        return key[: len(segment)]

    @staticmethod
    def _to_base64_char_list(text: str) -> List[str]:
        if text is None:
            raise ValueError("text cannot be None")
        if text == "":
            return []
        encoded = base64.b64encode(text.encode()).decode().rstrip("=")
        return list(encoded)

    @staticmethod
    def _from_base64_char_list(chars: List[str]) -> str:
        if not chars:
            return ""
        encoded = "".join(chars)
        padding_needed = (-len(encoded)) % 4
        encoded += "=" * padding_needed
        decoded_bytes = base64.b64decode(encoded)
        return decoded_bytes.decode()
