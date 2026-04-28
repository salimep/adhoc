# installig IBM MQ-HA on Kubernetes cluster

# pre-requests
- nfs storageclass (i have configured storage using democratic-csi with TrueNas)
- metalb Load Balancer (optional, if you wan externel access to MQ servers)
## add ibm-mq helm repo 

```
helm repo add ibm-charts https://raw.githubusercontent.com/IBM/charts/master/repo/stable/
```
update
```
helm repo update
```
extract  varibile which we can define during the installer
```
helm show values ibm-mq/ibm-mq > mq-val.yml
```
example(which i used for the single pod deployment)

about SDR channel SSL termination will cover later


```
# 1. License and Image
license: "accept"

image:
  repository: icr.io/ibm-messaging/mq
  tag: 9.4.2.0-r1
  pullPolicy: IfNotPresent
  pullSecret:
  disableDefaultPullSecret: true

# 2. Persistence - using exact chart schema keys
persistence:
  dataPVC:
    enable: true
    name: "data"
    size: 5Gi
    storageClassName: "freenas-iscsi-csi"

  logPVC:
    enable: true
    name: "log"
    size: 2Gi
    storageClassName: "freenas-iscsi-csi"

  qmPVC:
    enable: true
    name: "qm"
    size: 5Gi
    storageClassName: "freenas-iscsi-csi"

# 3. Queue Manager
queueManager:
  name: "PRODQM02"
  multiinstance:
    enable: false         # exact key: multiinstance.enable (not multiInstance)
  nativeha:
    enable: true
  terminationGracePeriodSeconds: 30
  updateStrategy: RollingUpdate
  envVariables: []
  mqscConfigMaps: []
  mqscSecrets: []
  qminiConfigMaps: []
  qminiSecrets: []

# 4. Resource Management
resources:
  limits:
    cpu: "2"
    memory: "1Gi"
  requests:
    cpu: "500m"
    memory: "1Gi"

# 5. Security Context - exact chart schema keys
security:
  context:
    fsGroup: 0
    supplementalGroups: []
    seccompProfile:
      type:
  initVolumeAsRoot: false
  runAsUser: 1001
  readOnlyRootFilesystem: false

# 6. Anti-Affinity (pods on different nodes)
affinity:
  nodeAffinity:
    matchExpressions: []

topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: "kubernetes.io/hostname"
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app.kubernetes.io/instance: qm2

# 7. Probes
livenessProbe:
  initialDelaySeconds: 300
  periodSeconds: 100
  timeoutSeconds: 50
  failureThreshold: 30

readinessProbe:
  initialDelaySeconds: 100
  periodSeconds: 50
  timeoutSeconds: 30
  failureThreshold: 10

startupProbe:
  timeoutSeconds: 5
  periodSeconds: 5
  successThreshold: 1
  failureThreshold: 24

# 8. Logging
log:
  format: json
  debug: false

# 9. Metrics
metrics:
  enabled: true

# 10. Routing (disabled unless needed)
route:
  nodePort:
    webconsole: false
    mqtraffic: false
    hacrrtraffic: false
  loadBalancer:
    webconsole: false
    mqtraffic: false

tolerations: []
~                     
```
install the ibm mq using helm

Make sure below secret and configmap created  before you install it

```
[vagrant@kube-master ~]$ k get cm/mq-production-config
NAME                   DATA   AGE
mq-production-config   1      41h
[vagrant@kube-master ~]$ k get cm/mq-production-config -o yaml|kubectl-neat 
apiVersion: v1
data:
  config.mqsc: "DEFINE QLOCAL(MY.QUEUE) REPLACE\nDEFINE CHANNEL(MY.SVRCONN) CHLTYPE(SVRCONN)
    TRPTYPE(TCP) REPLACE\nSET CHLAUTH(MY.SVRCONN) TYPE(BLOCKUSER) USERLIST(nobody)\nALTER
    AUTHINFO(SYSTEM.DEFAULT.AUTH.INFO.IDPWOS) AUTHTYPE(IDPWOS) CHCKCLNT(REQUIRED)\nREFRESH
    SECURITY TYPE(CONNAUTH)\nREFRESH SECURITY TYPE(SSL) \n"
kind: ConfigMap
metadata:
  name: mq-production-config
  namespace: ibm-mq
[vagrant@kube-master ~]$ vim mq.yml
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ k get secret
NAME                                TYPE                 DATA   AGE
mq-ssl-kydb                         Opaque               3      39h
mq-ssl-secret                       Opaque               3      41h
my-cluster-secrets                  Opaque               1      41h
prodqm1-ssl-secret                  kubernetes.io/tls    3      36h
sh.helm.release.v1.ibm-mq-prod.v1   helm.sh/release.v1   1      35h
[vagrant@kube-master ~]$ k get secret/prodqm1-ssl-secret -o yaml|kubectl-neat 
apiVersion: v1
data:
  ca.crt: LS0tLS1CRUdJTiBDRVbknWmFQY0JmRUxSaXg23KR1JkY3FhWllSRmhZCmxKdXZUVG9KdVZTeldVOVhiNmlNCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
  tls.crt: LS0tLS1CRUs5U3p2WnN1Q1UvK2dDaWgKRlMVp1FekhWNkVoM3p1NWxtdzd0enlZSVN1MkEyODc3OG9jPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
  tls.key: LrNlhBZTZueFFSVExyUGdWw1UmxvKytseGNBRXpCYlEvSkQKT3l1eXNQTkVsRmFBbTlwa0tkMVpQV3dYYXc9PQotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCg==
kind: Secret
metadata:
  name: prodqm1-ssl-secret
  namespace: ibm-mq
type: kubernetes.io/tls
[vagrant@kube-master ~]$ 


```
install it on  k8s cluster

```
helm install ibm-mq-prod ibm-mq/ibm-mq   -f mq.yml   --namespace ibm-mq
```

ant@kube-master ~]$ 
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ k get po
NAME            READY   STATUS    RESTARTS        AGE
ibm-mq-prod-0   1/1     Running   3 (3h46m ago)   35h
[vagrant@kube-master ~]$ k get po/ibm-mq-prod-0 -o jsonpath='{.spec.containers[*].name}'
qmgr[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ k get po/ibm-mq-prod-0 -o jsonpath='{.spec.containers[*].name}'
qmgr[vagrant@kube-master k get po/ibm-mq-prod-0 -o jsonpath='{.spec.initContainers[*].name}'
qmgr-init[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ k exec -it ibm-mq-prod-0 -- bash
Defaulted container "qmgr" out of: qmgr, qmgr-init (init)
bash-5.1$ dspmq  
QMNAME(PRODQM1)                                           STATUS(Running)
bash-5.1$ ps -ef |grep TCP
888          928     791  0 03:47 ?        00:00:01 /opt/mqm/bin/runmqlsr -r -m PRODQM1 -t TCP -p 1414
888        41405   41354  0 06:26 pts/0    00:00:00 grep TCP
bash-5.1$ exit
exit
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ k logs ibm-mq-prod-0 -c qmgr -f

```