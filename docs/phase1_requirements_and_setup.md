# Phase 1 — Requirements & GNS3 Setup

This phase covers getting GNS3 running in a stable, VMware-backed environment and installing the Cisco device images the rest of the lab depends on.

## Hardware & Software

The lab was built on a Windows host running VMware Workstation Pro, with the GNS3 VM handling all device emulation (so the host's CPU/RAM is what actually matters, not the host OS's native virtualization). Recommended specs for this kind of lab are roughly 16 GB RAM and a 4-core CPU at minimum, with more headroom making the 3-router / 2-switch / 4-PC topology run noticeably smoother.

Software used: GNS3 (2.2.59), the GNS3 VM appliance, VMware Workstation Pro, Python 3.11+, and VS Code for editing the automation scripts.

## Enabling Virtualization

Before the GNS3 VM would boot, a few Windows features had to be turned on — Virtual Machine Platform, Windows Hypervisor Platform, and Windows Subsystem for Linux — alongside VMware's own virtualization engine setting for the VM.

<p align="center">
  <img src="../screenshots/01-setup/03_windows_features_hyperv.png" alt="Windows Features - enabling Virtual Machine Platform and Hyper-V" width="450">
</p>

One issue hit along the way: VMware Workstation reported that virtualized Intel VT-x/EPT wasn't supported on the host, which blocks nested virtualization for the GNS3 VM. The workaround was continuing without it (with a performance trade-off) rather than a hardware fix.

<p align="center">
  <img src="../screenshots/01-setup/02_vtx_ept_warning.png" alt="VT-x/EPT not supported warning" width="420">
</p>

The GNS3 VM itself was allocated 4 GB RAM and 4 processor cores in VMware's VM settings.

<p align="center">
  <img src="../screenshots/01-setup/01_vm_hardware_settings.png" alt="GNS3 VM hardware settings" width="420">
</p>

## GNS3 VM Networking

The GNS3 VM communicates with the GNS3 desktop client over a host-only VMware network (VMnet1). This network adapter and its subnet were confirmed in VMware's Virtual Network Editor before booting the VM.

<p align="center">
  <img src="../screenshots/01-setup/06_vmware_virtual_network_editor.png" alt="VMware Virtual Network Editor - VMnet1 host-only" width="500">
</p>

Once booted, the GNS3 VM picked up an address on that host-only network and reported it directly on its console, along with the SSH and Web UI access details:

<p align="center">
  <img src="../screenshots/01-setup/05_gns3_vm_boot_console.png" alt="GNS3 VM boot console showing assigned IP" width="600">
</p>

## Connecting GNS3 to the VM

In GNS3's preferences, the GNS3 VM was enabled as the virtualization engine (VMware Workstation), with vCPU/RAM allocation set for the VM server itself:

<p align="center">
  <img src="../screenshots/01-setup/04_gns3_vm_preferences.png" alt="GNS3 VM preferences panel" width="500">
</p>

The local GNS3 server preferences (port 3080, the console port range used for telnet access to lab devices, and the UDP tunneling range) were left mostly at GNS3 defaults:

<p align="center">
  <img src="../screenshots/01-setup/07_gns3_server_preferences.png" alt="GNS3 server preferences - ports" width="500">
</p>

**Troubleshooting note:** at one point GNS3 timed out trying to save settings to the VM ("Operation timeout" on a PUT request to `/v2/gns3vm`), which usually points to a firewall/antivirus blocking the local connection rather than a GNS3 configuration problem.

<p align="center">
  <img src="../screenshots/01-setup/08_gns3_connection_timeout_issue.png" alt="GNS3 VM connection timeout error" width="600">
</p>

## Installing the Cisco Device Images

Two Cisco images were needed: `vios-adventerprisek9-m` for the routers (Cisco IOSv) and `vios_l2-adventerprisek9-m` for the switches (Cisco IOSvL2). These were registered in GNS3 as QEMU VM templates.

For the router template, the wizard runs through: choosing to run the QEMU VM on the local computer,

<p align="center">
  <img src="../screenshots/02-device-images/01_qemu_template_server_type.png" alt="QEMU template - server type" width="500">
</p>

naming the template,

<p align="center">
  <img src="../screenshots/02-device-images/02_qemu_template_name_iosv_router.png" alt="QEMU template name - IOSv-Router" width="500">
</p>

confirming the QEMU binary and RAM allocation,

<p align="center">
  <img src="../screenshots/02-device-images/03_qemu_binary_ram.png" alt="QEMU binary and RAM" width="500">
</p>

setting the console type to telnet (so GNS3 can hand out a telnet port per device for console/automation access),

<p align="center">
  <img src="../screenshots/02-device-images/04_qemu_console_type_telnet.png" alt="QEMU console type - telnet" width="500">
</p>

and pointing the template at the actual `vios-adventerprisek9-m` disk image:

<p align="center">
  <img src="../screenshots/02-device-images/05_qemu_disk_image_iosv.png" alt="QEMU disk image - vios-adventerprisek9" width="500">
</p>

One detail that mattered for the topology: the default template only ships 1 network adapter, which isn't enough once a router needs to connect to a parent link, a sibling router, and a switch. The adapter count was bumped to 6 on the finished template so every router has enough interfaces to wire up the full topology.

<p align="center">
  <img src="../screenshots/02-device-images/06_qemu_template_final_adapters6.png" alt="QEMU template final settings - 6 adapters" width="500">
</p>

The same process (with the `vios_l2-adventerprisek9-m` image) was repeated for the switch template.

## Next

With GNS3, the GNS3 VM, and both device templates working, the next step was designing the actual topology and addressing plan — covered in [Phase 2](phase2_planning_and_design.md).
