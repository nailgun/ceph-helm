#!/usr/bin/env python

import os
import time
import base64
import struct


templates = {
    'client-admin':  '[client.admin]\n'
                     '  key = {}\n'
                     '  auid = 0\n'
                     '  caps mds = "allow"\n'
                     '  caps mon = "allow *"\n'
                     '  caps osd = "allow *"\n',
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


manifest_template = '''---
apiVersion: v1
kind: Secret
metadata:
  name: {name}
type: {type}
data:
  {key}: {value_b64}
'''


def main():
    client_key = gen_key()  # TODO: use different client key for storage (without admin access)

    for name, tpl in templates.items():
        if name == 'client-admin':
            key = client_key
        else:
            key = gen_key()

        name = 'ceph-{}-keyring'.format(name)
        value = tpl.format(key)
        value_b64 = base64.b64encode(value.encode('ascii')).decode('ascii')
        manifest = manifest_template.format(name=name, type='Opaque', key='keyring', value_b64=value_b64)
        print(manifest)

    print(manifest_template.format(name='rbd-admin',
                                   type='kubernetes.io/rbd',
                                   key='key',
                                   value_b64=base64.b64encode(client_key).decode('ascii')))


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
