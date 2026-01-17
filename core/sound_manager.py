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
        self.count_sfx: Optional[pygame.mixer.Sound] = None  # for 67.wav/ogg
        self.music_playing = False
        self._restore_music_after_count = False
        self._background_music_to_restore = None
        self.vol_jump  = 0.4
        self.vol_hit   = 0.9
        self.vol_score = 1.0
        self.vol_music = 0.2
        self.vol_count = 1.0
        self.load_sounds()
        self.load_background_music()
        self.load_count_sound()
        self.music_ducked = False
        self.duck_timer_ms = 0
        self.duck_volume = 0.03          # during score
        self.normal_music_volume = self.vol_music
        self.duck_duration_ms = 6000      # how long to duck

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
        hit_path = os.path.join(sounds_dir, "hit.mp3")
        if os.path.exists(hit_path):
            try:
                self.hit_sound = pygame.mixer.Sound(hit_path)
                self.hit_sound.set_volume(self.vol_hit)
            except:
                pass
        
        # Load score sound
        score_path = os.path.join(sounds_dir, "score.wav")
        if os.path.exists(score_path):
            try:
                self.score_sound = pygame.mixer.Sound(score_path)
                self.score_sound.set_volume(self.vol_score)
            except:
                pass
    
    def load_background_music(self):
        """Load background music ONLY if file is named background.(mp3|wav|ogg)."""
        music_dir = "music"

        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            print(f"Created {music_dir} directory. Add background music files here:")
            print("  - background.mp3 or background.wav or background.ogg")
            return

        for ext in ('.mp3', '.wav', '.ogg'):
            music_path = os.path.join(music_dir, f"background{ext}")
            if os.path.exists(music_path):
                self.background_music = music_path
                print(f"Loaded background music: {self.background_music}")
                return

        # If none found
        self.background_music = None
        print("No background music found. Put background.mp3 (or .wav/.ogg) in the music/ folder.")
    
    def load_count_sound(self):
        music_dir = "music"

        # Best formats for pygame.mixer.Sound
        for ext in [".wav", ".ogg", ".mp3"]:
            p = os.path.join(music_dir, f"67{ext}")
            if os.path.exists(p):
                try:
                    self.count_sfx = pygame.mixer.Sound(p)
                    self.count_sfx.set_volume(self.vol_count)
                    print(f"Loaded count SFX (pygame): {p}")
                    return
                except Exception as e:
                    print(f"Failed to load count SFX {p}: {e}")

        # Fallback: M4A (pygame Sound usually can't load this)
        p = os.path.join(music_dir, "67.m4a")
        if os.path.exists(p):
            self.count_sound = p
            print(f"Loaded count sound (m4a fallback): {p}")
    
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
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.duck_volume)
            self.music_ducked = True
            self.duck_timer_ms = pygame.time.get_ticks() + self.duck_duration_ms
        
    def play_score_sound(self):
        """Play score sound effect."""
        if self.score_sound:
            try:
                self.score_sound.play()
            except:
                pass
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.duck_volume)
            self.music_ducked = True
            self.duck_timer_ms = pygame.time.get_ticks() + self.duck_duration_ms
    
    def play_start_sound(self):
        """Play start sound effect."""
        self.play_jump_sound()
    
    def start_background_music(self, filename: Optional[str] = None):
        if filename is not None:
            # Only allow loading from music/ folder
            self.background_music = os.path.join("music", filename)

        if self.background_music:
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.set_volume(self.vol_music)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception as e:
                print(f"Could not play background music: {e}")

    def stop_background_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        self.music_playing = False
    
    def play_count_sound(self):
        if self.count_sfx:
                try:
                    self.count_sfx.play()
                except Exception as e:
                    print(f"Could not play count SFX: {e}")
                return

        # Fallback: M4A
        if not self.count_sound:
            return

        file_ext = os.path.splitext(self.count_sound)[1].lower()

        if file_ext == ".m4a":
            # Try ffplay (no GUI window) if installed
            try:
                subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", self.count_sound],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
            except FileNotFoundError:
                print("ffplay not found. Convert 67.m4a to 67.wav or 67.ogg for no-popup playback.")
            except Exception as e:
                print(f"Could not play m4a via ffplay: {e}")

            # Last resort: would pop up (so we avoid doing it)
            return

        # Non-m4a fallback using pygame music channel (will interrupt bgm)
        try:
            was_playing = self.music_playing
            current_music = self.background_music

            if was_playing:
                pygame.mixer.music.stop()
                self.music_playing = False

            pygame.mixer.music.load(self.count_sound)
            pygame.mixer.music.play(0)

            self._restore_music_after_count = was_playing
            self._background_music_to_restore = current_music
        except Exception as e:  
            print(f"Could not play count sound: {e}")
            
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
        if self.music_ducked and pygame.time.get_ticks() >= self.duck_timer_ms:
            pygame.mixer.music.set_volume(self.vol_music)
            self.music_ducked = False
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
    def stop_all_sounds(self):
        """Stop EVERYTHING: music + all sound effect channels."""
        try:
            pygame.mixer.music.stop()   # background music
        except:
            pass

        try:
            pygame.mixer.stop()         # stops all Sound() channels
        except:
            pass

        self.music_playing = False