# musedash_advanced_v12_moviepy_bg.py

import pygame
import librosa
import librosa.display
import numpy as np
import os
import time
import traceback
import json
import threading
import subprocess
import math
import shutil

# --- Moviepy Import ---
try:
    import moviepy as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    print("Warning: moviepy not found. Video background will not work.")
    print("Install it using: pip install moviepy")
    print("You also need FFmpeg installed and accessible in your PATH.")
    mp = None # Placeholder
    MOVIEPY_AVAILABLE = False

# --- REMOVE ffpyplayer import ---
# try:
#     from ffpyplayer.player import MediaPlayer
#     FFPYPLAYER_AVAILABLE = True
# except ImportError: # ... rest of ffpyplayer import handling ...

# --- yt-dlp Import ---
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError: # ... rest of yt-dlp import handling ...
    print("Error: yt-dlp module not found.")
    yt_dlp = None; YTDLP_AVAILABLE = False # NOQA E701

# --- Tkinter imports ---
import tkinter as tk
from tkinter import filedialog


# --- Configuration --- (Mostly unchanged)
TARGET_GAME_WIDTH = 1920
TARGET_GAME_HEIGHT = 1080

TARGET_ASPECT_RATIO = TARGET_GAME_WIDTH / TARGET_GAME_HEIGHT
FPS = 60
TARGET_RADIUS = int(TARGET_GAME_HEIGHT * 0.04)
TARGET_GROUND_POS = (0, 0)
TARGET_AIR_POS = (0, 0)
NOTE_RADIUS = int(TARGET_RADIUS * 0.9)
TRAVEL_TIME_SEC = 1.8
NOTE_SPEED = 0
VIZ_MAX_HEIGHT = 100
PERFECT_WINDOW_MS = 60
GREAT_WINDOW_MS = 120
MISS_WINDOW_MS = 200
KEY_GROUND = pygame.K_j
KEY_AIR = pygame.K_f
KEY_PAUSE = pygame.K_p
KEY_BACK = pygame.K_ESCAPE
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_DARK_BG = (20, 20, 30)
COLOR_RED = (255, 0, 0)
COLOR_TARGET_GROUND = (200, 80, 80, 150)
COLOR_TARGET_AIR = (80, 80, 200, 150)
COLOR_NOTE_GROUND = (255, 100, 100)
COLOR_NOTE_AIR = (100, 100, 255)
COLOR_JUDGMENT = (200, 200, 0)
COLOR_HIT_PERFECT = (255, 215, 0)
COLOR_HIT_GREAT = (173, 216, 230)
COLOR_NOTE_GLOW = (200, 200, 200, 50)
COLOR_COMBO = (255, 165, 0)
COLOR_SCORE = (200, 200, 200)
COLOR_BUTTON = (50, 50, 70)
COLOR_BUTTON_HOVER = (80, 80, 100)
COLOR_BUTTON_TEXT = (220, 220, 220)
COLOR_VISUALIZER = (100, 150, 255, 180)
COLOR_LANE_LINE = (60, 60, 80)
COLOR_STAR = (200, 200, 220)
FALLBACK_BG_STAR_COUNT = 100
SONGS_DIR = "songs"
LIBRARY_FILE = os.path.join(SONGS_DIR, "song_library.json")
HIGHSCORE_FILE = os.path.join(SONGS_DIR, "high_scores.json")
ANALYSIS_CACHE_DIR = os.path.join(SONGS_DIR, "analysis_cache")
STATE_MENU = 0
STATE_LOADING = 1
STATE_GAMEPLAY = 2
STATE_GAME_OVER = 3
screen = None
clock = None
font_large = None
font_medium = None
font_small = None
song_library = []
high_scores = {}
current_song_info = None
audio_waveform_global = None
sample_rate_global = None
media_player = None
video_surface = None
viz_bar_heights = np.zeros(32)
VIZ_X_START, VIZ_WIDTH, VIZ_Y_POS = 0, 0, 0
VIZ_BAR_WIDTH, VIZ_BAR_SPACING = 10, 2
download_progress = {"status": "idle", "message": "", "thread": None, "percent": 0}
preview_playing = False
preview_sound = None
# --- Aesthetic Globals ---
fallback_bg_stars = []
TARGET_ASPECT_RATIO = TARGET_GAME_WIDTH / TARGET_GAME_HEIGHT
FPS = 60
# --- ADD Opacity Constant ---
BACKGROUND_OPACITY = 180 # Adjust this value (0-255) for desired dimness
# --------------------------
TARGET_RADIUS = int(TARGET_GAME_HEIGHT * 0.04)
# --- ADD THIS LINE IF MISSING OR UNCOMMENT IT ---
fallback_bg_scroll_y = 0.0
# -----------------------------------------------
combo_text_scale = 1.0
combo_text_scale_timer = 0.0
# ... (rest of config: FPS, TARGET_RADIUS, POS, NOTE_RADIUS, TRAVEL_TIME_SEC, VIZ_MAX_HEIGHT, WINDOWS, KEYS) ...
# ... (Colors remain the same) ...
# ... (File Paths remain the same) ...
# ... (States remain the same) ...

# --- Global variables ---
screen = None; clock = None; font_large = None; font_medium = None; font_small = None # NOQA E701
song_library = []; high_scores = {}; current_song_info = None # NOQA E701
audio_waveform_global = None; sample_rate_global = None # NOQA E701
# --- Replace ffpyplayer globals with moviepy globals ---
# media_player = None      # REMOVED
# video_surface = None     # REMOVED (We create this per frame now)
video_clip = None           # <<< Moviepy clip object
video_clip_duration = 0.0   # <<< Duration of the clip
current_video_frame_surface = None # <<< Surface holding the current processed frame
# --- End Replacement ---
viz_bar_heights = np.zeros(32); VIZ_X_START, VIZ_WIDTH, VIZ_Y_POS = 0,0,0; VIZ_BAR_WIDTH, VIZ_BAR_SPACING=10,2 # NOQA E701 E501
download_progress = {"status":"idle","message":"","thread":None,"percent":0} # NOQA E501
preview_playing = False; preview_sound = None # NOQA E701

# --- Helper Functions --- (init_pygame, draw_text, load/save, add_local_song, hooks, download, analysis, filtering - IDENTICAL)
# ... (Keep all helper functions from the previous version v11) ...
def init_pygame(): # Identical
    global screen, clock, font_large, font_medium, font_small, TARGET_GROUND_POS, TARGET_AIR_POS, NOTE_SPEED, VIZ_X_START, VIZ_WIDTH, VIZ_Y_POS, VIZ_BAR_WIDTH, VIZ_BAR_SPACING, VIZ_MAX_HEIGHT, fallback_bg_stars # NOQA E501
    pygame.init(); pygame.mixer.init() # NOQA E702
    print(f"Requesting Scaled Fullscreen: {TARGET_GAME_WIDTH}x{TARGET_GAME_HEIGHT}")
    screen = pygame.display.set_mode((TARGET_GAME_WIDTH, TARGET_GAME_HEIGHT), pygame.FULLSCREEN | pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF) # NOQA E501
    w, h = screen.get_size()
    if w != TARGET_GAME_WIDTH or h != TARGET_GAME_HEIGHT: print(f"Warn: Logical surface {w}x{h}") # NOQA E501
    pygame.display.set_caption("Rhythm Runner v12 (Moviepy BG)")
    try: font_large, font_medium, font_small = pygame.font.Font(None, int(h*0.1)), pygame.font.Font(None, int(h*0.07)), pygame.font.Font(None, int(h*0.045)) # NOQA E501
    except IOError: print("Default font not found."); font_large, font_medium, font_small = pygame.font.SysFont(None, int(h*0.1)), pygame.font.SysFont(None, int(h*0.07)), pygame.font.SysFont(None, int(h*0.045)) # NOQA E501
    clock = pygame.time.Clock()
    jx = TARGET_GAME_WIDTH * 0.15
    TARGET_GROUND_POS, TARGET_AIR_POS = (int(jx), int(h*0.75)), (int(jx), int(h*0.4)) # NOQA E501
    NOTE_SPEED = (TARGET_GAME_WIDTH - jx) / TRAVEL_TIME_SEC
    num_bars = len(viz_bar_heights); VIZ_BAR_WIDTH = max(5, int(w*0.01)); VIZ_BAR_SPACING = max(1, int(VIZ_BAR_WIDTH*0.2)); VIZ_WIDTH = num_bars*(VIZ_BAR_WIDTH+VIZ_BAR_SPACING)-VIZ_BAR_SPACING; VIZ_X_START = (w-VIZ_WIDTH)//2; VIZ_Y_POS = h-int(h*0.05); VIZ_MAX_HEIGHT = int(h*0.15) # NOQA E501
    os.makedirs(SONGS_DIR, exist_ok=True); os.makedirs(ANALYSIS_CACHE_DIR, exist_ok=True) # NOQA E701
    fallback_bg_stars = [(random.randint(0, TARGET_GAME_WIDTH), random.randint(0, TARGET_GAME_HEIGHT), random.randint(1, 3)) for _ in range(FALLBACK_BG_STAR_COUNT)] # NOQA E501

def draw_text(text, font, color, surface, x, y, center=False, center_x=False, center_y=False): # Identical
    textobj = font.render(text, True, color); textrect = textobj.get_rect() # NOQA E701
    if center: textrect.center = (x, y) # NOQA E701
    elif center_x: textrect.centerx = x; textrect.top = y # NOQA E701
    elif center_y: textrect.centery = y; textrect.left = x # NOQA E701
    else: textrect.topleft = (x, y) # NOQA E701
    surface.blit(textobj, textrect); return textrect # NOQA E701

def load_library(): # Identical logic
    global song_library
    try:
        with open(LIBRARY_FILE, 'r') as f: song_library = json.load(f) # NOQA E701
        song_library = [s for s in song_library if s.get('audio_path') and os.path.exists(s.get('audio_path','')) and s.get('video_path') and os.path.exists(s.get('video_path',''))] # NOQA E501
        save_library()
    except (FileNotFoundError, json.JSONDecodeError): song_library = []
def save_library(): # Identical
    try:
        with open(LIBRARY_FILE, 'w') as f: json.dump(song_library, f, indent=4) # NOQA E701
    except IOError: print("Error: Could not save song library.")
def load_high_scores(): # Identical
    global high_scores
    try:
        with open(HIGHSCORE_FILE, 'r') as f: high_scores = json.load(f) # NOQA E701
    except (FileNotFoundError, json.JSONDecodeError): high_scores = {}
def save_high_scores(): # Identical
    try:
        with open(HIGHSCORE_FILE, 'w') as f: json.dump(high_scores, f, indent=4) # NOQA E701
    except IOError: print("Error: Could not save high scores.")
def get_high_score(song_id): return high_scores.get(str(song_id), 0) # Identical
def set_high_score(song_id, score): # Identical
    hs = get_high_score(song_id);
    if score > hs: high_scores[str(song_id)] = score; save_high_scores(); return True # NOQA E701
    return False

def add_local_song(): # Identical logic (uses ffmpeg extraction)
    global song_library, selected_song_index
    ffmpeg_path = shutil.which("ffmpeg")
    root = tk.Tk(); root.withdraw() # NOQA E701
    filepath = filedialog.askopenfilename(title="Select Audio/Video File", filetypes=(("Media Files", "*.mp3 *.ogg *.wav *.mp4 *.mkv *.avi *.mov *.webm"), ("All files", "*.*"))) # NOQA E501
    root.destroy()
    if not filepath: print("No file selected."); return False # NOQA E701
    filepath = os.path.normpath(filepath); song_id = filepath # NOQA E701
    if any(s.get('id') == song_id for s in song_library):
        print(f"'{os.path.basename(filepath)}' already exists.");
        try: idx = next(i for i,s in enumerate(song_library) if s.get('id')==song_id); selected_song_index=idx # NOQA E701 E501
        except StopIteration: pass; return False # NOQA E701
    title = os.path.splitext(os.path.basename(filepath))[0]; aud_path, vid_path, dur = None, None, 0 # NOQA E701 E501
    file_ext = os.path.splitext(filepath)[1].lower(); aud_exts, vid_exts = ['.mp3','.ogg','.wav'],['.mp4','.mkv','.avi','.mov','.webm'] # NOQA E701 E501
    if file_ext in aud_exts: print(f"Audio file: {filepath}"); aud_path, vid_path = filepath, filepath # NOQA E701 E501
    elif file_ext in vid_exts:
        print(f"Video file: {filepath}");
        if not ffmpeg_path: print("Error: FFmpeg required for video."); return False # NOQA E701
        vid_path = filepath; aud_base = f"{title}_extracted_audio"; aud_path = os.path.join(SONGS_DIR, aud_base + ".mp3"); print(f"Extracting audio: {aud_path}") # NOQA E701 E501
        os.makedirs(SONGS_DIR, exist_ok=True)
        cmd = [ffmpeg_path,'-i',filepath,'-vn','-acodec','libmp3lame','-ab','192k','-ar','44100','-sn','-y',aud_path]
        try: print(f"FFmpeg: {' '.join(cmd)}"); result=subprocess.run(cmd,capture_output=True,text=True,check=True,encoding='utf-8',errors='ignore'); print("Audio extracted.") # NOQA E701 E501
        except FileNotFoundError: print("FFmpeg not found error."); return False # NOQA E701
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error:\n{e.stderr}")
            if os.path.exists(aud_path): os.remove(aud_path); return False # NOQA E701 E501
        except Exception as e:
            print(f"FFmpeg unexpected error: {e}"); traceback.print_exc()
            if os.path.exists(aud_path): os.remove(aud_path); return False # NOQA E701 E501
    else: print(f"Unsupported file: {file_ext}"); return False # NOQA E701
    if aud_path and vid_path:
        info = {"id":song_id,"title":title,"audio_path":aud_path,"video_path":vid_path,"thumbnail_path":None,"duration":dur}; song_library.append(info); save_library(); print(f"Added '{title}'."); selected_song_index=len(song_library)-1; return True # NOQA E701 E501
    else: print("Failed path determination."); return False # NOQA E701

def _download_hook(d): # Identical
    global download_progress
    if d['status'] == 'downloading': total_bytes=d.get('total_bytes_estimate') or d.get('total_bytes'); downloaded=d.get('downloaded_bytes'); percent=0; msg="Downloading..."; # NOQA E701 E501
    if downloaded is not None and total_bytes is not None and total_bytes > 0: percent=(downloaded/total_bytes)*100; msg=f"Downloading {percent:.1f}%"; # NOQA E701 E501
    elif downloaded is not None:
        msg=f"Downloading {downloaded/1024/1024:.1f} MB"; # NOQA E701
        download_progress["message"],download_progress["percent"]=msg,percent; # NOQA E701
    elif d['status'] == 'finished':
        download_progress["message"]
        download_progress["percent"]="Processing...",100; # NOQA E701
    elif d['status'] == 'error': download_progress["status"]="error"; # NOQA E701

def _perform_download_with_module(youtube_url): # Identical logic
    global download_progress, song_library
    if not YTDLP_AVAILABLE: download_progress["status"]="error"; download_progress["message"]="yt-dlp missing"; return # NOQA E701 E501
    download_progress = {"status":"downloading", "message":"Preparing...", "percent":0, "thread":download_progress.get("thread")} # NOQA E501
    try:
        base_out = os.path.join(SONGS_DIR, "%(title)s_%(id)s"); vid_tmpl = base_out + ".%(ext)s" # NOQA E701 E501
        ydl_opts = {'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio/best[ext=mp4]/best','outtmpl': vid_tmpl,'noplaylist': True, 'progress_hooks': [_download_hook], 'quiet': True, 'no_warnings': False, 'writethumbnail': True,'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},{'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'}],'keepvideo': True, 'ffmpeg_location': None} # NOQA E501
        info_dict = None; vid_path = None; aud_path = None; thumb_path = None # NOQA E701
        print(f"Starting download & audio extraction for: {youtube_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try: info_dict = ydl.extract_info(youtube_url, download=False); vid_id=info_dict.get('id'); title=info_dict.get('title', '?'); dur=info_dict.get('duration', 0); print(f"Found: '{title}' ({vid_id})") # NOQA E701 E501
            except Exception as e: raise ValueError(f"Info extract fail: {e}") # NOQA E701
            if not vid_id: raise ValueError("No video ID.") # NOQA E701
            download_progress["message"] = "Downloading/Extracting..."
            err_code = ydl.download([youtube_url])
            if err_code != 0: raise yt_dlp.utils.DownloadError(f"DL process error: {err_code}") # NOQA E701
            base_fn = f"{title}_{vid_id}"; vid_ext, aud_ext, thm_ext = '.mp4', '.mp3', '.jpg' # NOQA E701 E501
            vid_path, aud_path, thumb_path = None, None, None # Re-init before search loop
            print(f"Searching for files related to ID: {vid_id} in {SONGS_DIR}")
            for fname in os.listdir(SONGS_DIR):
                 low_f = fname.lower() # Assign always
                 if vid_id in fname:
                     if low_f.endswith(vid_ext): vid_path = os.path.join(SONGS_DIR, fname); print(f"  Found Vid (ID): {fname}") # NOQA E701 E501
                     elif vid_path is None and low_f.endswith(('.mkv','.webm')): vid_path = os.path.join(SONGS_DIR, fname); print(f"  Found Vid Fallback (ID): {fname}") # NOQA E701 E501
                     if low_f.endswith(aud_ext): aud_path = os.path.join(SONGS_DIR, fname); print(f"  Found Aud (ID): {fname}") # NOQA E701 E501
                     if low_f.endswith(thm_ext): thumb_path = os.path.join(SONGS_DIR, fname); print(f"  Found Thumb (ID): {fname}") # NOQA E701 E501
            if not vid_path or not aud_path:
                 print("Performing fallback search by prefix...")
                 for fname in os.listdir(SONGS_DIR):
                     low_f = fname.lower()
                     if fname.startswith(base_fn):
                          if not vid_path:
                               if low_f.endswith(vid_ext) or low_f.endswith(('.mkv','.webm')): vid_path=os.path.join(SONGS_DIR, fname); print(f"    Found Vid (Prefix): {fname}") # NOQA E701 E501
                          if not aud_path:
                               if low_f.endswith(aud_ext): aud_path=os.path.join(SONGS_DIR, fname); print(f"    Found Aud (Prefix): {fname}") # NOQA E701 E501
                          if not thumb_path:
                                if low_f.endswith(thm_ext): thumb_path=os.path.join(SONGS_DIR, fname); print(f"    Found Thumb (Prefix): {fname}") # NOQA E701 E501
            if not vid_path: raise FileNotFoundError(f"Vid missing: {title}") # NOQA E701
            if not aud_path: raise FileNotFoundError(f"Aud missing: {title}") # NOQA E701
            if not thumb_path: print(f"Warn: Thumb missing: {title}") # NOQA E701
        if not any(s['id'] == vid_id for s in song_library):
            info = {"id": vid_id, "title": title, "audio_path": aud_path, "video_path": vid_path,"thumbnail_path": thumb_path,"duration": dur}; song_library.append(info); save_library(); download_progress["message"] = f"'{title[:30]}' saved!" # NOQA E701 E501
        else: download_progress["message"] = f"'{title[:30]}' exists."
        download_progress["status"] = "success"
    except yt_dlp.utils.DownloadError as e:
        download_progress["status"]="error"; err_s=str(e).lower(); msg=f"DL fail: {err_s[:100]}"; # NOQA E701 E501
        if 'ffmpeg' in err_s: msg="FFmpeg Error"; # NOQA E701
        elif 'download video data' in err_s: msg="DL Error"; # NOQA E701
        download_progress["message"]=msg; print(f"yt-dlp DE: {e}") # NOQA E701
    except Exception as e:
        download_progress["status"]="error"; download_progress["message"]=f"Error: {str(e)[:100]}"; print(f"DL Ex: {traceback.format_exc()}") # NOQA E701 E501

def start_download_thread(youtube_url): # Identical
    global download_progress
    if not YTDLP_AVAILABLE: download_progress["status"]="error"; download_progress["message"]="yt-dlp missing"; return # NOQA E701 E501
    if download_progress["status"]=="downloading": print("DL in progress."); return # NOQA E701
    download_progress = {"status":"idle", "message":"", "thread":None, "percent":0}; print(f"Attempt DL: {youtube_url}"); # NOQA E701 E501
    download_progress["thread"] = threading.Thread(target=_perform_download_with_module, args=(youtube_url,), daemon=True); download_progress["thread"].start() # NOQA E701 E501

def analyze_audio(audio_path, use_onset_detect=True): # Identical
    cache_fn=os.path.basename(audio_path)+".json"; cache_path=os.path.join(ANALYSIS_CACHE_DIR, cache_fn) # NOQA E701 E501
    try:
        if os.path.exists(cache_path): print(f"Cache hit: {cache_path}"); # NOQA E701
        with open(cache_path,'r') as f: data=json.load(f); # NOQA E701
        times=np.array(data['event_times']); y,sr=librosa.load(audio_path,sr=None,mono=True); return times,y,sr # NOQA E701 E501
    except Exception as e: print(f"Cache fail: {e}.")
    print(f"Analyzing: {audio_path}")
    try:
        y,sr=librosa.load(audio_path,sr=None,mono=True); times=None; # NOQA E701
        if use_onset_detect: hop=512; frames=librosa.onset.onset_detect(y=y,sr=sr,hop_length=hop,units='frames',backtrack=True,wait=1,pre_avg=5,post_avg=5,pre_max=5,post_max=5,delta=0.05); times=librosa.frames_to_time(frames,sr=sr,hop_length=hop); print(f"{len(times)} onsets.") # NOQA E701 E501
        else: _,frames=librosa.beat.beat_track(y=y,sr=sr,tightness=100,units='frames'); times=librosa.frames_to_time(frames,sr=sr); print(f"{len(times)} beats.") # NOQA E701 E501
        if times is None: times=np.array([]) # NOQA E701
        cache_data={'event_times':times.tolist()}
        try:
            with open(cache_path,'w') as f: json.dump(cache_data,f); print(f"Cache saved: {cache_path}") # NOQA E701 E501
        except IOError as e: print(f"Cache save fail: {e}")
        return times,y,sr
    except Exception as e: print(f"Analysis error: {e}"); traceback.print_exc(); return None,None,None # NOQA E701 E501

def filter_close_events(times, min_separation_sec=0.08): # Identical
    if times is None or len(times)<2: return times # NOQA E701
    filtered=[times[0]]; # NOQA E701
    for i in range(1,len(times)):
        if (times[i]-filtered[-1])>=min_separation_sec: filtered.append(times[i]) # NOQA E701
    print(f"Filtered {len(times)}->{len(filtered)} (min: {min_separation_sec*1000:.0f}ms)")
    return np.array(filtered)

class Note: # Identical logic with updated draw
    def __init__(self, lane, hit_time_sec): self.lane,self.hit_time_sec=lane,hit_time_sec; self.spawn_time_sec=self.hit_time_sec-TRAVEL_TIME_SEC; self.start_x=TARGET_GAME_WIDTH+NOTE_RADIUS; self.target_pos=TARGET_GROUND_POS if lane=="ground" else TARGET_AIR_POS; self.y=self.target_pos[1]; self.x=self.start_x; self.radius=NOTE_RADIUS; self.color=COLOR_NOTE_GROUND if lane=="ground" else COLOR_NOTE_AIR; self.is_active,self.is_hit,self.is_missed=False,False,False; self.hit_result,self.hit_feedback_timer,self.feedback_color,self.effect_scale=None,0,COLOR_WHITE,1.0 # NOQA E501 E702
    def update(self, current_time_sec, dt): # Identical
        if self.is_hit or self.is_missed:
            if self.hit_feedback_timer>0: self.hit_feedback_timer-=dt; self.effect_scale+=dt*6 # Faster pop
            return
        if not self.is_active and current_time_sec>=self.spawn_time_sec: self.is_active=True # NOQA E701
        if self.is_active: self.x -= NOTE_SPEED*dt
        miss_thresh = self.hit_time_sec + (MISS_WINDOW_MS/1000.0)
        if self.is_active and (current_time_sec>miss_thresh or self.x<self.target_pos[0]-TARGET_RADIUS*2): self.is_missed,self.is_active,self.hit_result=True,False,"MISS (Timeout)" # NOQA E701 E501
    def draw(self, surface): # Modified draw
        if not self.is_active and not (self.is_hit and self.hit_feedback_timer > 0): return
        pos=(int(self.x),int(self.y)); rad=int(self.radius); col=self.color # NOQA E701 E501
        if self.is_hit and self.hit_feedback_timer > 0:
            progress = 1.0 - (self.hit_feedback_timer / 0.3); flash_alpha = max(0, int(255 * (1.0 - progress*1.5))); expand_radius = int(self.radius * (1.0 + progress * 1.5)); ring_alpha = max(0, int(150 * (1.0 - progress))); # NOQA E701 E501
            if flash_alpha > 10: tf = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA); pygame.draw.circle(tf, (*self.feedback_color, flash_alpha), (rad, rad), rad); surface.blit(tf, (pos[0] - rad, pos[1] - rad)) # NOQA E701 E501
            if ring_alpha > 10 and expand_radius > rad: pygame.draw.circle(surface, (*self.feedback_color[:3], ring_alpha), pos, expand_radius, width=max(2, int(rad * 0.1))) # NOQA E501
        if self.is_active:
            glow_rad = rad + 4; tg = pygame.Surface((glow_rad*2, glow_rad*2), pygame.SRCALPHA); pygame.draw.circle(tg, COLOR_NOTE_GLOW, (glow_rad, glow_rad), glow_rad); surface.blit(tg, (pos[0] - glow_rad, pos[1] - glow_rad)) # NOQA E701 E501
            pygame.draw.circle(surface,col,pos,rad); pygame.draw.circle(surface,COLOR_WHITE,pos,rad, 2) # NOQA E701 E501
    def check_hit_timing(self, current_time_sec): # Identical
        if not self.is_active or self.is_hit or self.is_missed: return None,0
        diff_ms=(current_time_sec-self.hit_time_sec)*1000.0; abs_diff=abs(diff_ms) # NOQA E701 E501
        if abs_diff<=PERFECT_WINDOW_MS: return "PERFECT",diff_ms # NOQA E701
        elif abs_diff<=GREAT_WINDOW_MS: return "GREAT",diff_ms # NOQA E701
        elif abs_diff<=MISS_WINDOW_MS: return "MISS (Timing)",diff_ms # NOQA E701
        return None,diff_ms

def generate_beatmap(event_times): # Identical
    notes=[]; lane="air"; # NOQA E701
    if event_times is None or len(event_times)==0: return notes
    for t in event_times: lane="ground" if lane=="air" else "air"; notes.append(Note(lane,t)) # NOQA E701 E501
    print(f"Generated {len(notes)} notes."); return notes # NOQA E701


# --- State Function Definitions ---

# ... (run_menu definition remains unchanged) ...
selected_song_index = 0; preview_sound = None; preview_playing = False; scroll_offset = 0; url_input_active = False; url_input_text = "" # NOQA: E702
def run_menu(events):
    global selected_song_index, preview_sound, preview_playing, scroll_offset, current_song_info, game_state, url_input_active, url_input_text, download_progress # Added download_progress # NOQA: E501
    screen.fill(COLOR_DARK_BG); draw_text("Rhythm Runner", font_large, COLOR_WHITE, screen, TARGET_GAME_WIDTH // 2, int(TARGET_GAME_HEIGHT*0.08), center=True) # NOQA: E701 E501
    list_area_height = TARGET_GAME_HEIGHT * 0.6; list_item_height = int(font_small.get_height() * 4); list_y_start = int(TARGET_GAME_HEIGHT * 0.18); visible_items = max(1, int(list_area_height // list_item_height)); list_area_rect = pygame.Rect(int(TARGET_GAME_WIDTH*0.05), list_y_start, int(TARGET_GAME_WIDTH * 0.5), list_area_height); pygame.draw.rect(screen, (30,30,40), list_area_rect) # NOQA: E701 E501
    start_index = scroll_offset; end_index = min(len(song_library), start_index + visible_items) # NOQA: E701
    mouse_pos = pygame.mouse.get_pos(); clicked = False; scroll_input = 0; url_pasted = False # NOQA E701 E501
    for event in events:
        if event.type == pygame.QUIT: return False
        if event.type == pygame.KEYDOWN:
            if url_input_active:
                 if event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                     try: clipboard_text = tk.Tk().clipboard_get(); url_input_text += clipboard_text if clipboard_text else ""; url_pasted = True # NOQA E701 E501
                     except Exception as clip_err: print(f"Clipboard error: {clip_err}")
                 elif event.key == pygame.K_RETURN:
                     if url_input_text: start_download_thread(url_input_text) # NOQA E701
                     url_input_active = False; url_input_text = ""
                 elif event.key == pygame.K_BACKSPACE: url_input_text = url_input_text[:-1]
                 elif event.key == pygame.K_ESCAPE: url_input_active = False; url_input_text = ""
                 elif not (pygame.key.get_mods() & pygame.KMOD_CTRL) and not url_pasted: url_input_text += event.unicode # NOQA E501
            else:
                 if event.key == pygame.K_UP: scroll_input = -1
                 if event.key == pygame.K_DOWN: scroll_input = 1
                 if event.key == pygame.K_RETURN:
                     if 0 <= selected_song_index < len(song_library): current_song_info = song_library[selected_song_index]; game_state = STATE_LOADING; # NOQA E701
                     if preview_playing: preview_sound.stop(); preview_playing = False; return True # NOQA E701
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: clicked = True
            if event.button == 4: scroll_input = -1
            if event.button == 5: scroll_input = 1
        if event.type == pygame.MOUSEWHEEL: scroll_input = -event.y
    if scroll_input != 0: scroll_offset += scroll_input; scroll_offset = max(0, min(scroll_offset, max(0, len(song_library) - visible_items))) # NOQA E701 E501
    for i in range(start_index, end_index):
        song = song_library[i]; item_y = list_y_start + (i - start_index) * list_item_height; item_rect = pygame.Rect(list_area_rect.left + 10, item_y + 5, list_area_rect.width - 20, list_item_height - 10) # NOQA E701 E501
        is_selected = (i == selected_song_index); bg_color = (60,60,70) if is_selected else (40,40,50) # NOQA E701
        if item_rect.collidepoint(mouse_pos):
            bg_color = (70,70,85) if is_selected else (55,55,65)
            if clicked and selected_song_index != i:
                selected_song_index = i;
                if preview_playing: preview_sound.stop(); preview_playing = False # NOQA E701
                try: preview_sound = pygame.mixer.Sound(song['audio_path']); duration = song.get('duration') or preview_sound.get_length(); preview_start = duration * 0.3; preview_sound.play(fade_ms=200, start=preview_start); preview_playing = True # NOQA E701 E501
                except Exception as e: print(f"Preview error: {e}"); preview_sound=None; preview_playing=False # NOQA E701
        pygame.draw.rect(screen, bg_color, item_rect, border_radius=5); title_rect = draw_text(song.get('title', '?')[:45], font_small, COLOR_WHITE, screen, item_rect.left + 15, item_rect.centery - int(font_small.get_height()*0.6), center_y=False); hs = get_high_score(song.get('id', '')); draw_text(f"HS: {hs}", font_small, (180,180,100), screen, item_rect.left + 15, title_rect.bottom + 2 ); duration = song.get('duration', 0); # NOQA E701 E501
        if duration > 0: mins, secs = divmod(duration, 60); draw_text(f"{mins}:{secs:02d}", font_small, (180,180,180), screen, item_rect.right - 60, item_rect.top + 15) # NOQA E701 E501
    details_x = list_area_rect.right + int(TARGET_GAME_WIDTH*0.03); details_rect = pygame.Rect(details_x, list_y_start, TARGET_GAME_WIDTH - details_x - int(TARGET_GAME_WIDTH*0.05), list_area_height); pygame.draw.rect(screen, (30,30,40), details_rect) # NOQA E701 E501
    if 0 <= selected_song_index < len(song_library):
        selected_song = song_library[selected_song_index]; thumb_path = selected_song.get('thumbnail_path'); thumb_surf = None # NOQA E701
        if thumb_path and os.path.exists(thumb_path):
            try: thumb_surf = pygame.image.load(thumb_path).convert(); max_thumb_w = details_rect.width - 40; max_thumb_h = details_rect.height * 0.45; orig_w, orig_h = thumb_surf.get_size(); ratio = min(max_thumb_w / orig_w, max_thumb_h / orig_h) if orig_w > 0 and orig_h > 0 else 1; new_w, new_h = int(orig_w * ratio), int(orig_h * ratio); thumb_surf = pygame.transform.smoothscale(thumb_surf, (new_w, new_h)) # NOQA E701 E501
            except Exception as e: print(f"Thumb load error {thumb_path}: {e}"); thumb_surf = None # NOQA E701
        if thumb_surf: thumb_rect = thumb_surf.get_rect(centerx=details_rect.centerx, top=details_rect.top + 20); screen.blit(thumb_surf, thumb_rect); details_y_offset = thumb_rect.bottom + 20 # NOQA E701 E501
        else: draw_text("No Thumbnail", font_medium, (100,100,100), screen, details_rect.centerx, details_rect.top + 100, center=True); details_y_offset = details_rect.top + 180 # NOQA E701 E501
        draw_text(selected_song.get('title', '?')[:35], font_medium, COLOR_WHITE, screen, details_rect.centerx, details_y_offset, center_x=True); details_y_offset += int(font_medium.get_height() * 1.2); hs = get_high_score(selected_song.get('id', '')); draw_text(f"High Score: {hs}", font_small, COLOR_SCORE, screen, details_rect.centerx, details_y_offset, center_x=True); details_y_offset += int(font_small.get_height() * 2) # NOQA E701 E501
        play_button_rect = pygame.Rect(0, 0, int(details_rect.width*0.6), int(TARGET_GAME_HEIGHT*0.08)); play_button_rect.center = (details_rect.centerx, details_y_offset + play_button_rect.height // 2); play_hover = play_button_rect.collidepoint(mouse_pos); pygame.draw.rect(screen, COLOR_BUTTON_HOVER if play_hover else COLOR_BUTTON, play_button_rect, border_radius=10); draw_text("Play", font_medium, COLOR_BUTTON_TEXT, screen, play_button_rect.centerx, play_button_rect.centery, center=True) # NOQA E701 E501
        if play_hover and clicked: current_song_info = selected_song; game_state = STATE_LOADING; # NOQA E701
        if preview_playing: preview_sound.stop(); preview_playing = False; return True # NOQA E701
    else: draw_text("No Songs", font_medium, (100,100,100), screen, details_rect.centerx, details_rect.centery, center=True) # NOQA E701
    bottom_area_y = list_area_rect.bottom + int(TARGET_GAME_HEIGHT*0.03)
    input_box_rect = pygame.Rect(list_area_rect.left, bottom_area_y, list_area_rect.width, int(TARGET_GAME_HEIGHT*0.07)); pygame.draw.rect(screen, (50,50,60) if url_input_active else (35,35,45), input_box_rect, border_radius=5); prompt_text = "Paste YouTube URL (Ctrl+V)..." if not url_input_text else url_input_text; # NOQA E701 E501
    if url_input_active: prompt_text += ("|" if int(time.time() * 2) % 2 == 0 else "")
    draw_text(prompt_text, font_small, COLOR_WHITE if url_input_active else (150,150,150), screen, input_box_rect.left + 10, input_box_rect.centery, center_y=True)
    if clicked and input_box_rect.collidepoint(mouse_pos): url_input_active = True # NOQA E701
    elif clicked and not input_box_rect.collidepoint(mouse_pos): url_input_active = False # NOQA E701
    dl_status_rect = pygame.Rect(details_x, bottom_area_y, details_rect.width, int(TARGET_GAME_HEIGHT*0.07)); status_color = None; status_text_color = COLOR_WHITE; status_text = download_progress["message"]; # NOQA E701 E501
    current_status = download_progress["status"]
    if current_status == "downloading": status_color = (60,60,30); status_text_color=(200,200,150); status_text += f" ({download_progress['percent']:.0f}%)" # NOQA E701 E501
    elif current_status == "error": status_color = (80,30,30); status_text_color=(220,150,150); status_text = f"Error: {status_text[:50]}..." # NOQA E701 E501
    elif current_status == "success": status_color = (30,80,30); status_text_color=(150,220,150) # NOQA E701 E501
    if current_status != "idle":
         pygame.draw.rect(screen, status_color, dl_status_rect, border_radius=5); draw_text(status_text, font_small, status_text_color, screen, dl_status_rect.centerx, dl_status_rect.centery, center=True); # NOQA E701 E501
         if dl_status_rect.collidepoint(mouse_pos) and clicked and current_status != "downloading": print(f"Dismiss status: {current_status}"); download_progress["status"] = "idle"; # NOQA E701 E501
    add_button_width = int(TARGET_GAME_WIDTH * 0.2); add_button_rect = pygame.Rect(0, 0, add_button_width, int(TARGET_GAME_HEIGHT*0.07)); add_button_rect.right = input_box_rect.right; add_button_rect.top = input_box_rect.bottom + 10; add_hover = add_button_rect.collidepoint(mouse_pos); pygame.draw.rect(screen, COLOR_BUTTON_HOVER if add_hover else COLOR_BUTTON, add_button_rect, border_radius=10); draw_text("Add Local File", font_small, COLOR_BUTTON_TEXT, screen, add_button_rect.centerx, add_button_rect.centery, center=True); # NOQA E701 E501
    if add_hover and clicked: add_local_song() # NOQA E701
    return True

loading_progress = 0; loading_message = "Loading..."; beatmap_data = None; analysis_thread = None # NOQA: E702
def _perform_analysis_and_load(audio_path, video_path):
    global loading_progress, loading_message, beatmap_data, audio_waveform_global, sample_rate_global, video_clip, video_clip_duration # Use moviepy globals
    try:
        loading_progress = 10; loading_message = "Analyzing audio..." # NOQA E701
        event_times, waveform, sample_rate = analyze_audio(audio_path, use_onset_detect=True)
        if event_times is None: raise ValueError("Audio analysis failed.") # NOQA E701
        loading_progress = 50; loading_message = "Filtering events..." # NOQA E701
        filtered_times = filter_close_events(event_times, min_separation_sec=0.08)
        if filtered_times is None or len(filtered_times) == 0: raise ValueError("No valid events found.") # NOQA E701
        audio_waveform_global = waveform; sample_rate_global = sample_rate # NOQA E701
        loading_progress = 75; loading_message = "Generating beatmap..." # NOQA E701
        beatmap_data = generate_beatmap(filtered_times)
        if not beatmap_data: raise ValueError("Beatmap generation failed.") # NOQA E701

        # --- Load Video with Moviepy ---
        loading_progress = 85; loading_message = "Loading video..." # NOQA E701
        video_clip = None; video_clip_duration = 0.0 # Reset
        if MOVIEPY_AVAILABLE and mp is not None and video_path and os.path.exists(video_path):
             try:
                 print(f"Initializing Moviepy Clip for: {video_path}")
                 # Make path raw just in case
                 raw_video_path = fr"{video_path}"
                 # Load clip - this might take a moment depending on video size/length
                 video_clip = mp.VideoFileClip(raw_video_path, audio=False) # Don't load audio track here
                 video_clip_duration = video_clip.duration if video_clip.duration else 0.0
                 print(f"Moviepy clip loaded. Duration: {video_clip_duration:.2f}s")
             except Exception as clip_err:
                  print(f"Error loading Moviepy clip: {clip_err}")
                  traceback.print_exc()
                  if video_clip: video_clip.close(); video_clip = None # NOQA E701
                  video_clip_duration = 0.0
        else: print("Skipping video loading (Moviepy unavailable or no video path).")
        # --- End Load Video ---

        loading_progress = 100; loading_message = "Ready!" # NOQA E701

    except Exception as e:
        loading_message = f"Error: {str(e)[:80]}"; loading_progress = -1 # NOQA E701
        print(f"Load Error: {e}"); traceback.print_exc() # NOQA E701
        if video_clip: video_clip.close(); video_clip = None # Close clip on error # NOQA E701

def run_loading(events):
    global game_state, analysis_thread, loading_progress, loading_message, video_clip, video_clip_duration # Add moviepy globals

    # Clean up previous clip if restarting loading
    if analysis_thread is None and video_clip:
        print("Closing previous video clip."); video_clip.close(); video_clip = None; video_clip_duration = 0.0 # NOQA E701 E501

    if loading_progress==-1: # Error state handling (Identical)
        draw_text(loading_message,font_medium,COLOR_RED,screen,TARGET_GAME_WIDTH//2,TARGET_GAME_HEIGHT//2-50,center=True); bw=TARGET_GAME_WIDTH*0.6; bh=30; bx=(TARGET_GAME_WIDTH-bw)//2; by=TARGET_GAME_HEIGHT//2+20; pygame.draw.rect(screen,COLOR_RED,(bx,by,bw,bh),border_radius=5); draw_text("Press ESC for Menu",font_small,COLOR_WHITE,screen,TARGET_GAME_WIDTH//2,by+50,center=True); # NOQA E701 E501
        for ev in events:
            if ev.type==pygame.QUIT: return False # NOQA E701
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: loading_progress,loading_message,analysis_thread,game_state=0,"",None,STATE_MENU; return True # NOQA E701 E501
        return True
    if analysis_thread is None: # Start loading (Identical)
        loading_progress,loading_message,beatmap_data,audio_waveform_global,sample_rate_global=0,"Starting...",None,None,None # NOQA E701 E501
        if current_song_info:
            aud_p, vid_p = current_song_info.get('audio_path'), current_song_info.get('video_path') # NOQA E701 E501
            if aud_p and vid_p: analysis_thread=threading.Thread(target=_perform_analysis_and_load, args=(aud_p,vid_p,), daemon=True); analysis_thread.start() # NOQA E701 E501
            else: loading_message,loading_progress="Error: Missing path(s).",-1 # NOQA E701 E501
        else: loading_message,loading_progress="Error: No song selected.",-1 # NOQA E701 E501
    # Drawing loading progress (Identical)
    screen.fill(COLOR_DARK_BG); draw_text(loading_message,font_medium,COLOR_WHITE,screen,TARGET_GAME_WIDTH//2,TARGET_GAME_HEIGHT//2-50,center=True); bw=TARGET_GAME_WIDTH*0.6; bh=30; bx=(TARGET_GAME_WIDTH-bw)//2; by=TARGET_GAME_HEIGHT//2+20; pygame.draw.rect(screen,(50,50,70),(bx,by,bw,bh),border_radius=5); # NOQA E701 E501
    if loading_progress>0: fill_w=int(bw*(loading_progress/100.0)); pygame.draw.rect(screen,COLOR_HIT_PERFECT,(bx,by,fill_w,bh),border_radius=5) # NOQA E701 E501
    # Check thread status (Identical logic for music preload)
    if analysis_thread and not analysis_thread.is_alive():
        analysis_thread=None
        if loading_progress==100:
            try: aud_p=current_song_info['audio_path']; print(f"Preload: {aud_p}"); pygame.mixer.music.load(aud_p); print("Music loaded."); game_state=STATE_GAMEPLAY # NOQA E701 E501
            except Exception as e: print(f"Music load fail: {e}"); loading_message="Error: Load audio fail."; loading_progress=-1; # NOQA E701 E501
            if loading_progress==-1 and video_clip: video_clip.close(); video_clip=None # Cleanup moviepy clip if audio fails # NOQA E701 E501
    # Handle ESC event (Identical, but add video_clip cleanup)
    for ev in events:
        if ev.type==pygame.QUIT: return False # NOQA E701
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
            if analysis_thread and analysis_thread.is_alive(): print("Warn: Abort load."); analysis_thread=None # NOQA E701 E501
            if video_clip: video_clip.close(); video_clip=None # NOQA E701
            loading_progress,loading_message,game_state=0,"",STATE_MENU; return True # NOQA E701 E501
    return True

# --- Gameplay State Variables & Helpers ---
gameplay_elements = {"score":0,"combo":0,"max_combo":0,"results":{"PERFECT":0,"GREAT":0,"MISS":0},"upcoming_notes":[],"active_notes":[],"notes_on_screen_for_hit_check":[],"last_feedback":{"text":"","time":-1,"color":COLOR_WHITE},"music_started":False,"playback_start_time":0,"accumulated_offset_ms":0,"game_paused":False,"current_time_sec":0.0} # NOQA E702 E501
last_video_fetch_time = 0.0
video_fetch_interval = 1 / 24.0 # Fetch slightly less often for moviepy performance
combo_text_scale = 1.0
combo_text_scale_timer = 0.0

def update_visualizer(current_sample_index, waveform, sr): # Identical
    global viz_bar_heights
    if waveform is None or sr <= 0 or current_sample_index < 0: viz_bar_heights.fill(0); return # NOQA E701
    win_sz=2048; st=max(0, current_sample_index-win_sz//2); end=min(len(waveform),st+win_sz); win=waveform[st:end] # NOQA E701 E501
    if len(win)<win_sz: win=np.pad(win,(0,win_sz-len(win))) # NOQA E701
    try:
        fft=np.fft.rfft(win*np.hanning(win_sz)); mag=np.abs(fft)/win_sz # NOQA E701 E501
        n_bars=len(viz_bar_heights); freqs=np.fft.rfftfreq(win_sz,1.0/sr); log_max=np.log10(sr/2 if sr > 0 else 1); log_min=np.log10(20 if sr > 20 else 1) # Guard against sr=0 # NOQA E701 E501
        targets=np.logspace(log_min,log_max,n_bars+1); heights=np.zeros(n_bars); # NOQA E701 E501
        for i in range(n_bars):
            f_min, f_max = targets[i], targets[i+1]; bins=np.where((freqs>=f_min)&(freqs<f_max))[0]; # NOQA E701 E501
            if len(bins)>0:
                val=np.mean(mag[bins]); scaled=np.log1p(val*15000)*10; heights[i]=min(1.0,max(0,scaled))*VIZ_MAX_HEIGHT; # NOQA E701 E501
            else: heights[i]=0 # NOQA E701
        viz_bar_heights=np.maximum(heights, viz_bar_heights*0.85) # NOQA E701
    except Exception: viz_bar_heights*=0.8
def draw_visualizer(surface): # Identical
    x=VIZ_X_START; col=(*COLOR_VISUALIZER[:3],180); sz=(VIZ_BAR_WIDTH,VIZ_MAX_HEIGHT); sf=pygame.Surface(sz, pygame.SRCALPHA) # NOQA E701 E501
    for h in viz_bar_heights:
        if h>1: sf.fill((0,0,0,0)); rect=pygame.Rect(0,VIZ_MAX_HEIGHT-h,VIZ_BAR_WIDTH,h); pygame.draw.rect(sf,col,rect); surface.blit(sf,(x,VIZ_Y_POS-VIZ_MAX_HEIGHT)) # NOQA E701 E501
        x+=VIZ_BAR_WIDTH+VIZ_BAR_SPACING
def draw_fallback_background(surface, dt): # Aesthetic addition
    global fallback_bg_scroll_y, fallback_bg_stars # Need stars if modifying list

    speed = 50 * dt # Pixels per second scroll speed
    fallback_bg_scroll_y = (fallback_bg_scroll_y + speed) % TARGET_GAME_HEIGHT

    surface.fill(COLOR_DARK_BG) # Ensure base color

    for x, y_orig, size in fallback_bg_stars:
        y = (y_orig + fallback_bg_scroll_y) % TARGET_GAME_HEIGHT
        # Simple brightness variation based on size
        brightness = 150 + size * 30

        # --- FIX: Clamp color values ---
        r = min(255, max(0, brightness))         # Clamp Red/Green component
        g = min(255, max(0, brightness))         # Clamp Red/Green component
        b = min(255, max(0, int(brightness * 1.1))) # Clamp Blue component
        final_color = (r, g, b)
        # --- END FIX ---

        # Draw using the clamped color
        pygame.draw.circle(surface, final_color, (int(x), int(y)), size)


# --- Game State: Gameplay (Uses moviepy, stop fix) ---
def run_gameplay(events):
    global gameplay_elements, game_state, audio_waveform_global, sample_rate_global, video_clip, video_clip_duration, current_video_frame_surface, last_video_fetch_time, combo_text_scale, combo_text_scale_timer # Modified globals # NOQA E501

    dt = clock.tick(FPS)/1000.0; paused=gameplay_elements["game_paused"]; music_pos_ms=0; ge=gameplay_elements # NOQA E701 E501

    if not ge["music_started"] and not ge["upcoming_notes"] and beatmap_data: # Reset state
        print("Resetting gameplay state."); ge.update({"upcoming_notes":list(beatmap_data),"active_notes":[],"notes_on_screen_for_hit_check":[],"score":0,"combo":0,"max_combo":0,"results":{"PERFECT":0,"GREAT":0,"MISS":0},"accumulated_offset_ms":0,"game_paused":False,"current_time_sec":0.0}); combo_text_scale=1.0; combo_text_scale_timer=0.0 # NOQA E701 E501
        # No seek needed for moviepy, time is calculated directly

    if not paused: # Timing and Music/Video Start
        if not ge["music_started"] and beatmap_data:
            try: pygame.mixer.music.play(); ge["music_started"],ge["playback_start_time"]=True,time.monotonic(); print("Gameplay started.") # NOQA E701 E501
            except Exception as e: print(f"Start fail: {e}"); ge["last_feedback"]={"text":"START FAIL","time":ge["current_time_sec"],"color":COLOR_RED} # NOQA E701 E501
        elif ge["music_started"]:
             music_pos_ms = pygame.mixer.music.get_pos()+ge["accumulated_offset_ms"]
             if music_pos_ms < ge["accumulated_offset_ms"]-100: # End condition check
                 if not ge["upcoming_notes"] and not ge["active_notes"]:
                     print("End of song detected.");
                     try: pygame.mixer.music.stop(); print("Music stopped.") # Explicit stop
                     except Exception as e: print(f"Error stopping music at end: {e}")
                     if video_clip: video_clip.close(); video_clip=None; print("Video clip closed.") # Close moviepy clip # NOQA E701 E501
                     game_state=STATE_GAME_OVER; set_high_score(current_song_info.get('id',''), ge['score']); return True # NOQA E701 E501
                 else: print("Warn: Mixer pos."); music_pos_ms=int((time.monotonic()-ge["playback_start_time"])*1000)+ge["accumulated_offset_ms"] # NOQA E701 E501
    ge["current_time_sec"]=music_pos_ms/1000.0; cur_t=ge["current_time_sec"] # NOQA E701 E501

    if combo_text_scale_timer>0: # Combo scale effect (Identical)
        combo_text_scale_timer-=dt;
        if combo_text_scale_timer>0.1: combo_text_scale=1.0+(0.2-combo_text_scale_timer)*2.0 # NOQA E701
        else: combo_text_scale=1.0+combo_text_scale_timer*2.0 # NOQA E701
        combo_text_scale=max(1.0,min(1.4,combo_text_scale)) # NOQA E701
    else: combo_text_scale=1.0

    # --- Event Handling ---
    for event in events:
        if event.type == pygame.QUIT: return False
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_PAUSE: # Pause Handling
                ge["game_paused"] = not paused
                try:
                    if ge["game_paused"]: pygame.mixer.music.pause() # Moviepy doesn't need explicit pause
                    else: pygame.mixer.music.unpause()
                except Exception as pause_err: print(f"Pause/Unpause Error: {pause_err}")
            elif event.key == KEY_BACK and paused: # Escape Handling
                try: pygame.mixer.music.stop(); print("Music stopped on escape.") # Stop music # NOQA E701
                except: pass
                ge["music_started"] = False
                if video_clip: video_clip.close(); video_clip = None; print("Video closed on escape.")# Close moviepy clip # NOQA E701
                game_state = STATE_MENU; return True
            elif not paused: # Hit Detection (Identical logic)
                target_lane = None
                if event.key == KEY_GROUND: target_lane = "ground"
                elif event.key == KEY_AIR: target_lane = "air"
                if target_lane:
                    try:
                        best_note_to_hit = None; min_abs_diff_ms = MISS_WINDOW_MS # NOQA E701
                        candidates = [n for n in ge["notes_on_screen_for_hit_check"] if n.lane == target_lane]
                        for note in candidates: note_res, t_diff = note.check_hit_timing(cur_t); abs_diff = abs(t_diff); # NOQA E701 E501
                        if note_res and abs_diff < min_abs_diff_ms: min_abs_diff_ms = abs_diff; best_note_to_hit = note # NOQA E701 E501
                        if best_note_to_hit:
                            result, _ = best_note_to_hit.check_hit_timing(cur_t)
                            if result and "MISS" not in result:
                                score_gain = 300 if result=="PERFECT" else 100; color = COLOR_HIT_PERFECT if result=="PERFECT" else COLOR_HIT_GREAT # NOQA E701 E501
                                ge["score"]+=score_gain*max(1,ge["combo"]); ge["combo"]+=1; best_note_to_hit.feedback_color=color; combo_text_scale_timer = 0.2; # NOQA E701 E501
                                best_note_to_hit.is_hit,best_note_to_hit.is_active,best_note_to_hit.hit_result=True,False,result; best_note_to_hit.hit_feedback_timer,best_note_to_hit.effect_scale=0.3,1.0; ge["results"][result]+=1; ge["last_feedback"]={"text":result,"time":cur_t,"color":color} # NOQA E701 E501
                                if best_note_to_hit in ge["notes_on_screen_for_hit_check"]: ge["notes_on_screen_for_hit_check"].remove(best_note_to_hit) # NOQA E701 E501
                            else: best_note_to_hit.is_missed,best_note_to_hit.is_active,best_note_to_hit.hit_result=True,False,"MISS (Timing)"; ge["results"]["MISS"]+=1; ge["combo"]=0; ge["last_feedback"]={"text":"MISS","time":cur_t,"color":COLOR_RED} # NOQA E701 E501
                            if best_note_to_hit in ge["notes_on_screen_for_hit_check"]: ge["notes_on_screen_for_hit_check"].remove(best_note_to_hit) # NOQA E701 E501
                        else: ge["combo"]=0; ge["results"]["MISS"]+=1; ge["last_feedback"]={"text":"MISS","time":cur_t,"color":COLOR_RED} # NOQA E701 E501
                    except Exception as hit_err: print(f"Hit Error: {hit_err}"); traceback.print_exc() # NOQA E701 E501

    # --- Gameplay Logic ---
    if not paused:
        # Note spawning/updating (Identical)
        spawn_indices = []; # NOQA: E701
        for i, note in enumerate(ge["upcoming_notes"]):
            if cur_t >= note.spawn_time_sec: spawn_indices.append(i); note.is_active = True; ge["active_notes"].append(note); # NOQA: E701 E501
        for i in sorted(spawn_indices, reverse=True): ge["upcoming_notes"].pop(i); # NOQA: E701
        notes_to_remove = []; cur_hit_check = []; # NOQA: E701
        hit_start_x = TARGET_GROUND_POS[0]-NOTE_SPEED*(MISS_WINDOW_MS/1000.0)*1.5; hit_end_x = TARGET_GROUND_POS[0]+NOTE_SPEED*(MISS_WINDOW_MS/1000.0)*1.5 # NOQA: E701 E501
        for note in ge["active_notes"]:
            note.update(cur_t, dt)
            if note.is_active and not note.is_hit and not note.is_missed and hit_start_x<=note.x<=hit_end_x: cur_hit_check.append(note); # NOQA: E701 E501
            if note.is_missed:
                if note.hit_result=="MISS (Timeout)": ge["results"]["MISS"]+=1; ge["combo"]=0; # NOQA E701 E501
                notes_to_remove.append(note)
                if note in ge["notes_on_screen_for_hit_check"]: ge["notes_on_screen_for_hit_check"].remove(note); # NOQA E701 E501
            elif note.is_hit and note.hit_feedback_timer<=0: notes_to_remove.append(note); # NOQA E701
        ge["notes_on_screen_for_hit_check"]=cur_hit_check
        ge["active_notes"]=[n for n in ge["active_notes"] if n not in notes_to_remove]
        if ge["combo"]>ge["max_combo"]: ge["max_combo"]=ge["combo"]; # NOQA E701
        # Update Visualizer (Identical)
        cur_sample=int(cur_t*sample_rate_global) if sample_rate_global else -1; update_visualizer(cur_sample,audio_waveform_global,sample_rate_global); # NOQA E701 E501

        # --- Fetch and Update Video Frame using Moviepy ---
        if MOVIEPY_AVAILABLE and video_clip and cur_t >= last_video_fetch_time + video_fetch_interval:
             last_video_fetch_time = cur_t
             try:
                 # Calculate looped video time
                 video_time = cur_t % video_clip_duration if video_clip_duration > 0 else 0
                 frame_array = video_clip.get_frame(video_time) # Get numpy array
                 # Convert to Pygame surface (H, W, C) -> (W, H)
                 frame_surface = pygame.image.frombuffer(frame_array.tobytes(), frame_array.shape[1::-1], "RGB")
                 # Scale immediately
                 current_video_frame_surface = pygame.transform.scale(frame_surface, (TARGET_GAME_WIDTH, TARGET_GAME_HEIGHT))
             except Exception as frame_err:
                  print(f"Error getting/processing moviepy frame at {video_time:.2f}s: {frame_err}")
                  # Keep the last good frame if available, otherwise None
                  # current_video_frame_surface = current_video_frame_surface

        # --- Drawing ---
        # 1. Draw Background (Video or Fallback)
        if current_video_frame_surface:  # Use the fetched and scaled frame
            screen.blit(current_video_frame_surface, (0, 0))
        else:
            draw_fallback_background(screen, dt)  # Use fallback

        # --- ADD: Draw Semi-Transparent Overlay ---
        if BACKGROUND_OPACITY > 0:  # Only draw if opacity is set
            overlay_surface = pygame.Surface((TARGET_GAME_WIDTH, TARGET_GAME_HEIGHT), pygame.SRCALPHA)
            overlay_surface.fill((0, 0, 0, BACKGROUND_OPACITY))  # Black with alpha
            screen.blit(overlay_surface, (0, 0))
        # --- END: Overlay ---

        # 2. Draw Lane Lines (Now drawn ON TOP of the dimmed background)
        pygame.draw.line(screen, COLOR_LANE_LINE, (0, TARGET_GROUND_POS[1]), (TARGET_GAME_WIDTH, TARGET_GROUND_POS[1]),
                         2)
        pygame.draw.line(screen, COLOR_LANE_LINE, (0, TARGET_AIR_POS[1]), (TARGET_GAME_WIDTH, TARGET_AIR_POS[1]), 2)

        # 3. Draw Visualizer
        draw_visualizer(screen)

        # 4. Draw Pulsing Target Circles
        # ... (Target drawing logic remains the same) ...
        pulse_factor = (math.sin(time.time() * 5) + 1) / 2;
        current_target_radius = TARGET_RADIUS * (1.0 + pulse_factor * 0.08);
        ts = pygame.Surface((current_target_radius * 2, current_target_radius * 2), pygame.SRCALPHA);  # NOQA E701 E501
        pygame.draw.circle(ts, COLOR_TARGET_GROUND, (current_target_radius, current_target_radius),
                           current_target_radius);
        pygame.draw.circle(ts, COLOR_WHITE, (current_target_radius, current_target_radius), current_target_radius, 2);
        screen.blit(ts, (
        TARGET_GROUND_POS[0] - current_target_radius, TARGET_GROUND_POS[1] - current_target_radius));  # NOQA E701 E501
        ts.fill((0, 0, 0, 0));
        pygame.draw.circle(ts, COLOR_TARGET_AIR, (current_target_radius, current_target_radius), current_target_radius);
        pygame.draw.circle(ts, COLOR_WHITE, (current_target_radius, current_target_radius), current_target_radius, 2);
        screen.blit(ts, (
        TARGET_AIR_POS[0] - current_target_radius, TARGET_AIR_POS[1] - current_target_radius));  # NOQA E701 E501

        # 5. Draw Notes & Effects
        # ... (Note drawing logic remains the same) ...
        for note in notes_to_remove:
            if note.is_hit and note.hit_feedback_timer > 0: note.draw(screen);  # NOQA E701
        for note in ge["active_notes"]: note.draw(screen);  # NOQA E701

        # 6. Draw UI (Score, Combo, Feedback)
        # ... (UI drawing logic remains the same) ...
        score_rend = font_large.render(f"{ge['score']:08d}", True, COLOR_SCORE);
        score_rect = score_rend.get_rect(right=TARGET_GAME_WIDTH - 20, centery=int(TARGET_GAME_HEIGHT * 0.05));
        screen.blit(score_rend, score_rect);  # NOQA E701 E501
        if ge["combo"] > 1:
            scaled_font_size = int(font_large.get_height() * combo_text_scale)
            try:
                combo_font = pygame.font.Font(None, scaled_font_size)
            except:
                combo_font = font_large  # Fallback
            draw_text(f"{ge['combo']}x", combo_font, COLOR_COMBO, screen, TARGET_GAME_WIDTH // 2,
                      int(TARGET_GAME_HEIGHT * 0.12), center=True)  # NOQA E701 E501
        if cur_t - ge["last_feedback"]["time"] < 0.6: fb_surf = font_medium.render(ge["last_feedback"]["text"], True,
                                                                                   ge["last_feedback"][
                                                                                       "color"]); fb_rect = fb_surf.get_rect(
            center=(TARGET_GROUND_POS[0] + int(TARGET_GAME_WIDTH * 0.1), TARGET_GAME_HEIGHT // 2)); screen.blit(fb_surf,
                                                                                                                fb_rect);  # NOQA E701 E501

        # 7. Draw Pause Overlay (On top of everything else)
        if paused: overlay = pygame.Surface((TARGET_GAME_WIDTH, TARGET_GAME_HEIGHT), pygame.SRCALPHA); overlay.fill(
            (0, 0, 0, 180)); screen.blit(overlay, (0, 0)); draw_text("PAUSED", font_large, COLOR_WHITE, screen,
                                                                     TARGET_GAME_WIDTH // 2,
                                                                     TARGET_GAME_HEIGHT // 2 - 40,
                                                                     center=True); draw_text("Press P to Resume",
                                                                                             font_small, COLOR_WHITE,
                                                                                             screen,
                                                                                             TARGET_GAME_WIDTH // 2,
                                                                                             TARGET_GAME_HEIGHT // 2 + 30,
                                                                                             center=True); draw_text(
            "Press ESC for Menu", font_small, COLOR_WHITE, screen, TARGET_GAME_WIDTH // 2, TARGET_GAME_HEIGHT // 2 + 60,
            center=True);  # NOQA E701 E501
        return True

# --- Game State: Game Over (Added music stop) ---
def run_game_over(events):
    global game_state, gameplay_elements, preview_playing, preview_sound, video_clip # Need video clip global

    # --- Stop music/preview/video when entering Game Over state ---
    if pygame.mixer.music.get_busy():
        try: pygame.mixer.music.stop() # NOQA E701
        except:
            pass
    if preview_playing and preview_sound:
        try: preview_sound.stop();
        except:
            pass; preview_playing=False; preview_sound=None # NOQA E701 E501
    if video_clip:
        try:
            video_clip.close();
        except:
            pass; video_clip = None # NOQA E701 E501
    # -----------------------------------------------------------

    screen.fill(COLOR_DARK_BG); draw_text("Game Over", font_large, COLOR_WHITE, screen, TARGET_GAME_WIDTH // 2, int(TARGET_GAME_HEIGHT*0.15), center=True); ge = gameplay_elements; stats_y = int(TARGET_GAME_HEIGHT*0.3); line_h = int(font_medium.get_height() * 1.1); # NOQA E701 E501
    # ... (Rest of drawing logic is identical) ...
    draw_text(f"Song: {current_song_info.get('title','?')[:40]}", font_medium, COLOR_WHITE, screen, TARGET_GAME_WIDTH // 2, stats_y, center=True); stats_y += line_h * 1.5 # NOQA E701 E501
    draw_text(f"Final Score: {ge['score']}", font_medium, COLOR_SCORE, screen, TARGET_GAME_WIDTH // 2, stats_y, center=True); stats_y += line_h # NOQA E701 E501
    hs = get_high_score(current_song_info.get('id','')); draw_text(f"High Score: {hs}", font_small, (200,200,100), screen, TARGET_GAME_WIDTH // 2, stats_y, center=True); stats_y += line_h * 1.5 # NOQA E701 E501
    draw_text(f"Max Combo: {ge['max_combo']}", font_medium, COLOR_COMBO, screen, TARGET_GAME_WIDTH // 2, stats_y, center=True); stats_y += line_h * 1.5 # NOQA E701 E501
    results_x = int(TARGET_GAME_WIDTH * 0.3); results_val_x = int(TARGET_GAME_WIDTH * 0.7) # NOQA E701 E501
    draw_text(f"Perfect:", font_medium, COLOR_HIT_PERFECT, screen, results_x, stats_y, center_y=True); draw_text(f"{ge['results']['PERFECT']}", font_medium, COLOR_HIT_PERFECT, screen, results_val_x, stats_y, center_y=True); stats_y += line_h # NOQA E701 E501
    draw_text(f"Great:", font_medium, COLOR_HIT_GREAT, screen, results_x, stats_y, center_y=True); draw_text(f"{ge['results']['GREAT']}", font_medium, COLOR_HIT_GREAT, screen, results_val_x, stats_y, center_y=True); stats_y += line_h # NOQA E701 E501
    draw_text(f"Miss:", font_medium, COLOR_RED, screen, results_x, stats_y, center_y=True); draw_text(f"{ge['results']['MISS']}", font_medium, COLOR_RED, screen, results_val_x, stats_y, center_y=True); stats_y += line_h * 2 # NOQA E701 E501
    draw_text("Press ESC for Menu", font_medium, COLOR_WHITE, screen, TARGET_GAME_WIDTH // 2, stats_y, center=True)
    for event in events:
        if event.type == pygame.QUIT: return False
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_BACK: game_state = STATE_MENU; return True # NOQA E701
    return True

# --- Main Game Execution ---
game_state = STATE_MENU
def run_game():
    global game_state, video_clip, preview_playing, preview_sound # Add video_clip for cleanup
    init_pygame()
    load_library(); load_high_scores() # NOQA: E702
    running = True
    while running:
        events = pygame.event.get()
        if game_state == STATE_MENU: running = run_menu(events)
        elif game_state == STATE_LOADING: running = run_loading(events)
        elif game_state == STATE_GAMEPLAY: running = run_gameplay(events)
        elif game_state == STATE_GAME_OVER: running = run_game_over(events)
        else: print(f"Error: Unknown state {game_state}"); running = False # NOQA: E701

        pygame.display.flip()

    # --- Cleanup --- (Added video_clip close)
    if preview_playing and preview_sound:
        try:
            preview_sound.stop();
        except:
            pass # NOQA E701
    try: pygame.mixer.music.stop();
    except:
        pass # NOQA E701
    if video_clip:
        print("Closing video clip...");
        try:
            video_clip.close();
        except:
            pass; video_clip = None # NOQA E701 E501
    pygame.quit()
    print("Game exited.")

if __name__ == "__main__":
    import random # Needed for fallback background
    import shutil
    if shutil.which("ffmpeg") is None:
         print("\n--- WARNING ---"); print("FFmpeg not found in PATH."); print("Video/Audio ops might fail."); print("Download FFmpeg and add to PATH."); print("---------------\n") # NOQA E701 E501
    run_game()