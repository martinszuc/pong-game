"""
UI: wxPython GUI window and controls
"""

import wx
import cv2
import logging

logger = logging.getLogger(__name__)


class PongFrame(wx.Frame):
    """Main application window with game display and menu/controls"""
    
    def __init__(self, game, renderer, on_close_callback=None):
        # Game dimensions
        game_width = 800
        game_height = 600
        
        # Window size
        window_width = game_width + 10  # small border
        window_height = game_height + 10
        
        super().__init__(None, title="Audio-Controlled Pong Game", 
                        size=(window_width, window_height))
        
        self.game = game
        self.renderer = renderer
        self.on_close_callback = on_close_callback
        
        # Track key states simply
        self.keys_down = {'W': False, 'S': False}
        
        # create panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(20, 20, 20))
        
        # Store panel reference first
        self.panel = panel
        
        # Create card panel for switching between menu and game
        self.card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create menu panel
        self.menu_panel = self.create_menu_panel(panel)
        
        # Create game panel
        self.game_panel = self.create_game_panel(panel)
        
        # Add panels to card sizer (only show one at a time)
        self.card_sizer.Add(self.menu_panel, 1, wx.EXPAND)
        self.card_sizer.Add(self.game_panel, 1, wx.EXPAND)
        
        panel.SetSizer(self.card_sizer)
        
        # Start with menu visible (after panel is set)
        self.show_menu_panel()
        
        # bind events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Simple key handling - bind to frame for global capture
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        
        # Timer to continuously check W/S key states
        self.key_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_movement_keys, self.key_timer)
        self.key_timer.Start(50)  # Check every 50ms
        
        self.Show()
        
        # Set focus to frame
        self.SetFocus()
    
    def create_menu_panel(self, parent):
        """Create the menu panel"""
        menu_panel = wx.Panel(parent)
        menu_panel.SetBackgroundColour(wx.Colour(30, 30, 30))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(menu_panel, label="PONG GAME")
        title_font = wx.Font(48, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 50)
        
        # Start button
        start_btn = wx.Button(menu_panel, label="START GAME", size=(200, 50))
        start_btn.Bind(wx.EVT_BUTTON, self.on_start_game)
        sizer.Add(start_btn, 0, wx.ALIGN_CENTER | wx.TOP, 50)
        
        # Volume control
        volume_label = wx.StaticText(menu_panel, label="Volume:")
        volume_label.SetForegroundColour(wx.Colour(200, 200, 200))
        sizer.Add(volume_label, 0, wx.ALIGN_CENTER | wx.TOP, 30)
        
        self.volume_slider = wx.Slider(menu_panel, value=50, minValue=0, maxValue=100, 
                                      size=(300, 50),
                                      style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        sizer.Add(self.volume_slider, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        # Controls info
        controls_label = wx.StaticText(menu_panel, 
            label="CONTROLS:\n\n" +
                  "W/S - Move Left Paddle\n" + 
                  "Arrow Keys - Move Right Paddle (if AI disabled)\n" +
                  "SPACE - Pause/Resume\n" +
                  "ESC - Return to Menu\n" +
                  "R - Reset Game")
        controls_label.SetForegroundColour(wx.Colour(180, 180, 180))
        controls_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        controls_label.SetFont(controls_font)
        sizer.Add(controls_label, 0, wx.ALIGN_CENTER | wx.TOP, 30)
        
        # AI Toggle
        self.ai_checkbox = wx.CheckBox(menu_panel, label="Enable AI Opponent")
        self.ai_checkbox.SetValue(self.game.ai_enabled)
        self.ai_checkbox.SetForegroundColour(wx.Colour(200, 200, 200))
        self.ai_checkbox.Bind(wx.EVT_CHECKBOX, self.on_toggle_ai)
        sizer.Add(self.ai_checkbox, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        menu_panel.SetSizer(sizer)
        return menu_panel
    
    def create_game_panel(self, parent):
        """Create the game display panel"""
        game_panel = wx.Panel(parent)
        game_panel.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # game display area (will show OpenCV frame)
        self.display_bitmap = wx.StaticBitmap(game_panel, size=(800, 600))
        self.display_bitmap.SetBackgroundColour(wx.Colour(0, 0, 0))
        sizer.Add(self.display_bitmap, 1, wx.EXPAND)
        
        game_panel.SetSizer(sizer)
        return game_panel
    
    def show_menu_panel(self):
        """Show menu panel"""
        self.menu_panel.Show()
        self.game_panel.Hide()
        self.panel.Layout()
    
    def show_game_panel(self):
        """Show game panel"""
        self.menu_panel.Hide()
        self.game_panel.Show()
        self.panel.Layout()
    
    def on_start_game(self, event):
        """Start game button clicked"""
        self.game.start_game()
        self.show_game_panel()
        self.SetFocus()  # Ensure we have focus for keyboard
    
    def on_toggle_ai(self, event):
        """Toggle AI opponent"""
        self.game.ai_enabled = self.ai_checkbox.GetValue()
    
    def on_key(self, event):
        """Simple unified key handler using CHAR_HOOK"""
        key = event.GetUnicodeKey()
        if key == wx.WXK_NONE:
            key = event.GetKeyCode()
        
        # Check for menu/game state
        if self.game.game_state == 'menu':
            # In menu, only handle ESC to quit
            if key == wx.WXK_ESCAPE:
                self.Close()
            else:
                event.Skip()
            return
        
        # In game states (playing/paused)
        if key == wx.WXK_ESCAPE:
            # Return to menu
            self.game.to_menu()
            self.show_menu_panel()
            return
        
        if key == wx.WXK_SPACE:
            # Toggle pause
            self.game.pause()
            return
        
        if key == ord('R') or key == ord('r'):
            # Reset game
            self.game.reset()
            return
        
        # Arrow keys for right paddle if AI disabled
        if not self.game.ai_enabled:
            if key == wx.WXK_UP:
                self.game.paddle_right.move_up()
            elif key == wx.WXK_DOWN:
                self.game.paddle_right.move_down()
        
        event.Skip()
    
    def check_movement_keys(self, event):
        """Timer callback to continuously check movement keys"""
        # Only check when in game
        if self.game.game_state not in ['playing', 'paused']:
            return
        
        # Check W/S keys
        w_pressed = wx.GetKeyState(ord('W'))
        s_pressed = wx.GetKeyState(ord('S'))
        
        # Determine paddle direction based on current key states
        if w_pressed and not s_pressed:
            if not self.keys_down['W']:
                self.keys_down['W'] = True
                self.keys_down['S'] = False
                self.game.paddle_left.move_up()
        elif s_pressed and not w_pressed:
            if not self.keys_down['S']:
                self.keys_down['S'] = True
                self.keys_down['W'] = False
                self.game.paddle_left.move_down()
        elif not w_pressed and not s_pressed:
            if self.keys_down['W'] or self.keys_down['S']:
                self.keys_down['W'] = False
                self.keys_down['S'] = False
                self.game.paddle_left.stop()
        
        # Check arrow keys for right paddle if AI disabled
        if not self.game.ai_enabled:
            up_pressed = wx.GetKeyState(wx.WXK_UP)
            down_pressed = wx.GetKeyState(wx.WXK_DOWN)
            
            if up_pressed and not down_pressed:
                self.game.paddle_right.move_up()
            elif down_pressed and not up_pressed:
                self.game.paddle_right.move_down()
            elif not up_pressed and not down_pressed:
                self.game.paddle_right.stop()
    
    def on_close(self, event):
        """Handle window close event"""
        if hasattr(self, 'key_timer'):
            self.key_timer.Stop()
        if self.on_close_callback:
            self.on_close_callback()
        self.Destroy()
    
    def update_display(self, frame):
        """Update the display bitmap with OpenCV frame"""
        try:
            # Only update if in game view
            if self.game.game_state in ['playing', 'paused']:
                if not self.game_panel.IsShown():
                    self.show_game_panel()
                
                if frame is None:
                    logger.warning("Received None frame, skipping display update")
                    return
                
                # convert opencv frame to wx bitmap
                height, width = frame.shape[:2]
                
                # opencv uses BGR, wx uses RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create wx Image from the array
                wx_image = wx.Image(width, height)
                wx_image.SetData(rgb_frame.tobytes())
                
                # Convert to bitmap and display
                bitmap = wx.Bitmap(wx_image)
                self.display_bitmap.SetBitmap(bitmap)
                self.display_bitmap.Refresh()
        except Exception as e:
            logger.error(f"Error updating display: {e}", exc_info=True)