import socket
import struct
import logging

logger = logging.getLogger(__name__)

DEFAULT_TARGET_IP = '127.0.0.1'
DEFAULT_UNIVERSE = 0
DEFAULT_PORT = 6454
DMX_CHANNELS = 512
DMX_MAX_VALUE = 255
BRIGHTNESS_MAX = 100
ARTNET_OPCODE = 0x5000
ARTNET_PROTOCOL_VERSION = 14
RGB_CHANNELS = 3


class ArtNetController:
    def __init__(self, target_ip=DEFAULT_TARGET_IP, universe=DEFAULT_UNIVERSE, port=DEFAULT_PORT):
        self.target_ip = target_ip
        self.universe = universe
        self.port = port
        self.sock = None
        self.is_connected = False
        self.channel_values = [0] * DMX_CHANNELS
        logger.info(f"ArtNetController initialized: {target_ip}:{port}, universe={universe}")
    
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.is_connected = True
            logger.info("ArtNET socket created")
            return True
        except Exception as e:
            logger.error(f"Failed to create ArtNET socket: {e}", exc_info=True)
            self.is_connected = False
            return False
    
    def send_dmx(self, channel_values):
        if not self.is_connected or self.sock is None:
            logger.warning("ArtNET not connected, cannot send DMX")
            return False
        
        try:
            data = channel_values[:DMX_CHANNELS]
            while len(data) < DMX_CHANNELS:
                data.append(0)
            
            packet = bytearray()
            packet.extend(b'Art-Net\x00')
            packet.extend(struct.pack('<H', ARTNET_OPCODE))
            packet.extend(struct.pack('>H', ARTNET_PROTOCOL_VERSION))
            packet.append(0)
            packet.append(0)
            packet.extend(struct.pack('<H', self.universe))
            length = len(data)
            packet.extend(struct.pack('>H', length))
            packet.extend(bytes(data))
            
            self.sock.sendto(packet, (self.target_ip, self.port))
            self.channel_values = data.copy()
            logger.debug(f"Sent DMX data: {length} channels to {self.target_ip}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending DMX data: {e}", exc_info=True)
            return False
    
    def set_brightness(self, brightness):
        dmx_value = int((brightness / BRIGHTNESS_MAX) * DMX_MAX_VALUE)
        dmx_value = max(0, min(DMX_MAX_VALUE, dmx_value))
        channels = [0] * DMX_CHANNELS
        for i in range(RGB_CHANNELS):
            channels[i] = dmx_value
        return self.send_dmx(channels)
    
    def set_rgb(self, r, g, b):
        channels = [0] * DMX_CHANNELS
        channels[0] = max(0, min(DMX_MAX_VALUE, int(r)))
        channels[1] = max(0, min(DMX_MAX_VALUE, int(g)))
        channels[2] = max(0, min(DMX_MAX_VALUE, int(b)))
        return self.send_dmx(channels)
    
    def flash_color(self, r, g, b, duration=0.2):
        self.set_rgb(r, g, b)
        logger.debug(f"Flash color: RGB({r}, {g}, {b})")
    
    def goal_flash(self, player_left=True):
        if player_left:
            self.flash_color(0, 255, 0)
        else:
            self.flash_color(255, 0, 0)
    
    def collision_flash(self):
        self.flash_color(255, 255, 255)
    
    def disconnect(self):
        if self.sock is not None:
            try:
                self.sock.close()
                logger.info("ArtNET socket closed")
            except Exception as e:
                logger.error(f"Error closing ArtNET socket: {e}")
            finally:
                self.sock = None
                self.is_connected = False
