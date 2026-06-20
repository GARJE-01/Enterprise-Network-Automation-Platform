# Phase 2 — Planning & Design

Before touching GNS3 again, this phase nailed down what the network actually needed to look like and what the automation layer would eventually have to do.

## Scenario

The lab simulates **ABC Company**: a Headquarters site plus two branch offices, needing inter-branch connectivity, dynamic routing between sites, VLAN segmentation within each site, and a way to manage it all without logging into every box by hand.

<p align="center">
  <img src="../topology/topology.png" alt="Planned network topology" width="600">
</p>

R1-HQ sits at the top of the topology with R2-BR1 and R3-BR2 as the two branch routers beneath it, each fronting its own access switch and pair of end hosts.

## Addressing Plan

| Site | Subnet | Gateway |
|---|---|---|
| HQ | 192.168.10.0/24 | 192.168.10.1 |
| Branch 1 | 192.168.20.0/24 | 192.168.20.1 |
| Branch 2 | 192.168.30.0/24 | 192.168.30.1 |

## Routing

OSPF, single area (Area 0), with all three routers participating. Each router has at least one OSPF neighbor relationship to verify once the lab is up — R1-HQ has two (one to each branch), and each branch router has one (back to HQ).

## VLAN Plan

| VLAN | Name | Purpose |
|---|---|---|
| 10 | USERS | End-user devices |
| 20 | SERVERS | Server segment |
| 99 | MGMT | Management traffic |

## Automation Task List

The Python/Netmiko layer was scoped to handle seven jobs once the lab itself was reachable over SSH/telnet:

1. Collect a device inventory across all routers and switches
2. Back up running configuration on a schedule
3. Verify OSPF neighbor health
4. Audit configuration against a compliance baseline (hostname set, local admin account present, SSH v2 enabled, OSPF configured, passwords encrypted)
5. Monitor interface up/down state
6. Deploy VLANs to the switches via `send_config_set`
7. Detect configuration drift between backup sets

Everything from Phase 4 onward maps directly back to this list — each numbered item became its own script.

## Next

With the topology, addressing, VLAN plan, and automation scope settled, [Phase 3](phase3_topology_build.md) covers actually building this in GNS3 and bringing devices up under SSH.
