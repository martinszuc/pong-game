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
TITLE_BAR_HEIGHT_LINUX = 50  # Linux needs more space for window decorations
TITLE_BAR_HEIGHT_WINDOWS = 30
AUDIO_VIZ_HEIGHT_MACOS = 50  # height of audio visualization bar on macOS
AUDIO_VIZ_HEIGHT_LINUX = 100  # Linux needs more height for audio viz
KEY_TIMER_INTERVAL_MS = 50
TOP_SCORES_COUNT = 5
MAX_NAME_DISPLAY_LENGTH = 15


class PongFrame(wx.Frame):
    def __init__(self, game, renderer, on_close_callback=None, 
                 lighting=None, audio_input=None, settings=None):
        self.game_width = GAME_WIDTH
        self.game_height = GAME_HEIGHT
        self.frame_width = FRAME_WIDTH
        
        # platform-specific dimensions (Linux needs more space for font rendering)
        if platform.system() == 'Darwin':
            title_bar_height = TITLE_BAR_HEIGHT_MACOS
            audio_viz_height = AUDIO_VIZ_HEIGHT_MACOS
            extra_width = 0  # macOS is fine as is
        else:  # Linux
            title_bar_height = TITLE_BAR_HEIGHT_LINUX
            audio_viz_height = AUDIO_VIZ_HEIGHT_LINUX
            extra_width = 100  # Linux needs more width
        
        window_width = self.game_width + (self.frame_width * 2) + (PADDING * 2) + extra_width
        # add extra height for audio visualization bar and title bar
        window_height = self.game_height + (self.frame_width * 2) + (PADDING * 2) + title_bar_height + audio_viz_height + 20
        
        # on Linux, make window resizable to handle different DPI/scaling
        style = wx.DEFAULT_FRAME_STYLE if platform.system() == 'Linux' else wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER
        
        super().__init__(None, title="Audio-Controlled Pong Game", 
                        size=(window_width, window_height),
                        style=style)
        
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
        
        # keyboard control state (for Linux/Windows where GetKeyState doesn't work)
        self.keyboard_up_pressed = False
        self.keyboard_down_pressed = False
        self.use_key_events = platform.system() == 'Linux'  # Linux needs event-based input
        
        self.key_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_movement_keys, self.key_timer)
        self.key_timer.Start(KEY_TIMER_INTERVAL_MS)
        
        self.Show()
        self.SetFocus()
        
        # start audio viz timer after window is shown (safer, only if audio viz exists)
        try:
            if hasattr(self, 'audio_viz_bar') and self.audio_viz_bar:
                self.audio_viz_timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.update_audio_viz, self.audio_viz_timer)
                self.audio_viz_timer.Start(50)
                logger.info("Audio visualization timer started")
        except Exception as e:
            logger.error(f"Error starting audio viz timer: {e}", exc_info=True)
            self.audio_viz_timer = None
        
        # apply initial theme to menu after window is shown (safer)
        wx.CallAfter(self.apply_theme_to_menu)
    
    def create_menu_panel(self, parent):
        menu_panel = wx.Panel(parent)
        self.menu_panel_widget = menu_panel  # store reference for theme updates
        menu_panel.SetBackgroundColour(wx.Colour(30, 30, 30))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.menu_title = wx.StaticText(menu_panel, label="PONG GAME")
        title_font = wx.Font(48, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.menu_title.SetFont(title_font)
        self.menu_title.SetForegroundColour(wx.Colour(255, 255, 255))
        sizer.Add(self.menu_title, 0, wx.ALIGN_CENTER | wx.TOP, 50)
        
        start_btn = wx.Button(menu_panel, label="START GAME", size=(200, 50))
        start_btn.Bind(wx.EVT_BUTTON, self.on_start_game)
        sizer.Add(start_btn, 0, wx.ALIGN_CENTER | wx.TOP, 50)
        
        settings_btn = wx.Button(menu_panel, label="SETTINGS", size=(200, 50))
        settings_btn.Bind(wx.EVT_BUTTON, self.on_settings)
        sizer.Add(settings_btn, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        self.high_scores_label = wx.StaticText(menu_panel, label="HIGH SCORES")
        self.high_scores_label.SetForegroundColour(wx.Colour(255, 215, 0))
        high_scores_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.high_scores_label.SetFont(high_scores_font)
        sizer.Add(self.high_scores_label, 0, wx.ALIGN_CENTER | wx.TOP, 30)
        
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
        game_panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # game display section
        game_display_sizer = wx.BoxSizer(wx.VERTICAL)
        game_display_sizer.AddSpacer(self.frame_width)
        
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
        
        game_display_sizer.Add(inner_sizer, 0, wx.CENTER)
        game_display_sizer.AddSpacer(self.frame_width)
        
        outer_sizer.Add(game_display_sizer, 0, wx.CENTER | wx.TOP, 10)
        
        # audio visualization widget (shows microphone level) - below game display
        try:
            outer_sizer.AddSpacer(5)
            
            self.audio_viz_panel = wx.Panel(game_panel)
            self.audio_viz_panel.SetBackgroundColour(wx.Colour(30, 30, 30))
            viz_sizer = wx.BoxSizer(wx.HORIZONTAL)
            viz_sizer.AddStretchSpacer()
            
            viz_label = wx.StaticText(self.audio_viz_panel, label="Mic Level:")
            viz_label.SetForegroundColour(wx.Colour(200, 200, 200))
            viz_font = viz_label.GetFont()
            viz_font.PointSize += 1
            viz_label.SetFont(viz_font)
            viz_sizer.Add(viz_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
            
            self.audio_viz_bar = wx.Gauge(self.audio_viz_panel, range=100, style=wx.GA_HORIZONTAL)
            self.audio_viz_bar.SetMinSize((250, 20))
            viz_sizer.Add(self.audio_viz_bar, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 8)
            
            self.audio_viz_text = wx.StaticText(self.audio_viz_panel, label="0.00")
            self.audio_viz_text.SetForegroundColour(wx.Colour(200, 200, 200))
            viz_text_font = self.audio_viz_text.GetFont()
            viz_text_font.PointSize += 1
            self.audio_viz_text.SetFont(viz_text_font)
            viz_sizer.Add(self.audio_viz_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
            
            viz_sizer.AddStretchSpacer()
            
            self.audio_viz_panel.SetSizer(viz_sizer)
            # platform-specific audio viz panel height
            if platform.system() == 'Linux':
                self.audio_viz_panel.SetMinSize((-1, 70))  # taller on Linux
            else:
                self.audio_viz_panel.SetMinSize((-1, 40))
            outer_sizer.Add(self.audio_viz_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

            logger.info("Audio visualization widget created")
        except Exception as e:
            logger.error(f"Error creating audio viz widget: {e}", exc_info=True)
            self.audio_viz_panel = None
            self.audio_viz_bar = None
            self.audio_viz_text = None
        
        # timer to update audio visualization (will start after window is shown)
        self.audio_viz_timer = None
        
        game_panel.SetSizer(outer_sizer)
        return game_panel
    
    def show_menu_panel(self):
        self.menu_panel.Show()
        self.game_panel.Hide()
        self.game_over_panel.Hide()
        self.panel.Layout()
        # apply theme when showing menu (in case it changed during gameplay)
        wx.CallAfter(self.apply_theme_to_menu)
    
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
    
    def apply_theme_to_menu(self):
        """apply current theme colors to the menu panel"""
        try:
            if not hasattr(self, 'renderer') or not self.renderer:
                return
            
            if not hasattr(self, 'menu_panel_widget') or not self.menu_panel_widget:
                return
            
            theme = self.renderer.theme
            if not theme:
                return
            
            # menu colors are already in RGB format (game colors are BGR for OpenCV)
            # no conversion needed for menu colors
            
            # update menu background
            bg_color = theme.get('menu_bg', (30, 30, 30))
            if bg_color and len(bg_color) == 3:
                self.menu_panel_widget.SetBackgroundColour(wx.Colour(bg_color[0], bg_color[1], bg_color[2]))
            
            # update title color
            title_color = theme.get('menu_title', (255, 255, 255))
            if title_color and len(title_color) == 3 and hasattr(self, 'menu_title'):
                self.menu_title.SetForegroundColour(wx.Colour(title_color[0], title_color[1], title_color[2]))
            
            # update high scores label color
            highlight_color = theme.get('menu_highlight', (255, 215, 0))
            if highlight_color and len(highlight_color) == 3 and hasattr(self, 'high_scores_label'):
                self.high_scores_label.SetForegroundColour(wx.Colour(highlight_color[0], highlight_color[1], highlight_color[2]))
            
            # update scores text color
            text_color = theme.get('menu_text', (200, 200, 200))
            if text_color and len(text_color) == 3 and hasattr(self, 'high_scores_text'):
                self.high_scores_text.SetForegroundColour(wx.Colour(text_color[0], text_color[1], text_color[2]))
            
            # refresh the panel
            self.menu_panel_widget.Refresh()
            self.panel.Layout()
        except Exception as e:
            logger.error(f"Error applying theme to menu: {e}", exc_info=True)
            # don't crash the game, just log the error
    
    def on_settings(self, event):
        dialog = SettingsDialog(self, self.audio_input, self.settings, self.game, self.renderer)
        result = dialog.ShowModal()
        dialog.Destroy()
        
        # theme is already applied by the dialog's on_apply/on_ok methods
    
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
        
        # handle game keys
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
        
        # handle movement keys (arrows + WASD)
        if key in [wx.WXK_UP, wx.WXK_DOWN, ord('W'), ord('w'), ord('S'), ord('s')]:
            if self.game.game_state == 'playing':
                # on Linux, use key events (GetKeyState doesn't work)
                if self.use_key_events:
                    control_mode = self.settings.get_control_mode() if self.settings else 'audio'
                    if control_mode == 'keyboard':
                        if key == wx.WXK_UP or key == ord('W') or key == ord('w'):
                            self.keyboard_up_pressed = True
                        elif key == wx.WXK_DOWN or key == ord('S') or key == ord('s'):
                            self.keyboard_down_pressed = True
                    return
                else:
                    # macOS/Windows: handled in check_movement_keys with GetKeyState
                    return
        
        event.Skip()
    
    def check_movement_keys(self, event):
        """check movement keys (arrows + WASD) for keyboard control and game over state"""
        # check for game over
        self.check_game_over()
        
        # handle keyboard controls if in keyboard mode
        if self.game.game_state == 'playing':
            control_mode = self.settings.get_control_mode() if self.settings else 'audio'
            if control_mode == 'keyboard':
                if self.use_key_events:
                    # Linux: use key press state (GetKeyState doesn't work on GTK)
                    if self.keyboard_up_pressed:
                        self.game.paddle_left.move_up()
                    elif self.keyboard_down_pressed:
                        self.game.paddle_left.move_down()
                    else:
                        self.game.paddle_left.stop()
                    
                    # reset states (will be set again by key event if still pressed)
                    self.keyboard_up_pressed = False
                    self.keyboard_down_pressed = False
                else:
                    # macOS/Windows: use GetKeyState (polling)
                    try:
                        keys = wx.GetKeyState
                        # check for up movement (arrow up or W)
                        if keys(wx.WXK_UP) or keys(ord('W')):
                            self.game.paddle_left.move_up()
                        # check for down movement (arrow down or S)
                        elif keys(wx.WXK_DOWN) or keys(ord('S')):
                            self.game.paddle_left.move_down()
                        else:
                            self.game.paddle_left.stop()
                    except Exception as e:
                        # if GetKeyState fails, fall back to event-based
                        logger.warning(f"GetKeyState failed, switching to event-based: {e}")
                        self.use_key_events = True
    
    def update_audio_viz(self, event):
        """update the audio visualization widget"""
        try:
            # check if widgets exist
            if not hasattr(self, 'audio_viz_bar') or not self.audio_viz_bar:
                return
            
            if self.audio_input and self.game.game_state == 'playing':
                # show audio viz during gameplay
                volume = self.audio_input.get_volume()
                self.audio_viz_bar.SetValue(int(volume * 100))
                if self.audio_viz_text:
                    self.audio_viz_text.SetLabel(f"{volume:.2f}")
                
                # change color based on threshold
                if volume > self.audio_input.noise_threshold:
                    self.audio_viz_bar.SetForegroundColour(wx.Colour(0, 255, 0))  # green when active
                else:
                    self.audio_viz_bar.SetForegroundColour(wx.Colour(100, 100, 100))  # gray when inactive
            else:
                self.audio_viz_bar.SetValue(0)
                if self.audio_viz_text:
                    self.audio_viz_text.SetLabel("--")
        except Exception as e:
            logger.error(f"Error updating audio viz: {e}")
    
    def on_close(self, event):
        # stop timers
        if hasattr(self, 'key_timer'):
            self.key_timer.Stop()
        if hasattr(self, 'audio_viz_timer') and self.audio_viz_timer.IsRunning():
            self.audio_viz_timer.Stop()
        
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

