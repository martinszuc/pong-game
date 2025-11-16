import wx

DIALOG_WIDTH = 500
DIALOG_HEIGHT = 400
DEFAULT_NAME = "Player"
ANONYMOUS_NAME = "Anonymous"


class GameOverDialog(wx.Dialog):
    def __init__(self, parent, score, is_high_score=False):
        title = "New High Score!" if is_high_score else "Game Over"
        super().__init__(parent, title=title, size=(DIALOG_WIDTH, DIALOG_HEIGHT))

        self.score = score
        self.is_high_score = is_high_score
        self.name = ""

        self.SetBackgroundColour(wx.Colour(40, 40, 40))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(50)

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

        score_text = wx.StaticText(self, label=f"Score: {score}")
        score_text.SetForegroundColour(wx.Colour(200, 200, 200))
        score_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        score_text.SetFont(score_font)
        main_sizer.Add(score_text, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        main_sizer.AddSpacer(60)

        if is_high_score:
            self.name_entry = wx.TextCtrl(self, value=DEFAULT_NAME, size=(300, 38))
            self.name_entry.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            main_sizer.Add(self.name_entry, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
            main_sizer.AddSpacer(60)
        else:
            main_sizer.AddSpacer(60)

        ok_btn = wx.Button(self, label="OK", size=(130, 45))
        ok_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        main_sizer.Add(ok_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        main_sizer.AddSpacer(50)

        self.SetSizer(main_sizer)
        self.Layout()
        self.Centre()

    def on_ok(self, event):
        if self.is_high_score:
            self.name = self.name_entry.GetValue().strip()
            if not self.name:
                self.name = ANONYMOUS_NAME
        self.EndModal(wx.ID_OK)

    def get_name(self):
        return self.name