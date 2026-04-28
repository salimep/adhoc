# setup MYSQL cluster on kubernetes

### setup iscsi block storage using TrueNAS(democratic-csi)

True-NasSetup 
1) - generate ssh-keys
```
ssh-keygen -t rsa -C root@truenas.billytech.local -f truenas_rsa
````
   - configure truenas to accomedate sc config
   ![bgp](/images/TrueNAsPool-1.png)
   ![](/images/TrueNAs-2-Iscsi-conf.png)
   ![](/images/Screenshot%202026-04-19%20at%2012.14.41 PM.png)

2) configure worker nodes for iscsi initiators
```
# On Ubuntu/Debian nodes
sudo apt-get update
sudo apt-get install -y open-iscsi lsscsi sg3-utils multipath-tools scsitools

# Start and enable iSCSI service
sudo systemctl enable --now iscsid
sudo systemctl enable --now open-iscsi

# Verify initiator name is set
sudo cat /etc/iscsi/initiatorname.iscsi

# Configure automatic session startup
sudo sed -i 's/node.startup = manual/node.startup = automatic/' /etc/iscsi/iscsid.conf
sudo systemctl restart iscsid
```
2) Configure Kubernetes democratic-csi
```
helm repo add democratic-csi https://democratic-csi.github.io/charts/
helm repo update
helm search repo democratic-csi/
```
3) Configure Helm Values File
```
# democratic-csi-values.yaml
csiDriver:
  name: "org.democratic-csi.iscsi"

storageClasses:
  - name: freenas-iscsi-csi
    defaultClass: false
    reclaimPolicy: Delete
    volumeBindingMode: Immediate
    allowVolumeExpansion: true
    parameters:
      fsType: ext4
    mountOptions: []

driver:
  config:
    driver: freenas-iscsi
    instance_id:
    httpConnection:
      protocol: http
      host: 192.168.8.132
      port: 80
      apiKey: 1-lcsry4HU0PiA3G8SMkUBFU2xCUs6kpOtCD2KYPhaP0y7pcTCUHD10MepCMx4e5GI
      allowInsecure: true
    zfs:
      datasetParentName: k8/scsi/v
      detachedSnapshotsDatasetParentName: k8/scsi/snap
      datasetEnableQuotas: true
      datasetEnableReservation: false
      datasetPermissionsMode: "0770"
      datasetPermissionsUser: 0
      datasetPermissionsGroup: 0
    iscsi:
      targetPortal: "192.168.8.132:3260"
      targetPortals: []
      interface:
      namePrefix: csi-
      nameSuffix: "-cluster"
      targetGroups:
        - targetGroupPortalGroup: 1
          targetGroupInitiatorGroup: 1
          targetGroupAuthType: None
      extentInsecureTpc: true
      extentXenCompat: false
      extentDisablePhysicalBlocksize: true
      extentBlocksize: 512
      extentRpm: "SSD"
      extentAvailThreshold: 0
    sshConnection:
      host: 192.168.8.132
      port: 22
      username: root
      # This is the SSH key that we generated for passwordless authentication
      privateKey: |
           -----BEGIN OPENSSH PRIVATE KEY-----
           b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
           NhAAAAAwEAAQAAAYEA0b4MBS2P4n7miMySqx7PyUFPbieWD
           -----END OPENSSH PRIVATE KEY-----
```
### Install the democratic-csi Helm Chart
```
# Create namespace for CSI driver
kubectl create namespace democratic-csi

# Install Democratic CSI
helm install freenas-iscsi democratic-csi/democratic-csi \
  --namespace democratic-csi \
  --values democratic-csi-values.yaml

# Verify deployment
kubectl get pods -n democratic-csi
kubectl get csidrivers
kubectl get storageclasses
```
### make it default storage class
```
 kubectl patch storageclass freenas-iscsi-csi -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
### deploy metalb operator(Loadbalncer IP provider)
```
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
```
### add IP address pool into it

```

```apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.8.240-192.168.8.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2-adv
  namespace: metallb-system
spec:
  ipAddressPools:
  - first-pool

