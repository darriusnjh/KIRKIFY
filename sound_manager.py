import pygame
import os
from typing import Optional


class SoundManager:
    def __init__(self):
        """Initialize sound manager for game audio."""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.jump_sound: Optional[pygame.mixer.Sound] = None
        self.hit_sound: Optional[pygame.mixer.Sound] = None
        self.score_sound: Optional[pygame.mixer.Sound] = None
        self.background_music: Optional[str] = None
        self.music_playing = False
        
        self.load_sounds()
        self.load_background_music()
    
    def load_sounds(self):
        """Load sound effects."""
        sounds_dir = "sounds"
        
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
            print(f"Created {sounds_dir} directory. Add sound files here:")
            print("  - jump.wav (for jump sound)")
            print("  - hit.wav (for collision sound)")
            print("  - score.wav (for scoring sound)")
            return
        
        # Load jump sound
        jump_path = os.path.join(sounds_dir, "jump.wav")
        if os.path.exists(jump_path):
            try:
                self.jump_sound = pygame.mixer.Sound(jump_path)
            except:
                pass
        
        # Load hit sound
        hit_path = os.path.join(sounds_dir, "hit.wav")
        if os.path.exists(hit_path):
            try:
                self.hit_sound = pygame.mixer.Sound(hit_path)
            except:
                pass
        
        # Load score sound
        score_path = os.path.join(sounds_dir, "score.wav")
        if os.path.exists(score_path):
            try:
                self.score_sound = pygame.mixer.Sound(score_path)
            except:
                pass
    
    def load_background_music(self):
        """Load background music."""
        music_dir = "music"
        
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            print(f"Created {music_dir} directory. Add background music files here:")
            print("  - background.mp3 or background.wav or background.ogg")
            return
        
        # Look for music files
        music_files = []
        for ext in ['.mp3', '.wav', '.ogg']:
            music_path = os.path.join(music_dir, f"background{ext}")
            if os.path.exists(music_path):
                music_files.append(music_path)
        
        # Also check for any music files in the directory
        if not music_files:
            for file in os.listdir(music_dir):
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    music_files.append(os.path.join(music_dir, file))
        
        if music_files:
            self.background_music = music_files[0]
            print(f"Loaded background music: {self.background_music}")
    
    def play_jump_sound(self):
        """Play jump sound effect."""
        if self.jump_sound:
            try:
                self.jump_sound.play()
            except:
                pass
    
    def play_hit_sound(self):
        """Play hit/collision sound effect."""
        if self.hit_sound:
            try:
                self.hit_sound.play()
            except:
                pass
    
    def play_score_sound(self):
        """Play score sound effect."""
        if self.score_sound:
            try:
                self.score_sound.play()
            except:
                pass
    
    def play_start_sound(self):
        """Play start sound effect."""
        self.play_jump_sound()
    
    def start_background_music(self):
        """Start playing background music."""
        if self.background_music and not self.music_playing:
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.music_playing = True
            except Exception as e:
                print(f"Could not play background music: {e}")
    
    def stop_background_music(self):
        """Stop background music."""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def update(self):
        """Update sound manager (check if music should start)."""
        # Auto-start music when game starts
        # This can be customized based on game state
        pass
