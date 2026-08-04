import hashlib


def get_device_hash(serial):
  return hashlib.sha256(f'cloudypilot:{serial}'.encode()).hexdigest()

def set_authorized_hash(device_hash, params):
  print("AuthorizedHash not set.")
  print("Correct partial hash found. Setting AuthorizedHash with device serial hash.")
  params.put("AuthorizedHash", device_hash, block=True)

def compare_hashes(device_hash, authorized_hash):
  if (device_hash is not None) and (authorized_hash is not None) and (device_hash == authorized_hash):
    print(f"{device_hash} == {authorized_hash}")
    print("Authorized serial number hash found. Continuing.")
  else:
    print(f"{device_hash} != {authorized_hash}")
    raise RuntimeError("This branch is locked to a specific device. Please install the master branch of cloudypilot instead.")
