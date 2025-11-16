"""ArtNET/DMX lighting control for synchronized light effects"""

import socket
import struct
import logging

logger = logging.getLogger(__name__)


class ArtNetController:
    """Controls DMX lighting via ArtNET protocol"""
    
    def __init__(self, target_ip='127.0.0.1', universe=0, port=6454):
        self.target_ip = target_ip
        self.universe = universe
        self.port = port
        self.sock = None
        self.is_connected = False
        self.channel_values = [0] * 512
        logger.info(f"ArtNetController initialized: {target_ip}:{port}, universe={universe}")
    
    def connect(self):
        """Initialize socket connection"""
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
        """Send DMX data via ArtNET"""
        if not self.is_connected or self.sock is None:
            logger.warning("ArtNET not connected, cannot send DMX")
            return False
        
        try:
            data = channel_values[:512]
            while len(data) < 512:
                data.append(0)
            
            packet = bytearray()
            packet.extend(b'Art-Net\x00')
            packet.extend(struct.pack('<H', 0x5000))
            packet.extend(struct.pack('>H', 14))
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
        """Set brightness for all channels (0-100%)"""
        dmx_value = int((brightness / 100.0) * 255)
        dmx_value = max(0, min(255, dmx_value))
        channels = [0] * 512
        channels[0] = dmx_value
        channels[1] = dmx_value
        channels[2] = dmx_value
        return self.send_dmx(channels)
    
    def set_rgb(self, r, g, b):
        """Set RGB values for channels 1-3"""
        channels = [0] * 512
        channels[0] = max(0, min(255, int(r)))
        channels[1] = max(0, min(255, int(g)))
        channels[2] = max(0, min(255, int(b)))
        return self.send_dmx(channels)
    
    def flash_color(self, r, g, b, duration=0.2):
        """Flash a color briefly"""
        self.set_rgb(r, g, b)
        logger.debug(f"Flash color: RGB({r}, {g}, {b})")
    
    def goal_flash(self, player_left=True):
        """Flash effect for goal scored"""
        if player_left:
            self.flash_color(0, 255, 0)
        else:
            self.flash_color(255, 0, 0)
    
    def collision_flash(self):
        """Brief intensity spike for ball collision"""
        self.flash_color(255, 255, 255)
    
    def disconnect(self):
        """Close socket connection"""
        if self.sock is not None:
            try:
                self.sock.close()
                logger.info("ArtNET socket closed")
            except Exception as e:
                logger.error(f"Error closing ArtNET socket: {e}")
            finally:
                self.sock = None
                self.is_connected = False
