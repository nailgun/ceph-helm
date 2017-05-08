# Ceph helm chart

## Cluster requirements

* Kubernetes 1.6 or newer
* [resolv.conf on nodes should contain kube-dns](https://github.com/ceph/ceph-docker/tree/master/examples/kubernetes#skydns-resolution)


## Ceph management

```
$ kubectl -n ceph -it exec $(kubectl -n ceph get pods -l daemon=mon --template='{{ (index .items 0).metadata.name }}') -- bash
```


## Manual testing

```
$ kubectl create -f test
$ curl -sSL https://github.com/nailgun/ceph-helm/raw/master/activate-namespace.sh | bash /dev/stdin -s ceph -t test
$ kubectl -n test exec -it $(kubectl -n test get pods -l run=ceph-test --template='{{ (index .items 0).metadata.name }}') -- sh
$ echo hello > /mnt/ceph/hello
```


## Fine-tuning

1. Make sure `/storage` directory on hosts survive restarts
2. Don’t set `ceph-osd` labels to nodes just after installing. Better to first edit ceph-osd DeamonSet's environment variables to match your setup. Default DaemonSet stores everything in `/storage` directory on host, which may be not what you want. Refer to [ceph-docker readme](https://github.com/ceph/ceph-docker/tree/master/ceph-releases/jewel/ubuntu/14.04/daemon#deploy-an-osd) for other options.
3. Also you may want to run more then one OSD per node (if you have multiple disks). Just copy DaemonSet manifest, rename it and update environment variables. Also you may want to change nodeSelector.
4. Create custom CRUSH map ruleset to match different hosts (some with SSDs, some with HDDs). Create pools using this rulesets and different *pool size*s. Copy StorageClass object with different name and change `parameters.pool` there.
5. Optionally store journalfile on separate drive (`OSD_JOURNAL`).


## Tested scenarios

### OSDs
1. 2 osds, size=2. 
    1. Stopped one osd
    2. PGs became active+undersized+degraded
    3. Restarted osd back
    4. PGs became active+clean
    5. PROFIT
2. 3 osds, size=2.
    1. Stopped one osd
    2. some PGs became active+undersized+degraded, some remain active+clean, 1/3 in osds are down
    3. HEALTH: recovery 85/254 objects degraded (33.465%), too few PGs per OSD (28 < min 30)
    4. After mon_osd_down_out_interval all PGs became active+clean
    5. Restarted osd back
    6. Everything is OK, osd joined the cluster back
    7. PROFIT
3. 3 osds, size=2
    1. Stopped one osd
    2. cluster state become like in test 2
    3. Removed osd from the cluster
    4. State remains active+undersized+degraded
    5. Removed osd from crushmap
    6. Cluster is recovering
    7. Cluster state clean
    8. PROFIT
    9. Restarted osd back
    10. OSD joined the cluster back
    11. But it was not in crushmap
    12. So better is to clear OSD directory before rejoin (see next test)
4. 3 osds, size=2
    1. Stopped one osd
    2. Removed osd from the cluster (http://docs.ceph.com/docs/hammer/rados/operations/add-or-rm-osds/#removing-osds-manual)
    3. Cluster state clean
    4. Cleared OSD directory
    5. Restarted osd back
    6. Cluster is recovering
    7. Cluster state clean
    8. PROFIT

### MONs
Adding, removing MONs works fine without any trouble.

Full shutdown:

1. 3 mons running
    1. Scaled to one
    2. Scaled to zero
    3. Set nodeSelector to last working host
    4. Scaled to one
    5. Cluster is OK
    6. Removed nodeSelector
    7. Scaled back to 3
    8. Cluster is OK
    9. PROFIT
2. 3 mons running
    1. Scaled to zero
    2. Scaled back to 3
    3. Cluster is OK
    4. PROFIT


## Notes
Provided [ceph.conf](ceph/templates/config/configmap.yaml) was last synced with [this upstream ceph.conf](https://github.com/ceph/ceph-docker/blob/ebf36ff/examples/kubernetes/generator/templates/ceph/ceph.conf.tmpl).
