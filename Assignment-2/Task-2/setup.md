# Experimental Setup: TCP Attack (Host as Router)

This guide outlines the procedure for setting up an experimental environment where the host machine acts as a router for a Virtual Machine (VM). This topology ensures the attacker script (running on the host) can intercept and inject forged TCP packets before legitimate packets arrive, winning the necessary race condition.

SourceIP: 91.189.91.108
DestinationIP: 172.17.0.2 (VM's IP)

## Phase 1: Docker Container Configuration

To sniff and manipulate the victim's traffic natively from the host, we will use a Docker container. By default, Docker attaches containers to a bridge network, which automatically routes the container's traffic through a virtual interface on the host machine.

1. **Start the Container (First Time):** Open a terminal on your host and run a new interactive Ubuntu container. We will name it `tcp_victim` for easy reference:
```bash
docker run -it --name tcp_victim ubuntu /bin/bash
```

(Note: For subsequent runs after you have exited the container, do not use the run command again. Instead, start and attach to the existing container using:
 `docker start -ai tcp_victim`

2. Install Networking Tools: Base Docker images are highly stripped down. Inside the container's shell, update the package manager and install the tools needed for the experiment:

```Bash
apt update && apt install wget iproute2 iputils-ping -y
   ```

3. Verify Connectivity: Inside the container, ping an external server to confirm its internet access is actively routing through the host's Docker bridge:

```Bash
ping 8.8.8.8
```
# Phase 2: Identifying IPs and Interfaces
Phase 2: Identifying IPs and Interfaces

To configure the Scapy script and Wireshark capture filters, you must identify the IP addresses of the communication endpoints and the specific Docker interface handling the traffic.

1. **Find the Container's IP (dest_ip):**
- Inside the container, run `ip addr`.
- Look for the eth0 interface and note the inet IP address.
- Example Output: 172.17.0.2.

2. **Find the Target Server IP (source_ip):**
- Decide on a target file to download (e.g., an Ubuntu ISO).
- Inside the container or on the host, run: ping releases.ubuntu.com
- Note the resolved IP address.

3. **Find the Host's Virtual Interface:**
- On the host machine (outside the container), list network interfaces using ip link or ifconfig.
- Identify the Docker bridge interface. Unless you have configured custom Docker networks, this is almost always named docker0.
- Would you like me to map out those Wireshark display filters next so you know exactly how to isolate your forged packets for your report screenshots?

## Phase 3: Script Adaptation (The Interface Tweak)

By default, Scapy's `sniff()` function listens on the host's primary network interface. Because the VM traffic traverses a virtual interface before being NATed, Scapy must be explicitly told where to listen.

Update the `sniff()` functions in your Python script to include the `iface` parameter:

```python
# Define your virtual interface (replace 'docker0' with your actual interface)
INTERFACE = "docker0" 

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