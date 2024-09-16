from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json
import base64


def calculate_sha256_string(input_string):
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()


# Encode the data
def base64_encode(input_dict):
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')



# Decode the data
def base64_decode(input_string):
    data_bytes = base64.b64decode(input_string)

    json_data = data_bytes.decode('utf-8')
    return json.loads(json_data)