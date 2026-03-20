# Experimental Setup: TCP Attack (Host as Router)

This guide outlines the procedure for setting up an experimental environment where the host machine acts as a router for a Virtual Machine (VM). This topology ensures the attacker script (running on the host) can intercept and inject forged TCP packets before legitimate packets arrive, winning the necessary race condition.

## Phase 1: Virtual Machine Network Configuration

To sniff and manipulate the VM's traffic natively from the host, the VM must route its traffic through the host's virtual network adapter.

1. **Configure the VM Network:** In your hypervisor (e.g., VirtualBox, VMware), open the VM settings and set the network adapter to **NAT** (or "NAT Network").
2. **Boot the VM:** Start your guest operating system (e.g., Ubuntu, Debian).
3. **Verify Connectivity:** Open a terminal inside the VM and ping an external server (e.g., `ping 8.8.8.8`) to confirm internet access is actively routing through the host.

## Phase 2: Identifying IPs and Interfaces

To configure the Scapy script and capture filters, you must identify the IP addresses of the communication endpoints and the virtual interface handling the traffic.

1. **Find the VM's IP (`dest_ip`):**
   * Inside the VM, run `ip addr` (Linux) or `ifconfig`.
   * *Example Output:* `10.0.2.15` or `192.168.122.51`.
2. **Find the Target Server IP (`source_ip`):**
   * Decide on a target file to download (e.g., an Ubuntu ISO).
   * On the host or VM, run: `ping releases.ubuntu.com`
   * Note the resolved IP address.
3. **Find the Host's Virtual Interface:**
   * On the **host machine**, list network interfaces using `ip link` (Linux/macOS) or `ipconfig` (Windows).
   * Identify the interface tied to the hypervisor (e.g., `vboxnet0`, `vmnet8`, `virbr0`, or `utun`).

## Phase 3: Script Adaptation (The Interface Tweak)

By default, Scapy's `sniff()` function listens on the host's primary network interface. Because the VM traffic traverses a virtual interface before being NATed, Scapy must be explicitly told where to listen.

Update the `sniff()` functions in your Python script to include the `iface` parameter:

```python
# Define your virtual interface (replace 'vmnet8' with your actual interface)
INTERFACE = "vmnet8" 

# Update inside throttle_transmission:
sniff(iface=INTERFACE, filter=f"tcp and src host {dest_ip} and dst host {source_ip}", prn=prn_throttle)

# Update inside kill_transmission:
sniff(iface=INTERFACE, filter=f"tcp and src host {source_ip} and dst host {dest_ip}", prn=prn_kill, count=10)
```

## Phase 4: Execution and Traffic Capture
With the environment configured and the script updated, you can execute the attack and capture the evidence required for the report.

1. Start Packet Capture (Host)
Open Wireshark on the host machine.

Select the virtual interface identified in Phase 2.

Apply a capture filter (e.g., host <VM_IP>) to isolate the relevant traffic.

2. Initiate the Download (VM)
Open a terminal in the VM.

Start downloading a large file using wget to monitor real-time speed:

```Bash
wget https://releases.ubuntu.com/22.04.4/ubuntu-22.04.4-desktop-amd64.iso
```
1. Launch the Attack (Host)
Open a terminal on the host machine.

Execute the Scapy script with elevated privileges (required for raw sockets):

To test the Throttling (Duplicate ACKs):

```Bash
sudo python3 throttle_script.py <Server_IP> <VM_IP> throttle
```
(Expected Result: The wget download speed in the VM should drastically decrease as TCP congestion control is triggered).

To test the Connection Kill (RST Injection):

```Bash
sudo python3 throttle_script.py <Server_IP> <VM_IP> kill
```
(Expected Result: The wget download should immediately terminate with a "Connection reset by peer" or similar error).


Would you like me to look over the Scapy logic for generating those duplicate ACKs