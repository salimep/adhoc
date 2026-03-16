###  Integrating OpenStack/Contrail with Multi-Vendor MPLS Cores

This Artcle will cover only below subject building contrail/openstack enviorment will be another article (lot of things to discuss such as mtu hugepage consideration etc)

1) BGP Labeled Unicast (BGP-LU)
2) Route Target (RT) Management
3) VRF Routing



## topolagy

![topolagy](/images/topolagy.png)

##  openstack & Vrouter version
![version](/images/op-vrouter-v.png)

ignore ovn&ovs containers for now

Os: Rocky Linux release 9.7 (Blue Onyx)

## lab enviorenment
![lab](/images/env.png)

## Verification

## vrf

![verify](/images/VRF-routes.png)

## ping

![ping](/images/ping-from%20-vm.png)

## Contrail BGP Recevied routes

![bgp](/images/contral-bgp.png)

## gns3 ping

![bgp](/images/gns3-ping.png)

## vmx config to contrail &rovider (EDGE ROUTER)
````
oot# run show configuration | display set | no-more    
set version 18.1R1.9
set system root-authentication encrypted-password "$6$/ck/X8aY$x9DwZxLJ.Lwih8unz3vfXlTxclZUUBfPq85QfCP8MkxEL9FqCJHlclECi.5grMoSHulBofDQ8yZ8FC/VLasmR1"
set system login user admin uid 2000
set system login user admin class super-user
set system login user admin authentication encrypted-password "$6$utIfluCr$bTTXn3kRrjvQRhDjr2dYPEJEvBQ2Vw1BWsUbiRO5YR7pTc0EQTrfTZ8nzcw9/i6bP7jWLRn.mr9SKpsF/CRgR0"
set system services ssh root-login allow
set system syslog user * any emergency
set system syslog file messages any notice
set system syslog file messages authorization info
set system syslog file interactive-commands interactive-commands any
set system processes dhcp-service traceoptions file dhcp_logfile
set system processes dhcp-service traceoptions file size 10m
set system processes dhcp-service traceoptions level all
set system processes dhcp-service traceoptions flag all
set chassis fpc 0 pic 0 tunnel-services
set chassis fpc 0 pic 0 number-of-ports 10
set chassis fpc 0 lite-mode
set interfaces ge-0/0/0 unit 0 family inet address 192.168.10.1/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces gr-0/0/0 unit 0 family inet
set interfaces gr-0/0/0 unit 0 family mpls
set interfaces fxp0 unit 0 family inet dhcp vendor-id Juniper-vmx-VM69B18D5735
set interfaces lo0 unit 0 family inet address 11.11.11.11/32
set interfaces lo0 unit 100 family inet address 99.99.99.1/32
set routing-options rib inet.3
set routing-options static route 0.0.0.0/0 next-hop 192.168.11.1
set routing-options static route 192.168.11.0/24 next-hop 192.168.10.167
set routing-options rib-groups BGP-TO-INET3 import-rib inet.0
set routing-options rib-groups BGP-TO-INET3 import-rib inet.3
set routing-options rib-groups BGP-TO-MPLS import-rib inet.0
set routing-options rib-groups BGP-TO-MPLS import-rib inet.3
set routing-options router-id 11.11.11.11
set routing-options autonomous-system 64512
set routing-options resolution rib bgp.l3vpn.0 resolution-ribs inet.3
set routing-options resolution rib bgp.l3vpn.0 import RESOLVE-VIA-TUNNEL
set routing-options resolution rib bgp.l3vpn.0 import RESOLVE-VIA-GRE
set routing-options dynamic-tunnels CONTRAIL_TUNNEL source-address 192.168.10.1
set routing-options dynamic-tunnels CONTRAIL_TUNNEL gre
set routing-options dynamic-tunnels CONTRAIL_TUNNEL destination-networks 192.168.10.20/32
set routing-options dynamic-tunnels CONTRAIL_TUNNEL destination-networks 192.168.10.40/32
set routing-options dynamic-tunnels CONTRAIL_TUNNEL destination-networks 192.168.10.174/32
set protocols mpls explicit-null
set protocols mpls ipv6-tunneling
set protocols mpls interface ge-0/0/0.0
set protocols mpls interface lo0.0
set protocols bgp family inet-vpn unicast
set protocols bgp group CONTRAIL-CONTROL type internal
set protocols bgp group CONTRAIL-CONTROL local-address 192.168.10.1
set protocols bgp group CONTRAIL-CONTROL family inet-vpn unicast
set protocols bgp group CONTRAIL-CONTROL family route-target
set protocols bgp group CONTRAIL-CONTROL neighbor 192.168.10.20
set protocols bgp group CONTRAIL-CONTRO local-address 192.168.10.1
set protocols bgp group TO-PROVIDER type external
set protocols bgp group TO-PROVIDER multihop ttl 2
set protocols bgp group TO-PROVIDER local-address 192.168.10.1
set protocols bgp group TO-PROVIDER family inet unicast
set protocols bgp group TO-PROVIDER family inet labeled-unicast rib-group BGP-TO-MPLS
set protocols bgp group TO-PROVIDER family inet-vpn unicast loops 2
set protocols bgp group TO-PROVIDER export SEND-LABEL
set protocols bgp group TO-PROVIDER export EXPORT-LU
set protocols bgp group TO-PROVIDER peer-as 100
set protocols bgp group TO-PROVIDER neighbor 192.168.10.10 family inet labeled-unicast rib-group BGP-TO-MPLS
set protocols bgp group TO-PROVIDER neighbor 192.168.10.10 family inet labeled-unicast explicit-null connected-only
set protocols bgp group TO-PROVIDER neighbor 192.168.10.10 family inet-vpn unicast
set protocols bgp group TO-PROVIDER neighbor 192.168.10.10 export EXPORT-LAN
set policy-options policy-statement ADVERTISE-VRF-ROUTES term 1 then next-hop 192.168.10.1
set policy-options policy-statement ADVERTISE-VRF-ROUTES term 1 then accept
set policy-options policy-statement EXPORT-LAN term 1 from instance company-A
set policy-options policy-statement EXPORT-LAN term 1 from protocol direct
set policy-options policy-statement EXPORT-LAN term 1 then community add comm-1
set policy-options policy-statement EXPORT-LAN term 1 then accept
set policy-options policy-statement EXPORT-LAN term 2 from protocol direct
set policy-options policy-statement EXPORT-LAN term 2 then accept
set policy-options policy-statement EXPORT-LAN from protocol direct
set policy-options policy-statement EXPORT-LAN then accept
set policy-options policy-statement EXPORT-LU term 1 from route-filter 11.11.11.11/32 exact
set policy-options policy-statement EXPORT-LU term 1 then accept
set policy-options policy-statement EXPORT-POLICY term 1 from protocol direct
set policy-options policy-statement EXPORT-POLICY term 1 from protocol bgp
set policy-options policy-statement EXPORT-POLICY term 1 then accept
set policy-options policy-statement RESOLVE-VIA-GRE term 1 then accept
set policy-options policy-statement RESOLVE-VIA-TUNNEL term 1 from route-filter 192.168.10.0/24 orlonger
set policy-options policy-statement RESOLVE-VIA-TUNNEL term 1 then accept
set policy-options policy-statement RESOLVE-VIA-TUNNEL term SKIP-CISCO then reject
set policy-options policy-statement SEND-LABEL term 1 from protocol direct
set policy-options policy-statement SEND-LABEL term 1 from route-filter 11.11.11.11/32 exact
set policy-options policy-statement SEND-LABEL term 1 then accept
set policy-options policy-statement TRIGGER-TUNNEL term 1 from route-filter 192.168.10.0/24 orlonger
set policy-options policy-statement TRIGGER-TUNNEL term 1 then accept
set policy-options policy-statement company-A-import term 1 from community comm-1
set policy-options policy-statement company-A-import term 1 then accept
set policy-options policy-statement company-A-import term 2 from community comm-2
set policy-options policy-statement company-A-import term 2 then accept
set policy-options policy-statement company-A-import term default then reject
set policy-options community comm-1 members target:100:101
set policy-options community comm-1 members target:64512:101
set policy-options community comm-1 members target:64512:20002
set policy-options community comm-2 members target:64512:20002
set routing-instances company-A instance-type vrf
set routing-instances company-A interface lo0.100
set routing-instances company-A route-distinguisher 64512:20002
set routing-instances company-A vrf-target target:64512:20002
set routing-instances company-A vrf-table-label
set routing-instances company-A routing-options auto-export

[edit]
root# 

````

## Adding customer (VRF)  steps

```

### Adding VRF   steps #####

juniper vmx
--

set routing-instances company-B instance-type vrf
set routing-instances company-B interface lo0.200
set routing-instances company-B route-distinguisher 64512:30001
set routing-instances company-B vrf-target target:64512:30001
set routing-instances company-B vrf-table-label


set interfaces lo0 unit 200 family inet address 88.88.88.1/32

# Update your existing policy
set policy-options policy-statement EXPORT-LAN term 3 from instance company-B
set policy-options policy-statement EXPORT-LAN term 3 from protocol direct
set policy-options policy-statement EXPORT-LAN term 3 then accept

PE-CE-1 side

---
ip vrf company-B
 rd 64512:30001
 route-target export 64512:30001
 route-target import 64512:30001
 

BGP CONFIG CHANGE 

address-family ipv4 vrf company-B
  redistribute connected
  redistribute static


PE-CE-2 side

---
ip vrf company-B
 rd 64512:30001
 route-target export 64512:30001
 route-target import 64512:30001
 

BGP CONFIG CHANGE 

 address-family ipv4 vrf company-B
  network 0.0.0.0
  redistribute connected
  redistribute static
  neighbor 55.55.55.2 remote-as 301
  neighbor 55.55.55.2 activate
 exit-address-family


Customer END router
----

router bgp 301
 neighbor 55.55.55.1 remote-as 100
 address-family ipv4
  redistribute connected
  neighbor 55.55.55.1 activate
 exit-address-family
 ```


### if  use vxlan tunnel between SDN and cisco  model (i were trying with cisco as well :)





```

lb1.salimonline.local#sh run | sec bgp
 host-reachability protocol bgp
router bgp 64512
 bgp log-neighbor-changes
 neighbor 2.2.2.2 remote-as 100
 neighbor 2.2.2.2 ebgp-multihop 2
 neighbor 192.168.10.20 remote-as 64512
 neighbor 192.168.10.20 update-source Loopback0
 !
 address-family ipv4
  neighbor 2.2.2.2 activate
  neighbor 2.2.2.2 soft-reconfiguration inbound
  neighbor 2.2.2.2 send-label
  neighbor 192.168.10.20 activate
 exit-address-family
 !
 address-family vpnv4
  import l2vpn evpn re-originate
  neighbor 2.2.2.2 activate
  neighbor 2.2.2.2 send-community both
  neighbor 2.2.2.2 next-hop-self
  neighbor 2.2.2.2 route-map SET-NEXT-HOP out
 exit-address-family
 !
 address-family l2vpn evpn
  import vpnv4 unicast re-originate
  neighbor 192.168.10.20 activate
  neighbor 192.168.10.20 send-community both
  neighbor 192.168.10.20 soft-reconfiguration inbound
  neighbor 192.168.10.20 encap vxlan
 exit-address-family
 !
 address-family ipv4 vrf admin
  advertise l2vpn evpn
  redistribute connected
 exit-address-family
 !
 address-family ipv4 vrf company-A
  advertise l2vpn evpn
  redistribute connected
 exit-address-family


```