# installing IBM MQ-HA on k8s cluster

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
extract  variable which we can define during the installer
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


```
helm install ibm-mq-prod ibm-mq/ibm-mq   -f mq-availibilty.yml -n ibm-mq
```
verification part
```
[vagrant@kube-master ~]$ 
[vagrant@kube-master ~]$ k get pod -o wide
NAME           READY   STATUS    RESTARTS      AGE     IP               NODE                            NOMINATED NODE   READINESS GATES
qm2-ibm-mq-0   0/1     Running   6 (27m ago)   5d      10.244.182.43    worker3                         <none>           <none>
qm2-ibm-mq-1   0/1     Running   0             2m13s   10.244.226.116   worker-1                        <none>           <none>
qm2-ibm-mq-2   1/1     Running   5 (27m ago)   5d      10.244.123.1     kube-master.salimonline.local   <none>           <none>
[vagrant@kube-master ~]$ k exec qm2-ibm-mq-2  -- bash -c dspmq
QMNAME(PRODQM02)                                          STATUS(Running)
[vagrant@kube-master ~]$ k exec qm2-ibm-mq-1  -- bash -c dspmq
QMNAME(PRODQM02)                                          STATUS(Replica)
[vagrant@kube-master ~]$ k exec qm2-ibm-mq-0  -- bash -c dspmq
QMNAME(PRODQM02)                                          STATUS(Replica)
[vagrant@kube-master ~]$ k get svc
NAME                          TYPE           CLUSTER-IP       EXTERNAL-IP     PORT(S)                         AGE
qm2-ibm-mq                    LoadBalancer   10.109.114.214   192.168.8.243   9443:30606/TCP,1414:30102/TCP   5d
qm2-ibm-mq-metrics            ClusterIP      10.104.230.71    <none>          9157/TCP                        5d
qm2-ibm-mq-metrics-headless   ClusterIP      None             <none>          9157/TCP                        47h
qm2-ibm-mq-replica-0          ClusterIP      10.110.59.214    <none>          9414/TCP                        5d
qm2-ibm-mq-replica-1          ClusterIP      10.99.40.17      <none>          9414/TCP                        5d
qm2-ibm-mq-replica-2          ClusterIP      10.97.160.184    <none>          9414/TCP                        5d
qm2-mq-metrics                ClusterIP      10.96.77.3       <none>          9157/TCP                        4d9h
[vagrant@kube-master ~]$ k get eo
error: the server doesn't have a resource type "eo"
[vagrant@kube-master ~]$ k get ep
NAME                          ENDPOINTS                                                  AGE
qm2-ibm-mq                    10.244.123.1:9443,10.244.123.1:1414                        5d
qm2-ibm-mq-metrics            10.244.123.1:9157                                          5d
qm2-ibm-mq-metrics-headless   10.244.123.1:9157,10.244.182.43:9157,10.244.226.116:9157   47h
qm2-ibm-mq-replica-0          10.244.182.43:9414                                         5d
qm2-ibm-mq-replica-1          10.244.226.116:9414                                        5d
qm2-ibm-mq-replica-2          10.244.123.1:9414                                          5d
qm2-mq-metrics                10.244.123.1:9157                                          4d9h
[vagrant@kube-master ~]$ 

[vagrant@kube-master ~]$  helm list -A
NAME         	NAMESPACE     	REVISION	UPDATED                                	STATUS  	CHART                	APP VERSION
freenas-iscsi	democratic-csi	3       	2026-04-13 21:33:55.046516065 +0300 +03	deployed	democratic-csi-0.15.1	1.0        
my-grafana   	monitoring    	3       	2026-04-26 11:19:25.159220339 +0300 +03	deployed	grafana-10.5.15      	12.3.1     
prometheus   	monitoring    	2       	2026-04-26 11:52:41.483417577 +0300 +03	deployed	prometheus-29.2.1    	v3.11.2    
qm2          	ibm-mq        	1       	2026-04-23 17:46:30.675677489 +0300 +03	deployed	ibm-mq-12.0.1        	9.4.2.0    
zfs-nfs      	democratic-csi	3       	2026-04-12 18:27:29.492336532 +0000 UTC	deployed	democratic-csi-0.15.1	1.0        
[vagrant@kube-master ~]$ 

```


