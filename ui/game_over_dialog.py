"""Game over dialog with optional high score entry"""

import wx


class GameOverDialog(wx.Dialog):
    """Game over dialog with optional high score entry"""
    
    def __init__(self, parent, score, is_high_score=False):
        title = "New High Score!" if is_high_score else "Game Over"
        super().__init__(parent, title=title, size=(500, 400))

        self.score = score
        self.is_high_score = is_high_score
        self.name = ""

        self.SetBackgroundColour(wx.Colour(40, 40, 40))

        # main vertical sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # top spacer
        main_sizer.AddSpacer(50)

        # title
        if is_high_score:
            title_text = wx.StaticText(self, label="NEW HIGH SCORE!")
            title_text.SetForegroundColour(wx.Colour(255, 215, 0))
        else:
            title_text = wx.StaticText(self, label="GAME OVER")
            title_text.SetForegroundColour(wx.Colour(255, 255, 255))

        title_font = wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text.SetFont(title_font)
        main_sizer.Add(title_text, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        main_sizer.AddSpacer(30)

        # score
        score_text = wx.StaticText(self, label=f"Score: {score}")
        score_text.SetForegroundColour(wx.Colour(200, 200, 200))
        score_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        score_text.SetFont(score_font)
        main_sizer.Add(score_text, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        main_sizer.AddSpacer(60)

        # text entry for high score (NO LABEL)
        if is_high_score:
            self.name_entry = wx.TextCtrl(self, value="Player", size=(300, 38))
            self.name_entry.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            main_sizer.Add(self.name_entry, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

            main_sizer.AddSpacer(60)
        else:
            main_sizer.AddSpacer(60)

        # ok button
        ok_btn = wx.Button(self, label="OK", size=(130, 45))
        ok_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        main_sizer.Add(ok_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # bottom spacer
        main_sizer.AddSpacer(50)

        self.SetSizer(main_sizer)
        self.Layout()
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