#!/bin/bash

set -e

source_namespace=ceph
target_namespace=ceph

while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--source-namespace)
            source_namespace="$2"
            shift
        ;;
        -t|--target-namespace)
            target_namespace="$2"
            shift
        ;;
        -d|--debug)
            conf_file=/etc/squid/debug.conf
        ;;
        -h|--help)
            echo "-s|--source-namespace: namespace from where to copy the secret"
            echo "-t|--target-namespace: namespace where to copy the secret"
            echo "-h|--help: this help"
            exit 0
        ;;
        *)
            echo "unknown option: $1" >&2
            exit 1
        ;;
    esac

    shift
done

{
  cat <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: rbd-user
type: kubernetes.io/rbd
data:
  key: |
    $(kubectl get secret rbd-user --namespace=${source_namespace} --template='{{ .data.key }}')
EOF
} | kubectl create --namespace ${target_namespace} -f -
