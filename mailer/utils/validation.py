import re

__valid_phone_number_pattern = r"^7\d{10}$"


def is_valid_phone_number(phone: str) -> bool:
    return bool(re.findall(__valid_phone_number_pattern, phone))


def parse_mobile_provider_prefix(phone: str) -> str:
    parsed = re.findall(__valid_phone_number_pattern, phone)
    if parsed:
        return parsed[0][1:4]
