"""
audio_calibration_dialog.py - Audio calibration wizard

This dialog helps users calibrate their microphone sensitivity by:
1. Testing background noise levels
2. Testing loud sounds (screaming/clapping)
3. Automatically setting the optimal threshold
"""

import wx
import logging
import time
import platform

logger = logging.getLogger(__name__)

# Linux/Windows need more space due to different font rendering
WIZARD_WIDTH = 750 if platform.system() in ['Linux', 'Windows'] else 650
WIZARD_HEIGHT = 750 if platform.system() in ['Linux', 'Windows'] else 600
TEST_DURATION = 3  # seconds to test each level


class AudioCalibrationDialog(wx.Dialog):
    """
    wizard-style dialog for calibrating microphone sensitivity
    
    guides the user through:
    - step 1: measure quiet (background noise)
    - step 2: measure loud (screaming/clapping)
    - step 3: calculate and apply optimal threshold
    """
    
    def __init__(self, parent, audio_input, settings):
        super().__init__(parent, title="Audio Calibration Wizard",
                        size=(WIZARD_WIDTH, WIZARD_HEIGHT),
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.audio_input = audio_input
        self.settings = settings
        
        # calibration state
        self.step = 0  # 0=intro, 1=quiet, 2=loud, 3=complete
        self.quiet_level = 0.0
        self.loud_level = 0.0
        self.timer = None
        self.test_start_time = 0
        self.test_samples = []
        
        self._init_ui()
        self.Center()
    
    def _init_ui(self):
        """create the wizard UI"""
        # main vertical sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # title
        self.title_label = wx.StaticText(self, label="Audio Calibration Wizard")
        title_font = self.title_label.GetFont()
        title_font.PointSize += 4
        title_font = title_font.Bold()
        self.title_label.SetFont(title_font)
        main_sizer.Add(self.title_label, 0, wx.ALL | wx.CENTER, 15)
        
        # instructions panel (changes per step)
        self.instructions = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        instruction_font = self.instructions.GetFont()
        instruction_font.PointSize += 2
        self.instructions.SetFont(instruction_font)
        main_sizer.Add(self.instructions, 0, wx.ALL | wx.EXPAND, 15)
        
        # volume level display
        volume_panel = wx.Panel(self)
        volume_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.volume_label = wx.StaticText(volume_panel, label="Current Volume:")
        volume_sizer.Add(self.volume_label, 0, wx.ALL | wx.CENTER, 5)
        
        self.volume_bar = wx.Gauge(volume_panel, range=100, style=wx.GA_HORIZONTAL)
        self.volume_bar.SetMinSize((450, 35))
        volume_sizer.Add(self.volume_bar, 0, wx.ALL | wx.CENTER, 5)
        
        self.volume_text = wx.StaticText(volume_panel, label="0.00")
        volume_sizer.Add(self.volume_text, 0, wx.ALL | wx.CENTER, 5)
        
        volume_panel.SetSizer(volume_sizer)
        main_sizer.Add(volume_panel, 0, wx.ALL | wx.CENTER, 10)
        
        # progress indicator (timer display)
        self.progress_label = wx.StaticText(self, label="")
        progress_font = self.progress_label.GetFont()
        progress_font.PointSize += 3
        progress_font = progress_font.Bold()
        self.progress_label.SetFont(progress_font)
        self.progress_label.SetForegroundColour(wx.Colour(0, 200, 0))  # green
        main_sizer.Add(self.progress_label, 0, wx.ALL | wx.CENTER, 10)
        
        # result display (hidden initially)
        self.result_panel = wx.Panel(self)
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.quiet_result = wx.StaticText(self.result_panel, label="")
        result_sizer.Add(self.quiet_result, 0, wx.ALL, 5)
        
        self.loud_result = wx.StaticText(self.result_panel, label="")
        result_sizer.Add(self.loud_result, 0, wx.ALL, 5)
        
        self.threshold_result = wx.StaticText(self.result_panel, label="")
        threshold_font = self.threshold_result.GetFont().Bold()
        self.threshold_result.SetFont(threshold_font)
        result_sizer.Add(self.threshold_result, 0, wx.ALL, 5)
        
        self.result_panel.SetSizer(result_sizer)
        self.result_panel.Hide()
        main_sizer.Add(self.result_panel, 0, wx.ALL | wx.CENTER, 10)
        
        # buttons
        main_sizer.AddSpacer(20)  # extra space before buttons
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()
        
        self.back_button = wx.Button(self, wx.ID_BACKWARD, "Back", size=(130, 45))
        back_font = self.back_button.GetFont()
        back_font.PointSize += 1
        self.back_button.SetFont(back_font)
        self.back_button.Bind(wx.EVT_BUTTON, self.on_back)
        self.back_button.Enable(False)
        button_sizer.Add(self.back_button, 0, wx.ALL, 8)
        
        self.next_button = wx.Button(self, wx.ID_FORWARD, "Start", size=(150, 45))
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next)
        next_font = self.next_button.GetFont()
        next_font.PointSize += 2
        next_font = next_font.Bold()
        self.next_button.SetFont(next_font)
        self.next_button.SetForegroundColour(wx.Colour(0, 120, 0))  # green text
        button_sizer.Add(self.next_button, 0, wx.ALL, 8)
        
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel", size=(130, 45))
        cancel_font = self.cancel_button.GetFont()
        cancel_font.PointSize += 1
        self.cancel_button.SetFont(cancel_font)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        button_sizer.Add(self.cancel_button, 0, wx.ALL, 8)
        
        button_sizer.AddStretchSpacer()
        
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 15)
        
        self.SetSizer(main_sizer)
        
        # show intro step
        self._show_intro()
    
    def _show_intro(self):
        """show the introduction step"""
        self.step = 0
        self.instructions.SetLabel(
            "This wizard will help you calibrate your microphone.\n\n"
            "You'll need to:\n"
            "1. Stay quiet for 3 seconds (measure background noise)\n"
            "2. Make loud sounds for 3 seconds (scream, clap, etc.)\n\n"
            "Click 'Start' when ready!"
        )
        self.progress_label.SetLabel("")
        self.next_button.SetLabel("Start")
        self.next_button.Enable(True)  # make sure button is enabled
        self.next_button.Show()  # make sure button is visible
        self.back_button.Enable(False)
        self.Layout()
    
    def _show_quiet_test(self):
        """show the quiet test step"""
        self.step = 1
        self.instructions.SetLabel(
            "Step 1: Quiet Test\n\n"
            "Stay quiet for 3 seconds...\n"
            "Measuring background noise level..."
        )
        self.progress_label.SetLabel("Starting test...")
        self.progress_label.SetForegroundColour(wx.Colour(255, 165, 0))  # orange during test
        self.next_button.Enable(False)
        self.test_samples = []
        self.test_start_time = time.time()
        
        # start timer to measure volume
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer.Start(50)  # update every 50ms
        
        self.Layout()
    
    def _show_loud_test(self):
        """show the loud test step"""
        self.step = 2
        self.instructions.SetLabel(
            "Step 2: Loud Test\n\n"
            "Make loud sounds for 3 seconds!\n"
            "Scream, clap, or yell as loud as you can!"
        )
        self.progress_label.SetLabel("Starting test...")
        self.progress_label.SetForegroundColour(wx.Colour(255, 0, 0))  # red during loud test
        self.next_button.Enable(False)
        self.test_samples = []
        self.test_start_time = time.time()
        
        # continue timer
        if not self.timer or not self.timer.IsRunning():
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_timer)
            self.timer.Start(50)
        
        self.Layout()
    
    def _show_results(self):
        """show the calibration results"""
        self.step = 3
        
        # calculate optimal threshold - closer to quiet level for better responsiveness
        # using 30% of the range between quiet and loud (was 60% = midpoint * 1.2)
        range_between = self.loud_level - self.quiet_level
        threshold = self.quiet_level + (range_between * 0.30)
        
        self.instructions.SetLabel(
            "Calibration Complete!\n\n"
            "Your microphone has been calibrated."
        )
        
        # show results
        self.quiet_result.SetLabel(f"Quiet level: {self.quiet_level:.4f}")
        self.loud_result.SetLabel(f"Loud level: {self.loud_level:.4f}")
        self.threshold_result.SetLabel(f"Optimal threshold: {threshold:.4f}")
        self.result_panel.Show()
        
        # update settings
        self.settings.set_audio_sensitivity(threshold)
        if self.audio_input:
            self.audio_input.noise_threshold = threshold
        
        self.progress_label.SetLabel("✓ Settings have been saved!")
        self.progress_label.SetForegroundColour(wx.Colour(0, 200, 0))  # green for success
        self.next_button.SetLabel("Finish")
        self.next_button.Enable(True)
        self.next_button.Show()
        self.back_button.Enable(True)
        
        self.Layout()
    
    def on_timer(self, event):
        """update volume display during testing"""
        if not self.audio_input:
            return
        
        # get current volume
        volume = self.audio_input.get_volume()
        
        # update display
        self.volume_text.SetLabel(f"{volume:.4f}")
        self.volume_bar.SetValue(int(volume * 100))
        
        # collect sample
        self.test_samples.append(volume)
        
        # check if test is complete
        elapsed = time.time() - self.test_start_time
        remaining = TEST_DURATION - elapsed
        
        if remaining > 0:
            # show timer with visual countdown
            self.progress_label.SetLabel(f"⏱ Time remaining: {remaining:.1f}s")
            self.progress_label.Show()  # ensure it's visible
        else:
            # test complete
            self.timer.Stop()
            
            if self.step == 1:
                # quiet test complete
                self.quiet_level = sum(self.test_samples) / len(self.test_samples)
                logger.info(f"Quiet level measured: {self.quiet_level}")
                self.progress_label.SetLabel(f"✓ Quiet level: {self.quiet_level:.4f}")
                wx.CallLater(1000, self._show_loud_test)  # pause before next step
            
            elif self.step == 2:
                # loud test complete
                self.loud_level = max(self.test_samples)  # use max for loud level
                logger.info(f"Loud level measured: {self.loud_level}")
                self.progress_label.SetLabel(f"✓ Loud level: {self.loud_level:.4f}")
                wx.CallLater(1000, self._show_results)  # pause before showing results
    
    def on_next(self, event):
        """handle next/start/finish button"""
        if self.step == 0:
            # start calibration
            self._show_quiet_test()
        elif self.step == 3:
            # finish and close
            self.EndModal(wx.ID_OK)
    
    def on_back(self, event):
        """handle back button"""
        if self.step == 3:
            # allow restarting calibration
            self._show_intro()
            self.result_panel.Hide()
            self.Layout()
    
    def on_cancel(self, event):
        """handle cancel button"""
        if self.timer and self.timer.IsRunning():
            self.timer.Stop()
        self.EndModal(wx.ID_CANCEL)

