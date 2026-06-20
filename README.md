# Enterprise Network Automation & Operations Dashboard Platform

A multi-branch enterprise network built in **GNS3** and automated end-to-end with **Python + Netmiko** — covering OSPF routing, VLAN segmentation, SSH-based management, configuration backups, compliance auditing, configuration drift detection, and a unified HTML **Network Operations Dashboard**.

This started as a CCNA-level lab and grew into a small network operations platform: instead of manually checking each device, a set of Netmiko scripts connects to every router and switch, pulls live state, and renders it into a single dashboard you'd actually want to look at every morning.

## Overview

The lab simulates **ABC Company**, with a Headquarters site and two branch offices connected over OSPF, each site segmented into VLANs for users, servers, and management. On top of the network itself, a Python automation layer handles the day-2 operations work: pushing configuration, backing it up, watching for drift between backups, checking compliance against a baseline, and reporting it all in one place.

| | |
|---|---|
| **Lab platform** | GNS3 (run inside the GNS3 VM on VMware Workstation) |
| **Devices** | 3x Cisco IOSv routers, 2x Cisco IOSvL2 switches, 4x VPCS end hosts |
| **Routing** | OSPF, single area (Area 0) |
| **Switching** | VLAN 10 (USERS), VLAN 20 (SERVERS), VLAN 99 (MGMT) |
| **Management access** | SSH (Netmiko `cisco_ios_telnet` to the lab; SSH config pushed on-box) |
| **Automation language** | Python 3 + Netmiko |

## Network Topology

<p align="center">
  <img src="topology/topology.png" alt="Network topology diagram" width="650">
</p>

R1-HQ sits at the head of the topology and connects down to two branch routers, R2-BR1 and R3-BR2, each of which connects to its own access switch and a pair of end hosts. A GNS3 Cloud node bridges the Windows host machine to the lab so that the Python scripts (running on the host) can reach the device telnet/SSH ports — it's part of the working lab file, but it's left out of this diagram since it's lab plumbing rather than a network design feature. More detail on that decision is in [`docs/phase3_topology_build.md`](docs/phase3_topology_build.md).

| Site | Subnet | Gateway |
|---|---|---|
| HQ | 192.168.10.0/24 | 192.168.10.1 |
| Branch 1 | 192.168.20.0/24 | 192.168.20.1 |
| Branch 2 | 192.168.30.0/24 | 192.168.30.1 |

## Features

- Automated device inventory collection across all routers and switches
- Scheduled, timestamped configuration backups
- OSPF neighbor health checks with pass/fail reporting
- Compliance auditing (hostname, local admin account, SSH v2, OSPF presence, password encryption)
- Per-interface up/down monitoring
- VLAN deployment automation via Netmiko `send_config_set`
- Configuration drift detection between any two backup sets
- A unified, dark-themed **Network Operations Dashboard (V2)** with live status cards, per-device health scoring, compliance/OSPF/VLAN tables, a backup & drift viewer, and a search box with an expandable device explorer

## Tech Stack

Cisco IOSv / IOSvL2, GNS3 + GNS3 VM, VMware Workstation, Python 3, Netmiko, OSPF, VLANs, SSH, HTML/CSS/JavaScript (for the dashboard output).

## Repository Structure

```
Network-Automation-Platform/
│
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── topology/
│   └── topology.png
│
├── configs/
│   ├── router_configs/
│   └── switch_configs/
│
├── scripts/
│   ├── inventory/
│   │   └── inventory.py
│   ├── backups/
│   │   └── backup_configs.py
│   ├── monitoring/
│   │   ├── ospf_health_check.py
│   │   ├── interface_monitor.py
│   │   └── compliance_audit.py
│   ├── automation/
│   │   ├── deploy_vlans.py
│   │   └── config_drift.py
│   └── dashboard/
│       └── network_operations_dashboard_v2.py
│
├── backups/            (generated at runtime)
├── drift_reports/       (generated at runtime)
├── reports/             (generated at runtime, dashboard HTML lands here)
│
├── screenshots/
│   ├── 01-setup/
│   ├── 02-device-images/
│   ├── 03-topology-build/
│   ├── 04-automation-scripts/
│   └── 05-dashboard/
│
└── docs/
    ├── phase1_requirements_and_setup.md
    ├── phase2_planning_and_design.md
    ├── phase3_topology_build.md
    ├── phase4_automation_scripts.md
    └── phase5_dashboard_evolution.md
```

## Dashboard Preview

The flagship piece of this project is the merged **Unified Network Operations Dashboard V2** — it connects once to every device, collects everything it needs, and renders one HTML page.

<p align="center">
  <img src="screenshots/05-dashboard/final-v2/01_overview_status_cards.png" alt="Dashboard overview and status cards" width="700">
</p>

<p align="center">
  <img src="screenshots/05-dashboard/final-v2/02_switch_compliance_ospf.png" alt="Switch summary, compliance and OSPF dashboards" width="700">
</p>

<p align="center">
  <img src="screenshots/05-dashboard/final-v2/03_vlan_backup_drift.png" alt="VLAN, backup and drift dashboards" width="700">
</p>

<p align="center">
  <img src="screenshots/05-dashboard/final-v2/04_search_device_explorer.png" alt="Search and device explorer" width="700">
</p>

The dashboard didn't start out looking like this — it began as a single basic status table and grew module by module. That evolution, along with the GNS3 setup, lab build, and individual script runs, is documented phase-by-phase in [`docs/`](docs/).

## Getting Started

**Prerequisites**

- GNS3 + GNS3 VM running on VMware Workstation, with the lab topology imported (see [`docs/phase1_requirements_and_setup.md`](docs/phase1_requirements_and_setup.md) and [`docs/phase3_topology_build.md`](docs/phase3_topology_build.md))
- Python 3.11+
- SSH enabled and a local admin account configured on every router and switch in the lab

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Update device connection details**

Each script in `scripts/` defines its own `routers` / `switches` list at the top of the file (host, port, device type). Update these to match the telnet/SSH ports your own GNS3 topology exposes before running anything.

## Usage

Run any script from inside the `scripts/` folder so the relative `../backups`, `../reports`, `../drift_reports` paths resolve correctly.

```bash
cd scripts
python inventory/inventory.py
python backups/backup_configs.py
python monitoring/ospf_health_check.py
python monitoring/compliance_audit.py
python monitoring/interface_monitor.py
python automation/deploy_vlans.py
python automation/config_drift.py
python dashboard/network_operations_dashboard_v2.py
```

The dashboard script is the one to run last — open the resulting `reports/network_operations_dashboard_v2.html` in any browser.

## Project Phases

| Phase | Description |
|---|---|
| [Phase 1](docs/phase1_requirements_and_setup.md) | GNS3 / GNS3 VM / VMware setup, Cisco IOSv & IOSvL2 device image installation |
| [Phase 2](docs/phase2_planning_and_design.md) | Topology design, IP addressing plan, VLAN plan, automation task list |
| [Phase 3](docs/phase3_topology_build.md) | Building the lab in GNS3, SSH bring-up, IP reachability verification |
| [Phase 4](docs/phase4_automation_scripts.md) | The Netmiko automation scripts — inventory, backup, OSPF check, compliance audit, interface monitor, VLAN deployment, drift detection |
| [Phase 5](docs/phase5_dashboard_evolution.md) | From a single status table to the merged Unified Network Operations Dashboard V2 |

## Future Enhancements

A few directions this project could be taken further: a live Flask dashboard with auto-refresh, email/Slack alerts on compliance or OSPF failures, scheduled backups via cron/Task Scheduler, a topology visualization layer, Git-based configuration version control, and a REST API in front of the inventory/health data.

## Author

Built and documented by Mayu as a flagship CCNA-level network automation project, combining Cisco IOS, GNS3, Python, and Netmiko.
