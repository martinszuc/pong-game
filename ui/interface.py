"""
UI: wxPython GUI window and controls
"""

import wx
import cv2
import logging

logger = logging.getLogger(__name__)


class PongFrame(wx.Frame):
    """Main application window with game display and controls"""
    
    def __init__(self, game, renderer, on_close_callback=None):
        super().__init__(None, title="Audio-Controlled Pong Game", 
                        size=(800, 600))
        
        self.game = game
        self.renderer = renderer
        self.on_close_callback = on_close_callback
        
        # create panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        # create sizer for layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # game display area (will show OpenCV frame)
        # Use StaticBitmap for more reliable image display
        self.display_bitmap = wx.StaticBitmap(panel, size=(800, 600))
        self.display_bitmap.SetBackgroundColour(wx.Colour(0, 0, 0))
        main_sizer.Add(self.display_bitmap, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        # Small status bar at bottom
        status_bar = wx.Panel(panel)
        status_bar.SetBackgroundColour(wx.Colour(30, 30, 30))
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.status_text = wx.StaticText(status_bar, label="Press ESC for menu | W/S to move paddle | Space to pause")
        self.status_text.SetForegroundColour(wx.Colour(200, 200, 200))
        status_sizer.Add(self.status_text, flag=wx.ALL, border=5)
        
        status_bar.SetSizer(status_sizer)
        main_sizer.Add(status_bar, flag=wx.EXPAND | wx.ALL, border=0)
        
        panel.SetSizer(main_sizer)
        
        # Store panel reference for focus management
        self.panel = panel
        
        # bind events - bind to panel so it can receive keyboard events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        panel.Bind(wx.EVT_KEY_UP, self.on_key_up)
        
        # make panel accept keyboard focus
        panel.SetCanFocus(True)
        panel.SetFocus()
        
        # also bind to frame for when panel loses focus
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        
        # bind focus events to ensure panel can receive keys
        panel.Bind(wx.EVT_SET_FOCUS, lambda e: logger.debug("Panel gained focus"))
        panel.Bind(wx.EVT_KILL_FOCUS, lambda e: panel.SetFocus())  # Auto-refocus
        
        self.Show()
        
        # Store menu reference
        self.menu_dialog = None
    
    def on_close(self, event):
        """Handle window close event"""
        if self.on_close_callback:
            self.on_close_callback()
        self.Destroy()
    
    def show_menu(self):
        """Show menu dialog"""
        if self.menu_dialog is None or not self.menu_dialog.IsShown():
            from .menu import MenuDialog
            self.menu_dialog = MenuDialog(self, self.game, self.renderer)
            self.menu_dialog.ShowModal()
            self.menu_dialog.Destroy()
            self.menu_dialog = None
            # Refocus panel after menu closes
            self.panel.SetFocus()
    
    def on_key_down(self, event):
        """Handle key press events"""
        key_code = event.GetKeyCode()
        key_char = event.GetUnicodeKey()
        
        logger.debug(f"Key pressed: code={key_code}, char={key_char}")
        
        # left paddle: W (up), S (down)
        # Check both key code and unicode key for case-insensitive matching
        if key_code == ord('W') or key_code == ord('w') or key_char == ord('W') or key_char == ord('w'):
            logger.debug("Moving left paddle up")
            self.game.paddle_left.move_up()
        elif key_code == ord('S') or key_code == ord('s') or key_char == ord('S') or key_char == ord('s'):
            logger.debug("Moving left paddle down")
            self.game.paddle_left.move_down()
        
        # right paddle: Up arrow, Down arrow (only if AI is disabled)
        elif key_code == wx.WXK_UP:
            if not self.game.ai_enabled:
                logger.debug("Moving right paddle up")
                self.game.paddle_right.move_up()
        elif key_code == wx.WXK_DOWN:
            if not self.game.ai_enabled:
                logger.debug("Moving right paddle down")
                self.game.paddle_right.move_down()
        
        # pause: Space
        elif key_code == wx.WXK_SPACE:
            logger.debug("Toggling pause")
            self.game.pause()
            status = "PAUSED" if self.game.game_state == 'paused' else "Playing"
            self.status_text.SetLabel(f"Status: {status} | Press ESC for menu | W/S to move paddle")
        
        # menu: ESC
        elif key_code == wx.WXK_ESCAPE:
            logger.debug("Opening menu")
            self.show_menu()
        
        event.Skip()
    
    def on_key_up(self, event):
        """Handle key release events"""
        key_code = event.GetKeyCode()
        key_char = event.GetUnicodeKey()
        
        # stop paddle movement when keys released
        if key_code in (ord('W'), ord('w'), ord('S'), ord('s')) or key_char in (ord('W'), ord('w'), ord('S'), ord('s')):
            logger.debug("Stopping left paddle")
            self.game.paddle_left.stop()
        elif key_code in (wx.WXK_UP, wx.WXK_DOWN):
            if not self.game.ai_enabled:
                logger.debug("Stopping right paddle")
                self.game.paddle_right.stop()
        
        event.Skip()
    
    def update_display(self, frame):
        """Update the display bitmap with OpenCV frame"""
        try:
            if frame is None:
                logger.warning("Attempted to display None frame")
                return
            
            height, width = frame.shape[:2]
            
            # convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # convert to wx.Image
            wx_image = wx.Image(width, height, frame_rgb.tobytes())
            
            # scale to fit bitmap if needed
            bitmap_size = self.display_bitmap.GetSize()
            if width != bitmap_size.width or height != bitmap_size.height:
                wx_image = wx_image.Scale(bitmap_size.width, bitmap_size.height, wx.IMAGE_QUALITY_HIGH)
            
            # convert to wx.Bitmap and set
            bitmap = wx.Bitmap(wx_image)
            self.display_bitmap.SetBitmap(bitmap)
            
            # Force refresh
            self.display_bitmap.Refresh()
            
            # Ensure panel maintains focus for keyboard input
            if not self.panel.HasFocus():
                wx.CallAfter(self.panel.SetFocus)
            
        except Exception as e:
            logger.error(f"Error updating display: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())

