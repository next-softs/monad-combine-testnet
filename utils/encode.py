import binascii


def byte64(text=""):
    text = str(text).replace("0x", "")
    return ("0" * (64 - len(str(text)))) + str(text) if text else "0"*64

def get_data_byte64(func, *args):
    data = str(func)
    for arg in args:
        data += byte64(arg)

    return data

def data_decoder(data):
    try:
        data = data[10:]
        string_length = int(data[64:128], 16)
        error_message = bytes.fromhex(data[128:128 + string_length * 2]).decode("utf-8")

        return error_message

    except:
        pass

    return data


