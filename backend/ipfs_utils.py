import ipfshttpclient2
import json
from robonomicsinterface import web_3_auth
from pinatapy import PinataPy

with open('config.json') as config_file:
    config = json.load(config_file)

def upload_file_to_local_node(path: str) -> tuple:
    with ipfshttpclient2.connect() as client:
        res = client.add(path)
    ipfs_hash = res.get("Hash")
    ipfs_size = res.get("Size")
    return ipfs_hash, ipfs_size

def upload_file(path: str) -> tuple:
    try:
        local_hash, local_size = upload_file_to_local_node(path)
    except Exception as e:
        print(f"Exception in pinning to local gateway: {e}")
        local_hash, local_size = None, None
    try:
        usr, pwd = web_3_auth(config["seed"])
        client = ipfshttpclient2.connect(addr=config["ipfs_gateway_addr"], auth=(usr, pwd), session=True, timeout=5)
        res = client.add(path)
        custom_hash, custom_size = res.get('Hash'), res.get('Size')
    except Exception as e:
        print(f"Error uploading to multi agent ipfs: {e}. Retrying...")
        custom_hash, custom_size = None, None
    res_hash = local_hash if local_hash else custom_hash
    res_size = local_size if local_size else custom_size
    return res_hash, res_size

def pin_file(file_path):
    api_key = config["api_key"]
    secret_key = config["secret_key"]
    pinata = PinataPy(api_key, secret_key)
    pinata.pin_file_to_ipfs(path_to_file=file_path)
    print("pinned to pinata")