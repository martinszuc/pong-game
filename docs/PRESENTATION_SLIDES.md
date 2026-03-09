# Audio-Controlled Pong Game - Presentation Guide

**Duration**: 10-12 minutes  
**Format**: 6 slides + video demo

---

## 🎯 Presentation Overview

**Goal**: Demonstrate multimedia integration through an audio-controlled game  
**Approach**: Show, don't tell - focus on visuals and video demo  
**Tone**: Technical but accessible, showcase the working product

---

## 📊 SLIDE 1: Title

**AUDIO-CONTROLLED PONG GAME**

[Large game screenshot/logo]


**Visual**: Clean title slide with game screenshot or stylized logo

**Say** (15 seconds):
> "We created a Pong game where your voice controls the paddle, integrating real-time audio processing, visual effects, and professional lighting control."

---

## 🎮 SLIDE 2: Concept Demo

[10-second gameplay GIF/video]

**Traditional Pong**: ⌨️ Keyboard  
**Our Pong**: 🎤 Voice + ⌨️ Keyboard

**Visual**: Looping GIF showing gameplay with audio control

**Say** (30 seconds):
> "Players control the left paddle using their voice. The paddle naturally falls, and making noise raises it up. We also added keyboard mode for accessibility. Let's see it in action."

---

## 🏗️ SLIDE 3: System Architecture

[System diagram with 4 boxes and arrows]

**🎤 Audio Input**  
→ Volume Detection → Calibration

**🎮 Game Engine**  
→ Physics → AI → 3 Difficulties

**🎨 Visual System**  
→ Themes → Particles → Rendering

**💡 Lighting**  
→ ArtNET/DMX → External Lights

**Visual**: Clean architecture diagram with icons and arrows

**Say** (45 seconds):
> "Our system has four integrated components. Audio input processes the microphone 60 times per second with automatic calibration. The game engine handles physics, AI, and three difficulty levels. Visuals include three color themes and particle effects. Lighting uses the professional ArtNET protocol to control external DMX lights."

---

## 🎬 SLIDE 4: Video Demo

**DEMONSTRATION VIDEO**

[Play pre-recorded demo video - 4-5 minutes]

**Video Content**:

1. **Menu Screen** (20 sec)
   - High score leaderboard
   - Click "Start Game"

2. **Gameplay - Audio Mode** (90 sec)
   - Audio visualization bar showing mic level
   - Paddle responding to noise
   - Particle effects on collisions
   - Goal flash effect (green/red)

3. **Settings Menu** (60 sec)
   - Theme switching (show 2-3 themes)
   - Difficulty options
   - Calibration Wizard process
   - Control mode toggle

4. **Gameplay - Keyboard Mode** (30 sec)
   - WASD/arrow key control
   - Same gameplay, different input

5. **Lighting Integration** (20 sec)
   - Capture/QLC+ software showing DMX output
   - Lights responding to game events

---

## 💡 SLIDE 5: Technical Highlights

**KEY TECHNICAL ACHIEVEMENTS**

✓ 60 FPS real-time audio processing  
✓ Automatic calibration wizard  
✓ Dynamic theme system (3 themes)  
✓ Professional lighting protocol  
✓ Multimodal input (audio + keyboard)  
✓ ~1,400 lines of modular code

[Small code snippet or architecture diagram]

**Say** (60 seconds):
> "Key achievements: We process audio at 60 frames per second with under 16 milliseconds latency. The calibration wizard automatically finds the optimal threshold for any microphone. Our theme system dynamically changes colors throughout the interface. We implemented the professional ArtNET protocol used in theaters and concerts. Players can choose between audio and keyboard control. The modular architecture spans 1,400 lines of clean, documented code."

---

## 🎉 SLIDE 6: Conclusion

**MULTIMEDIA INTEGRATION ACHIEVED**

**Audio Input** ──┐  
**Visual Output** ├─→ Synchronized Real-time System  
**Lighting Output** ─┘

[Final gameplay screenshot]

**Questions?**

**Say** (30 seconds):
> "We successfully integrated audio input, visual output, and lighting control into a synchronized real-time system. The game demonstrates practical multimedia programming with professional protocols and polished user experience. Thank you - we're happy to answer questions."

---

## 📋 Presentation Checklist

### Before Presentation (15 minutes prior)

- [ ] Confirm video file works on presentation computer
- [ ] Test video playback (sound and visuals)
- [ ] Have video file in multiple formats (MP4, MOV backup)
- [ ] Test projector resolution and visibility
- [ ] Queue video to start position
- [ ] Have slides ready
- [ ] Close unnecessary applications
- [ ] Optional: Have game ready to show code if asked

### During Presentation

- [ ] Speak clearly and at moderate pace
- [ ] Point at screen when referencing features
- [ ] If demo fails, switch to backup video immediately
- [ ] Keep within time limit (set phone timer)
- [ ] Make eye contact with audience
- [ ] Show enthusiasm for the project!

### Common Questions & Answers

**Q: Why volume instead of pitch detection?**  
A: Volume-based control is more responsive (< 16ms latency) and more intuitive. Pitch detection had 50-100ms latency which felt laggy.

**Q: Can you play multiplayer?**  
A: Not currently, but the architecture supports it. Would need two separate audio inputs or one player on keyboard.

**Q: How does the AI work?**  
A: Simple tracking algorithm - the AI paddle follows the ball's Y position with a difficulty-based reaction speed.

**Q: Did you write all the code?**  
A: Yes, with AI coding assistant help (Composer and Claude). We directed the development, debugged issues, and made all design decisions. AI assisted with implementation.

**Q: What was the hardest part?**  
A: Audio calibration and macOS compatibility. Different microphones and environments needed adaptive thresholds. macOS had specific issues with window management and keyboard events.

**Q: Why ArtNET instead of simpler LED control?**  
A: ArtNET is the professional standard. It demonstrates real-world protocol implementation and works with any DMX-compatible lighting system.

---

## ⏱️ Time Management

| Section | Duration | Running Total |
|---------|----------|---------------|
| Slide 1: Title | 15s | 0:15 |
| Slide 2: Concept | 30s | 0:45 |
| Slide 3: Architecture | 45s | 1:30 |
| Slide 4: **Video Demo** | 4-5 min | 6:00 |
| Slide 5: Technical | 60s | 7:00 |
| Slide 6: Conclusion | 30s | 7:30 |
| Questions | 3-4 min | 11:00 |

**Total**: 10-12 minutes ✅

**Note**: Video should be 4-5 minutes max. Narrate over it, don't just let it play silently!

---

## 🎥 Demo Tips

### What to Include in Video (Priority Order)

1. **Audio control** (must show) - Core feature, 90 seconds
2. **Theme switching** (impressive) - Shows polish, 30 seconds
3. **Calibration wizard** (quick) - Shows thoughtfulness, 30 seconds
4. **Keyboard mode** (quick) - Shows flexibility, 30 seconds
5. **Lighting** (if time) - Bonus wow factor, 20 seconds

### What to Say During Video

**Narrate over the video**:
- "Here you can see the audio bar at the bottom showing mic level"
- "Notice the particle effects when the ball hits the paddle"
- "The green flash indicates a player goal"
- "Now we're switching to keyboard mode for accessibility"
- "The lighting software shows DMX signals being sent in real-time"

**Don't let video play silently - guide the audience through it!**

### If Something Goes Wrong

**Video won't play**:
- Have backup file in different format ready
- Use image slides with verbal explanation as last resort

**Video has no sound**:
- Continue narrating what's happening on screen
- Point out visual elements

**Projector issues**:
- Show on laptop screen if needed
- Emphasize what's visible

**Stay calm - the video contains everything!**

---

## 🎨 Slide Design Recommendations

**Color Scheme**: Dark backgrounds with bright accents (matches game aesthetic)

**Fonts**:
- Title: Bold, large (40-48pt)
- Body: Clean sans-serif (24-28pt)
- Code: Monospace (18-20pt)

**Images**: 
- High resolution (at least 1920x1080)
- GIF/video embedded (not linked)
- Screenshots with clear contrast

**Keep it Clean**:
- Minimal text per slide (bullet points, not paragraphs)
- One main visual per slide
- Consistent layout and spacing

---

## 🚀 Required Materials

Have ready on laptop:
- **Demo video** (4-5 minutes) - PRIMARY MATERIAL
- Backup video in different format (MP4 + MOV)
- This presentation guide
- Code open in IDE (show if asked about implementation)
- Lighting software screenshots (if video quality is poor)
- Project folder accessible

---

**Good luck with the presentation!** 🎤🏓💡

