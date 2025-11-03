"""
Menu screen for game settings and controls
"""

import wx
import logging

logger = logging.getLogger(__name__)


class MenuDialog(wx.Dialog):
    """Menu dialog for game settings"""
    
    def __init__(self, parent, game, renderer):
        super().__init__(parent, title="Game Menu", size=(400, 350))
        
        self.game = game
        self.renderer = renderer
        self.volume_value = 50
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Game Settings", style=wx.ALIGN_CENTER)
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        main_sizer.Add(title, flag=wx.ALL | wx.EXPAND, border=20)
        
        # Volume control
        volume_box = wx.StaticBox(panel, label="Audio Settings")
        volume_sizer = wx.StaticBoxSizer(volume_box, wx.VERTICAL)
        
        volume_label = wx.StaticText(panel, label="Volume:")
        volume_label.SetForegroundColour(wx.Colour(255, 255, 255))
        volume_sizer.Add(volume_label, flag=wx.ALL, border=5)
        
        self.volume_slider = wx.Slider(panel, value=50, minValue=0, maxValue=100,
                                       style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        volume_sizer.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=5)
        
        main_sizer.Add(volume_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        # Controls info
        controls_box = wx.StaticBox(panel, label="Controls")
        controls_sizer = wx.StaticBoxSizer(controls_box, wx.VERTICAL)
        
        controls_text = wx.StaticText(panel, 
            label="W/S - Move left paddle\n"
                  "Right paddle is AI-controlled\n"
                  "Space - Pause/Resume\n"
                  "ESC - Open menu")
        controls_text.SetForegroundColour(wx.Colour(255, 255, 255))
        controls_sizer.Add(controls_text, flag=wx.ALL, border=10)
        
        main_sizer.Add(controls_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        pause_button = wx.Button(panel, label="Pause")
        pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
        button_sizer.Add(pause_button, flag=wx.ALL, border=5)
        
        reset_button = wx.Button(panel, label="Reset Game")
        reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        button_sizer.Add(reset_button, flag=wx.ALL, border=5)
        
        close_button = wx.Button(panel, label="Close Menu")
        close_button.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        button_sizer.Add(close_button, flag=wx.ALL, border=5)
        
        main_sizer.Add(button_sizer, flag=wx.ALL | wx.CENTER, border=10)
        
        panel.SetSizer(main_sizer)
        
        # Center on parent
        self.CentreOnParent()
    
    def on_volume_change(self, event):
        """Handle volume slider change"""
        self.volume_value = self.volume_slider.GetValue()
        logger.info(f"Volume changed to {self.volume_value}")
        # TODO: Update audio volume when audio system is implemented
    
    def update_pause_button(self):
        """Update pause button label based on game state"""
        if self.game.game_state == 'paused':
            self.pause_button.SetLabel("Resume")
        else:
            self.pause_button.SetLabel("Pause")
    
    def on_pause(self, event):
        """Handle pause button"""
        self.game.pause()
        self.update_pause_button()
    
    def on_reset(self, event):
        """Handle reset button"""
        self.game.reset_game()
        self.update_pause_button()
        self.Close()

