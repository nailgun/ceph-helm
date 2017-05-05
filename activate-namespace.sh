#!/bin/bash

set -e

kube_namespace=$1

{
  cat <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: rbd-user
type: kubernetes.io/rbd
data:
  key: |
    $(kubectl get secret rbd-admin --namespace=ceph -o json | jq -r '.data | .[]')
EOF
} | kubectl create --namespace ${kube_namespace} -f -
