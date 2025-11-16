import wx
import cv2
import logging
import platform

from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)

GAME_WIDTH = 800
GAME_HEIGHT = 600
FRAME_WIDTH = 4
PADDING = 20
TITLE_BAR_HEIGHT_MACOS = 40
TITLE_BAR_HEIGHT_OTHER = 30
KEY_TIMER_INTERVAL_MS = 50
TOP_SCORES_COUNT = 5
MAX_NAME_DISPLAY_LENGTH = 15


class PongFrame(wx.Frame):
    def __init__(self, game, renderer, on_close_callback=None, 
                 lighting=None, audio_input=None, settings=None):
        self.game_width = GAME_WIDTH
        self.game_height = GAME_HEIGHT
        self.frame_width = FRAME_WIDTH
        
        title_bar_height = TITLE_BAR_HEIGHT_MACOS if platform.system() == 'Darwin' else TITLE_BAR_HEIGHT_OTHER
        window_width = self.game_width + (self.frame_width * 2) + (PADDING * 2)
        window_height = self.game_height + (self.frame_width * 2) + (PADDING * 2) + title_bar_height
        
        super().__init__(None, title="Audio-Controlled Pong Game", 
                        size=(window_width, window_height))
        
        self.game = game
        self.renderer = renderer
        self.on_close_callback = on_close_callback
        self.lighting = lighting
        self.audio_input = audio_input
        self.settings = settings
        self.game_mode = 'voice_ai'
        self.current_game_score = 0
        
        from utils.high_scores import HighScoreManager
        self.high_score_manager = HighScoreManager()
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        self.panel = panel
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.card_sizer = wx.BoxSizer(wx.VERTICAL)
        self.menu_panel = self.create_menu_panel(panel)
        self.game_panel = self.create_game_panel(panel)
        self.game_over_panel = self.create_game_over_panel(panel)
        
        self.card_sizer.Add(self.menu_panel, 1, wx.EXPAND)
        self.card_sizer.Add(self.game_panel, 1, wx.EXPAND)
        
        main_sizer.Add(self.card_sizer, 1, wx.EXPAND | wx.ALL, PADDING)
        panel.SetSizer(main_sizer)
        
        self.game_over_panel.Reparent(self.game_panel)
        self.game_over_panel.SetPosition((0, 0))
        self.game_over_panel.SetSize(self.game_panel.GetSize())
        
        self.Centre()
        self.show_menu_panel()
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        
        self.key_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_movement_keys, self.key_timer)
        self.key_timer.Start(KEY_TIMER_INTERVAL_MS)
        
        self.Show()
        self.SetFocus()
    
    def create_menu_panel(self, parent):
        menu_panel = wx.Panel(parent)
        menu_panel.SetBackgroundColour(wx.Colour(30, 30, 30))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(menu_panel, label="PONG GAME")
        title_font = wx.Font(48, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 50)
        
        start_btn = wx.Button(menu_panel, label="START GAME", size=(200, 50))
        start_btn.Bind(wx.EVT_BUTTON, self.on_start_game)
        sizer.Add(start_btn, 0, wx.ALIGN_CENTER | wx.TOP, 50)
        
        settings_btn = wx.Button(menu_panel, label="SETTINGS", size=(200, 50))
        settings_btn.Bind(wx.EVT_BUTTON, self.on_settings)
        sizer.Add(settings_btn, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        high_scores_label = wx.StaticText(menu_panel, label="HIGH SCORES")
        high_scores_label.SetForegroundColour(wx.Colour(255, 215, 0))
        high_scores_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        high_scores_label.SetFont(high_scores_font)
        sizer.Add(high_scores_label, 0, wx.ALIGN_CENTER | wx.TOP, 30)
        
        self.high_scores_text = wx.StaticText(menu_panel, label="")
        self.high_scores_text.SetForegroundColour(wx.Colour(200, 200, 200))
        scores_font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.high_scores_text.SetFont(scores_font)
        sizer.Add(self.high_scores_text, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        self.update_high_scores_display()
        
        menu_panel.SetSizer(sizer)
        return menu_panel
    
    def update_high_scores_display(self):
        self.high_score_manager.load_scores()
        top_scores = self.high_score_manager.get_top_scores(TOP_SCORES_COUNT)
        if top_scores:
            scores_lines = []
            for i, s in enumerate(top_scores):
                rank = f"{i+1}."
                name = s['name'][:MAX_NAME_DISPLAY_LENGTH]
                score = s['score']
                scores_lines.append(f"{rank:4} {name:15} {score:6}")
            scores_text = "\n".join(scores_lines)
        else:
            scores_text = "No scores yet"
        self.high_scores_text.SetLabel(scores_text)
        logger.info(f"Updated high scores display: {top_scores}")
    
    def create_game_over_panel(self, parent):
        overlay_panel = wx.Panel(parent)
        overlay_panel.SetBackgroundColour(wx.Colour(20, 20, 20))
        overlay_panel.Hide()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer()
        
        self.game_over_title = wx.StaticText(overlay_panel, label="GAME OVER")
        self.game_over_title.SetForegroundColour(wx.Colour(255, 255, 255))
        title_font = wx.Font(48, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.game_over_title.SetFont(title_font)
        sizer.Add(self.game_over_title, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        name_container_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_container_sizer.AddStretchSpacer()
        
        self.game_over_name_entry = wx.TextCtrl(overlay_panel, value="Player", size=(300, 40), style=wx.TE_PROCESS_ENTER)
        self.game_over_name_entry.Hide()
        self.game_over_name_entry.Bind(wx.EVT_TEXT_ENTER, self.on_game_over_ok)
        name_container_sizer.Add(self.game_over_name_entry, 0, wx.ALIGN_CENTER_VERTICAL)
        
        name_container_sizer.AddStretchSpacer()
        sizer.Add(name_container_sizer, 0, wx.EXPAND | wx.TOP, 30)
        
        self.game_over_score = wx.StaticText(overlay_panel, label="Score: 0")
        self.game_over_score.SetForegroundColour(wx.Colour(200, 200, 200))
        score_font = wx.Font(32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.game_over_score.SetFont(score_font)
        sizer.Add(self.game_over_score, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.game_over_ok_btn = wx.Button(overlay_panel, label="OK", size=(150, 50))
        self.game_over_ok_btn.Bind(wx.EVT_BUTTON, self.on_game_over_ok)
        self.game_over_ok_btn.SetDefault()
        button_sizer.Add(self.game_over_ok_btn, 0, wx.ALL, 15)
        
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.TOP, 30)
        sizer.AddStretchSpacer()
        
        overlay_panel.SetSizer(sizer)
        return overlay_panel
    
    def create_game_panel(self, parent):
        game_panel = wx.Panel(parent)
        game_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.AddSpacer(self.frame_width)
        
        inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        inner_sizer.AddSpacer(self.frame_width)
        
        bitmap_panel = wx.Panel(game_panel)
        bitmap_panel.SetBackgroundColour(wx.Colour(0, 0, 0))
        bitmap_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.display_bitmap = wx.StaticBitmap(bitmap_panel, size=(self.game_width, self.game_height))
        self.display_bitmap.SetBackgroundColour(wx.Colour(0, 0, 0))
        bitmap_sizer.Add(self.display_bitmap, 0, wx.CENTER)
        bitmap_panel.SetSizer(bitmap_sizer)
        
        inner_sizer.Add(bitmap_panel, 0, wx.CENTER)
        inner_sizer.AddSpacer(self.frame_width)
        
        outer_sizer.Add(inner_sizer, 1, wx.CENTER)
        outer_sizer.AddSpacer(self.frame_width)
        
        game_panel.SetSizer(outer_sizer)
        return game_panel
    
    def show_menu_panel(self):
        self.menu_panel.Show()
        self.game_panel.Hide()
        self.game_over_panel.Hide()
        self.panel.Layout()
    
    def show_game_panel(self):
        self.menu_panel.Hide()
        self.game_panel.Show()
        self.game_over_panel.Hide()
        self.panel.Layout()
        if self.game_over_panel.GetParent() == self.game_panel:
            self.game_over_panel.SetSize(self.game_panel.GetSize())
    
    def show_game_over_panel(self):
        if not self.game_panel.IsShown():
            self.show_game_panel()
        
        game_panel_size = self.game_panel.GetSize()
        self.game_over_panel.SetSize(game_panel_size)
        self.game_over_panel.SetPosition((0, 0))
        self.game_over_panel.Show()
        self.game_over_panel.Raise()
        self.game_over_panel.Update()
        self.game_over_panel.SetFocus()
        self.game_panel.Refresh()
        self.Refresh()
        self.Update()
    
    def on_start_game(self, event):
        if hasattr(self, '_game_over_handled'):
            delattr(self, '_game_over_handled')
        
        self.game_mode = 'voice_ai'
        self.game.start_game()
        self.show_game_panel()
        self.SetFocus()
    
    def check_game_over(self):
        if self.game.game_state == 'game_over' and not hasattr(self, '_game_over_handled'):
            self._game_over_handled = True
            score = self.game.bounce_count
            self.current_game_score = score
            is_high_score = self.high_score_manager.is_high_score(score)
            wx.CallAfter(self._show_game_over_overlay, score, is_high_score)
        elif self.game.game_state != 'game_over':
            if hasattr(self, '_game_over_handled'):
                self._game_over_handled = False
    
    def _show_game_over_overlay(self, score, is_high_score):
        if not self.game_panel.IsShown():
            self.show_game_panel()
        
        self.game_over_score.SetLabel(f"Score: {score}")
        
        if is_high_score:
            self.game_over_title.SetLabel("NEW HIGH SCORE!")
            self.game_over_title.SetForegroundColour(wx.Colour(255, 215, 0))
            self.game_over_name_entry.Show()
            self.game_over_name_entry.SetValue("Player")
            self.game_over_ok_btn.SetLabel("OK")
        else:
            self.game_over_title.SetLabel("GAME OVER")
            self.game_over_title.SetForegroundColour(wx.Colour(255, 255, 255))
            self.game_over_name_entry.Hide()
            self.game_over_ok_btn.SetLabel("Main Menu")
        
        self.show_game_over_panel()
        self.game_over_panel.Layout()
        self.Layout()
        self.Refresh()
        if is_high_score:
            self.game_over_name_entry.SetFocus()
        self.SetFocus()
    
    def on_game_over_ok(self, event):
        score = self.current_game_score
        
        if self.game_over_name_entry.IsShown():
            name = self.game_over_name_entry.GetValue().strip()
            if not name:
                name = "Anonymous"
            logger.info(f"Saving high score: {name} - {score}")
            self.high_score_manager.add_score(name, score)
            logger.info(f"High scores after save: {self.high_score_manager.scores}")
            self.high_score_manager.load_scores()
            logger.info(f"High scores after reload: {self.high_score_manager.scores}")
        
        self.game_over_panel.Hide()
        self.game.to_menu()
        self.show_menu_panel()
        self.update_high_scores_display()
        self.SetFocus()
    
    def on_settings(self, event):
        dialog = SettingsDialog(self, self.audio_input, self.settings)
        dialog.ShowModal()
        dialog.Destroy()
    
    def on_key(self, event):
        key = event.GetUnicodeKey()
        if key == wx.WXK_NONE:
            key = event.GetKeyCode()
        
        if self.game_over_panel.IsShown():
            if key == wx.WXK_ESCAPE:
                self.on_game_over_ok(event)
                return
            event.Skip()
            return
        
        if self.game.game_state == 'menu':
            if key == wx.WXK_ESCAPE:
                self.Close()
            else:
                event.Skip()
            return
        
        if key == wx.WXK_ESCAPE:
            self.game.to_menu()
            self.show_menu_panel()
            return
        
        if key == wx.WXK_SPACE:
            self.game.pause()
            return
        
        if key == ord('R') or key == ord('r'):
            self.game.reset_game()
            return
        
        event.Skip()
    
    def check_movement_keys(self, event):
        self.check_game_over()
    
    def on_close(self, event):
        if hasattr(self, 'key_timer'):
            self.key_timer.Stop()
        if self.on_close_callback:
            self.on_close_callback()
        self.Destroy()
    
    def update_display(self, frame):
        try:
            if self.game.game_state in ['playing', 'paused', 'game_over']:
                if not self.game_panel.IsShown():
                    self.show_game_panel()
                
                if frame is None:
                    logger.warning("Received None frame, skipping display update")
                    return
                
                height, width = frame.shape[:2]
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                wx_image = wx.Image(width, height)
                wx_image.SetData(rgb_frame.tobytes())
                bitmap = wx.Bitmap(wx_image)
                self.display_bitmap.SetBitmap(bitmap)
                self.display_bitmap.Refresh()
        except Exception as e:
            logger.error(f"Error updating display: {e}", exc_info=True)

