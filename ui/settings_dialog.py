"""Settings dialog for audio sensitivity"""

import wx
import logging

logger = logging.getLogger(__name__)


class SettingsDialog(wx.Dialog):
    """Settings dialog for audio sensitivity"""
    
    def __init__(self, parent, audio_input=None, settings=None):
        super().__init__(parent, title="Settings", size=(450, 300))
        
        self.audio_input = audio_input
        self.settings = settings
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sensitivity_label = wx.StaticText(panel, label="Audio Sensitivity:")
        sensitivity_label.SetForegroundColour(wx.Colour(200, 200, 200))
        sizer.Add(sensitivity_label, 0, wx.ALIGN_CENTER | wx.TOP, 40)
        
        current_threshold = 0.02
        if self.audio_input:
            current_threshold = self.audio_input.noise_threshold
        elif self.settings:
            current_threshold = self.settings.get_audio_sensitivity()
        
        min_threshold = 0.001
        max_threshold = 0.5
        slider_value = int(((current_threshold - min_threshold) / (max_threshold - min_threshold)) * 100)
        slider_value = max(0, min(100, slider_value))
        
        self.sensitivity_slider = wx.Slider(panel, value=slider_value, minValue=0, maxValue=100,
                                            size=(380, 60),
                                            style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sensitivity_slider.Bind(wx.EVT_SLIDER, self.on_sensitivity_change)
        sizer.Add(self.sensitivity_slider, 0, wx.ALIGN_CENTER | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(panel, label="OK", size=(130, 40))
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        ok_btn.SetDefault()
        button_sizer.Add(ok_btn, 0, wx.ALL, 15)
        
        cancel_btn = wx.Button(panel, label="Cancel", size=(130, 40))
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_sizer.Add(cancel_btn, 0, wx.ALL, 15)
        
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)
        
        panel.SetSizer(sizer)
        self.Centre()
    
    def on_sensitivity_change(self, event):
        """Handle sensitivity slider change"""
        slider_value = self.sensitivity_slider.GetValue()
        min_threshold = 0.001
        max_threshold = 0.5
        threshold = min_threshold + (slider_value / 100.0) * (max_threshold - min_threshold)
        
        if self.audio_input:
            self.audio_input.noise_threshold = threshold
        
        if self.settings:
            self.settings.set_audio_sensitivity(threshold)
        
        logger.info(f"Audio sensitivity changed to threshold={threshold:.4f}")
    
    def on_ok(self, event):
        """Confirm and apply settings, then close dialog"""
        logger.info("Settings confirmed and applied")
        self.EndModal(wx.ID_OK)
    
    def on_cancel(self, event):
        """Cancel changes and close dialog"""
        logger.info("Settings dialog cancelled")
        self.EndModal(wx.ID_CANCEL)

