from typing import Any


def encode(value: Any):
    return '#'.join(["%s$%s" % (k, v) for k, v in value.items()])
    # return json.dumps(value)


def decode(encoded: str):
    return {
        part.split("$")[0]: part.split("$")[1] for part in encoded.split("#")
    }
    # return json.loads(encoded)
