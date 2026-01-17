import pygame
import os
import subprocess
import platform
from typing import Optional


class SoundManager:
    def __init__(self):
        """Initialize sound manager for game audio."""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.jump_sound: Optional[pygame.mixer.Sound] = None
        self.hit_sound: Optional[pygame.mixer.Sound] = None
        self.score_sound: Optional[pygame.mixer.Sound] = None
        self.count_sound: Optional[str] = None  # Path to 67.m4a file
        self.background_music: Optional[str] = None
        self.music_playing = False
        self._restore_music_after_count = False
        self._background_music_to_restore = None
        
        self.load_sounds()
        self.load_background_music()
        self.load_count_sound()
    
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
    
    def load_count_sound(self):
        """Load the 67.m4a sound file for counting game."""
        music_dir = "music"
        count_sound_path = os.path.join(music_dir, "67.m4a")
        
        if os.path.exists(count_sound_path):
            self.count_sound = count_sound_path
            print(f"Loaded count sound: {self.count_sound}")
        else:
            # Also check for other formats
            for ext in ['.m4a', '.mp3', '.wav', '.ogg']:
                alt_path = os.path.join(music_dir, f"67{ext}")
                if os.path.exists(alt_path):
                    self.count_sound = alt_path
                    print(f"Loaded count sound: {self.count_sound}")
                    return
    
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
    
    def play_count_sound(self):
        """Play the 67.m4a sound file for counting game."""
        if not self.count_sound:
            return
        
        # Check file extension
        file_ext = os.path.splitext(self.count_sound)[1].lower()
        
        # Try different methods based on file format
        if file_ext == '.m4a':
            # M4A files - use system command (most reliable)
            self._play_m4a_system(self.count_sound)
        else:
            # Try pygame mixer for other formats
            try:
                # Save current music state
                was_playing = self.music_playing
                current_music = self.background_music
                
                # Stop background music if playing
                if was_playing:
                    pygame.mixer.music.stop()
                    self.music_playing = False
                
                # Load and play the count sound
                pygame.mixer.music.load(self.count_sound)
                pygame.mixer.music.play(0)  # Play once, don't loop
                
                # Set up to restart background music when count sound finishes
                self._restore_music_after_count = was_playing
                self._background_music_to_restore = current_music
            except Exception as e:
                print(f"Could not play count sound with pygame: {e}")
                # Fallback to system command
                self._play_m4a_system(self.count_sound)
    
    def _play_m4a_system(self, file_path):
        """Play M4A file using system command (works on macOS, Linux, Windows)."""
        try:
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                # Use afplay (built-in on macOS)
                subprocess.Popen(['afplay', file_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            elif system == 'Linux':
                # Try various Linux audio players
                players = ['paplay', 'aplay', 'mpg123', 'ffplay']
                for player in players:
                    try:
                        subprocess.Popen([player, file_path],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        return
                    except FileNotFoundError:
                        continue
                print("No audio player found for M4A files on Linux")
            elif system == 'Windows':
                # Use Windows Media Player or start command
                try:
                    os.startfile(file_path)  # Windows
                except:
                    subprocess.Popen(['start', file_path], shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Could not play M4A file with system command: {e}")
            print("Consider converting 67.m4a to 67.wav or 67.ogg format")
    
    def update(self):
        """Update sound manager (check if music should start or restore)."""
        # Check if we need to restore background music after count sound
        if self._restore_music_after_count and self._background_music_to_restore:
            if not pygame.mixer.music.get_busy():
                # Count sound finished, restore background music
                try:
                    pygame.mixer.music.load(self._background_music_to_restore)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.music_playing = True
                    self._restore_music_after_count = False
                except:
                    self._restore_music_after_count = False
