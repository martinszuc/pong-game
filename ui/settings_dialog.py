import wx
import logging
import platform
from .audio_calibration_dialog import AudioCalibrationDialog

logger = logging.getLogger(__name__)

# Linux/Windows need more space due to different font rendering
DIALOG_WIDTH = 700 if platform.system() != 'Darwin' else 600
DIALOG_HEIGHT = 750 if platform.system() != 'Darwin' else 650
SLIDER_WIDTH = 380
SLIDER_HEIGHT = 60
SLIDER_MIN = 0
SLIDER_MAX = 100
MIN_THRESHOLD = 0.001
MAX_THRESHOLD = 0.5
DEFAULT_THRESHOLD = 0.02


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, audio_input=None, settings=None, game=None, renderer=None):
        super().__init__(parent, title="Settings", 
                        size=(DIALOG_WIDTH, DIALOG_HEIGHT),
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.audio_input = audio_input
        self.settings = settings
        self.game = game
        self.renderer = renderer
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # title
        title_label = wx.StaticText(panel, label="Game Settings")
        title_font = title_label.GetFont()
        title_font.PointSize += 4
        title_font = title_font.Bold()
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(255, 255, 255))
        sizer.Add(title_label, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        sizer.AddSpacer(20)
        
        # ===== CONTROL MODE =====
        control_label = wx.StaticText(panel, label="Control Mode:")
        control_label.SetForegroundColour(wx.Colour(255, 255, 255))
        control_font = control_label.GetFont()
        control_font.PointSize += 1
        control_font = control_font.Bold()
        control_label.SetFont(control_font)
        sizer.Add(control_label, 0, wx.ALL, 10)
        
        current_mode = self.settings.get_control_mode() if self.settings else 'audio'
        
        self.audio_radio = wx.RadioButton(panel, label="Audio (Microphone)", style=wx.RB_GROUP)
        self.audio_radio.SetForegroundColour(wx.Colour(200, 200, 200))
        self.audio_radio.SetValue(current_mode == 'audio')
        sizer.Add(self.audio_radio, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        self.keyboard_radio = wx.RadioButton(panel, label="Keyboard (Arrow Keys / WASD)")
        self.keyboard_radio.SetForegroundColour(wx.Colour(200, 200, 200))
        self.keyboard_radio.SetValue(current_mode == 'keyboard')
        sizer.Add(self.keyboard_radio, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        sizer.AddSpacer(10)
        
        # ===== AUDIO SENSITIVITY =====
        audio_label = wx.StaticText(panel, label="Audio Sensitivity:")
        audio_label.SetForegroundColour(wx.Colour(255, 255, 255))
        audio_font = audio_label.GetFont()
        audio_font.PointSize += 1
        audio_font = audio_font.Bold()
        audio_label.SetFont(audio_font)
        sizer.Add(audio_label, 0, wx.ALL, 10)
        
        sensitivity_label = wx.StaticText(panel, label="Threshold (how loud to move paddle up):")
        sensitivity_label.SetForegroundColour(wx.Colour(200, 200, 200))
        sizer.Add(sensitivity_label, 0, wx.LEFT | wx.RIGHT, 10)
        
        current_threshold = DEFAULT_THRESHOLD
        if self.audio_input:
            current_threshold = self.audio_input.noise_threshold
        elif self.settings:
            current_threshold = self.settings.get_audio_sensitivity()
        
        slider_value = int(((current_threshold - MIN_THRESHOLD) / (MAX_THRESHOLD - MIN_THRESHOLD)) * 100)
        slider_value = max(SLIDER_MIN, min(SLIDER_MAX, slider_value))
        
        self.sensitivity_slider = wx.Slider(panel, value=slider_value, minValue=SLIDER_MIN, maxValue=SLIDER_MAX,
                                            style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sensitivity_slider.Bind(wx.EVT_SLIDER, self.on_sensitivity_change)
        sizer.Add(self.sensitivity_slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        calibrate_btn = wx.Button(panel, label="Run Calibration Wizard", size=(200, 35))
        calibrate_btn.Bind(wx.EVT_BUTTON, self.on_calibrate)
        sizer.Add(calibrate_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        sizer.AddSpacer(10)
        
        # ===== DIFFICULTY =====
        difficulty_label = wx.StaticText(panel, label="Difficulty:")
        difficulty_label.SetForegroundColour(wx.Colour(255, 255, 255))
        difficulty_font = difficulty_label.GetFont()
        difficulty_font.PointSize += 1
        difficulty_font = difficulty_font.Bold()
        difficulty_label.SetFont(difficulty_font)
        sizer.Add(difficulty_label, 0, wx.ALL, 10)
        
        current_difficulty = self.settings.get_difficulty() if self.settings else 'medium'
        
        difficulties = ['easy', 'medium', 'hard']
        self.difficulty_choice = wx.Choice(panel, choices=[d.capitalize() for d in difficulties])
        try:
            self.difficulty_choice.SetSelection(difficulties.index(current_difficulty))
        except ValueError:
            self.difficulty_choice.SetSelection(1)  # default to medium
        sizer.Add(self.difficulty_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        sizer.AddSpacer(10)
        
        # ===== COLOR THEME =====
        theme_label = wx.StaticText(panel, label="Color Theme:")
        theme_label.SetForegroundColour(wx.Colour(255, 255, 255))
        theme_font = theme_label.GetFont()
        theme_font.PointSize += 1
        theme_font = theme_font.Bold()
        theme_label.SetFont(theme_font)
        sizer.Add(theme_label, 0, wx.ALL, 10)
        
        from visuals.themes import get_theme_names, THEMES
        current_theme = self.settings.get_color_theme() if self.settings else 'classic'
        
        theme_names = get_theme_names()
        theme_display_names = [THEMES[name]['name'] for name in theme_names]
        self.theme_choice = wx.Choice(panel, choices=theme_display_names)
        self.theme_choice.SetSelection(theme_names.index(current_theme))
        sizer.Add(self.theme_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # ===== BUTTONS =====
        sizer.AddSpacer(20)  # extra space before buttons
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()
        
        apply_btn = wx.Button(panel, label="Apply", size=(130, 45))
        apply_font = apply_btn.GetFont()
        apply_font.PointSize += 1
        apply_btn.SetFont(apply_font)
        apply_btn.Bind(wx.EVT_BUTTON, self.on_apply)
        button_sizer.Add(apply_btn, 0, wx.ALL, 8)
        
        ok_btn = wx.Button(panel, label="OK", size=(130, 45))
        ok_font = ok_btn.GetFont()
        ok_font.PointSize += 1
        ok_btn.SetFont(ok_font)
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        ok_btn.SetDefault()
        button_sizer.Add(ok_btn, 0, wx.ALL, 8)
        
        cancel_btn = wx.Button(panel, label="Cancel", size=(130, 45))
        cancel_font = cancel_btn.GetFont()
        cancel_font.PointSize += 1
        cancel_btn.SetFont(cancel_font)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_sizer.Add(cancel_btn, 0, wx.ALL, 8)
        
        button_sizer.AddStretchSpacer()
        
        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 15)
        
        panel.SetSizer(sizer)
        self.Centre()
    
    def on_sensitivity_change(self, event):
        slider_value = self.sensitivity_slider.GetValue()
        threshold = MIN_THRESHOLD + (slider_value / 100.0) * (MAX_THRESHOLD - MIN_THRESHOLD)
        
        if self.audio_input:
            self.audio_input.noise_threshold = threshold
        
        if self.settings:
            self.settings.set_audio_sensitivity(threshold)
        
        logger.info(f"Audio sensitivity changed to threshold={threshold:.4f}")
    
    def on_calibrate(self, event):
        """open the audio calibration wizard"""
        if not self.audio_input:
            wx.MessageBox("Audio input not available", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        dialog = AudioCalibrationDialog(self, self.audio_input, self.settings)
        result = dialog.ShowModal()
        dialog.Destroy()
        
        if result == wx.ID_OK:
            # update slider to reflect new calibrated value
            current_threshold = self.settings.get_audio_sensitivity()
            slider_value = int(((current_threshold - MIN_THRESHOLD) / (MAX_THRESHOLD - MIN_THRESHOLD)) * 100)
            slider_value = max(SLIDER_MIN, min(SLIDER_MAX, slider_value))
            self.sensitivity_slider.SetValue(slider_value)
    
    def on_apply(self, event):
        """apply settings without closing dialog"""
        self._apply_all_settings()
        
        # update menu theme immediately
        parent_frame = self.GetParent()
        if hasattr(parent_frame, 'apply_theme_to_menu'):
            parent_frame.apply_theme_to_menu()
        
        # show confirmation
        wx.MessageBox("Settings applied successfully!", "Applied", wx.OK | wx.ICON_INFORMATION, self)
    
    def _apply_all_settings(self):
        """internal method to apply all settings"""
        # save control mode
        if self.audio_radio.GetValue():
            self.settings.set_control_mode('audio')
        else:
            self.settings.set_control_mode('keyboard')
        
        # save difficulty
        from visuals.themes import get_theme_names
        difficulties = ['easy', 'medium', 'hard']
        selected_difficulty = difficulties[self.difficulty_choice.GetSelection()]
        self.settings.set_difficulty(selected_difficulty)
        
        # apply difficulty to game if available
        if self.game:
            self.game.set_difficulty(selected_difficulty)
        
        # save theme
        theme_names = get_theme_names()
        selected_theme = theme_names[self.theme_choice.GetSelection()]
        self.settings.set_color_theme(selected_theme)
        
        # apply theme to renderer if available
        if self.renderer:
            self.renderer.set_theme(selected_theme)
        
        logger.info("Settings applied")
    
    def on_ok(self, event):
        """apply all settings and close"""
        self._apply_all_settings()
        
        # update menu theme immediately
        parent_frame = self.GetParent()
        if hasattr(parent_frame, 'apply_theme_to_menu'):
            parent_frame.apply_theme_to_menu()
        
        logger.info("Settings confirmed and dialog closed")
        self.EndModal(wx.ID_OK)
    
    def on_cancel(self, event):
        logger.info("Settings dialog cancelled")
        self.EndModal(wx.ID_CANCEL)

