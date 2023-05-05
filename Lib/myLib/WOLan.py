import socket
import struct

broadcast_address = '192.168.1.255'


class WakeOnLan:

    def wake_up(self, mac_address):

        mac = mac_address.replace(':', '').replace('-', '')
        mac = struct.pack('!6B', *[int(mac[i:i+2], 16)
                          for i in range(0, 12, 2)])

        packet = b'\xff' * 6 + mac * 16

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(packet, (broadcast_address, 9))
        sock.close()

    @staticmethod
    def process_mac_address(mac):

        wol = WakeOnLan()
        wol.wake_up(mac)

        del wol
