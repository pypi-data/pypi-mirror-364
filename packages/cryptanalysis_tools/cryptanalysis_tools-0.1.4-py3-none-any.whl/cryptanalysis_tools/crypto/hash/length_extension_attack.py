# https://en.wikipedia.org/wiki/Merkle%E2%80%93Damg%C3%A5rd_construction#Security_characteristics
# https://en.wikipedia.org/wiki/Length_extension_attack

# Given the hash H(X) of an unknown input X, it is easy to find the value of H(Pad(X) || Y), where Pad is the padding function of the hash.

import math
from struct import pack, unpack

from . import sm3


def sm3_attack(secret_length: int, secret_digest: bytes, additional_data: bytes) -> bytes:
    # to calculate the hash of Pad(X) || Y, we need to know the length of X
    # and the digest of Pad(X) is the same as v_i which is the previous block of the hash
    # so we can use the sm3.CF function to calculate final hash value
    # we need to construct the additional_data padding

    additional_data_block = sm3.padding(additional_data)
    construct_B_for_additional_data_block = (
        additional_data_block[:-8]
        + (len(additional_data) * 8 + math.ceil(secret_length / 64) * 512).to_bytes(length=8)
    )

    msg_bytes = construct_B_for_additional_data_block

    group_count = round(len(msg_bytes) / 64)

    B = [msg_bytes[i : i + 64] for i in range(0, len(msg_bytes), 64)]

    previous_V_i = list(unpack(">8I", secret_digest))
    for i in range(0, group_count):
        previous_V_i = sm3.CF(previous_V_i, B[i])

    result = pack(">8I", *previous_V_i)
    # this hash value === sm3.hash(pad(secret)||additional_data)
    return result
