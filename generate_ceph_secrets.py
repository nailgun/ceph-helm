#!/usr/bin/env python

import os
import time
import base64
import struct


daemon_keyring_templates = {
    'mon':           '[mon.]\n'
                     '  key = {}\n'
                     '  caps mon = "allow *"\n',
    'bootstrap-mds': '[client.bootstrap-mds]\n'
                     '  key = {}\n'
                     '  caps mon = "allow profile bootstrap-mds"\n',
    'bootstrap-osd': '[client.bootstrap-osd]\n'
                     '  key = {}\n'
                     '  caps mon = "allow profile bootstrap-osd"\n',
    'bootstrap-rgw': '[client.bootstrap-rgw]\n'
                     '  key = {}\n'
                     '  caps mon = "allow profile bootstrap-rgw"\n',
}

client_keyring_template = '''
[client.admin]
  key = {admin_key}
  auid = 0
  caps mds = "allow"
  caps mon = "allow *"
  caps osd = "allow *"

[client.user]
  key = {user_key}
  auid = 1
  caps mon = "allow *"
  caps osd = "allow *"
'''

secret_manifest_template = '''---
apiVersion: v1
kind: Secret
metadata:
  name: {name}
type: {type}
data:
  {key}: {value_b64}
'''


def main():
    for name, tpl in daemon_keyring_templates.items():
        key = gen_key()

        secret_name = 'ceph-{}-keyring'.format(name)
        value = tpl.format(key)
        value_b64 = base64.b64encode(value.encode('ascii')).decode('ascii')
        manifest = secret_manifest_template.format(name=secret_name,
                                                   type='Opaque',
                                                   key='keyring',
                                                   value_b64=value_b64)
        print(manifest)

    client_keys = {
        'admin': gen_key(),
        'user': gen_key(),
    }

    secret_name = 'ceph-client-admin-keyring'
    value = client_keyring_template.format(admin_key=client_keys['admin'],
                                           user_key=client_keys['user'])
    value_b64 = base64.b64encode(value.encode('ascii')).decode('ascii')
    manifest = secret_manifest_template.format(name=secret_name,
                                               type='Opaque',
                                               key='keyring',
                                               value_b64=value_b64)
    print(manifest)

    for client_name, key in client_keys.items():
        secret_name = 'rbd-' + client_name
        value_b64 = base64.b64encode(key.encode('ascii')).decode('ascii')
        manifest = secret_manifest_template.format(name=secret_name,
                                                   type='kubernetes.io/rbd',
                                                   key='key',
                                                   value_b64=value_b64)
        print(manifest)


# based on https://github.com/ceph/ceph-docker/blob/master/examples/kubernetes/generator/ceph-key.py
def gen_key(keysize_bytes=16):
    key = os.urandom(keysize_bytes)

    header = struct.pack(
        '<hiih',
        1,                 # le16 type: CEPH_CRYPTO_AES
        int(time.time()),  # le32 created: seconds
        0,                 # le32 created: nanoseconds,
        len(key),          # le16: len(key)
    )

    return base64.b64encode(header + key)


if __name__ == '__main__':
    main()
