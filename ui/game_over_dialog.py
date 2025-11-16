"""Game over dialog with optional high score entry"""

import wx


class GameOverDialog(wx.Dialog):
    """Game over dialog with optional high score entry"""
    
    def __init__(self, parent, score, is_high_score=False):
        title = "New High Score!" if is_high_score else "Game Over"
        super().__init__(parent, title=title, size=(350, 200))
        
        self.score = score
        self.is_high_score = is_high_score
        self.name = ""
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        if is_high_score:
            title_text = wx.StaticText(panel, label="NEW HIGH SCORE!")
            title_text.SetForegroundColour(wx.Colour(255, 215, 0))
        else:
            title_text = wx.StaticText(panel, label="GAME OVER")
            title_text.SetForegroundColour(wx.Colour(255, 255, 255))
        
        title_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text.SetFont(title_font)
        sizer.Add(title_text, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        score_text = wx.StaticText(panel, label=f"Score: {score}")
        score_text.SetForegroundColour(wx.Colour(200, 200, 200))
        score_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        score_text.SetFont(score_font)
        sizer.Add(score_text, 0, wx.ALIGN_CENTER | wx.TOP, 15)
        
        if is_high_score:
            name_label = wx.StaticText(panel, label="Enter your name:")
            name_label.SetForegroundColour(wx.Colour(200, 200, 200))
            sizer.Add(name_label, 0, wx.ALIGN_CENTER | wx.TOP, 20)
            
            self.name_entry = wx.TextCtrl(panel, value="Player", size=(200, 30))
            sizer.Add(self.name_entry, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(panel, label="OK", size=(100, 35))
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        ok_btn.SetDefault()
        button_sizer.Add(ok_btn, 0, wx.ALL, 10)
        
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        
        panel.SetSizer(sizer)
        self.Centre()
    
    def on_ok(self, event):
        """Handle OK button"""
        if self.is_high_score:
            self.name = self.name_entry.GetValue().strip()
            if not self.name:
                self.name = "Anonymous"
        self.EndModal(wx.ID_OK)
    
    def get_name(self):
        """Get entered name"""
        return self.name

