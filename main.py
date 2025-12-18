import pygame
import mido
import menu
import game_draw
import game_logic
import time
import os
import math
from songs import find_songs, load_song
from draw_utils import draw_gear
import cv2

# Try to import MediaPipe for better hand detection; fall back gracefully
try:
    import mediapipe as mp
    HAVE_MEDIAPIPE = True
except Exception:
    HAVE_MEDIAPIPE = False

# ---------- CONFIG ----------
SONG_DIR = "songs"
# Number of lanes for each input method
LANES_KEYBOARD = 4
LANES_CAMERA = 4
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_LABELS = ["D", "F", "J", "K"]

# Color presets for blocks
BLOCK_COLORS = [
    (0, 200, 200),  # Cyan
    (255, 50, 50),  # Red
    (50, 255, 50),  # Green
    (200, 0, 200),  # Purple
    (255, 165, 0)   # Orange
]

# ---------- INIT ----------
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("MIDI Hero")

clock = pygame.time.Clock()

font_small = pygame.font.Font(None, 32)
font_medium = pygame.font.Font(None, 48)
font_big = pygame.font.Font(None, 72)

# Optional scoreboard background image (shown for end-of-song scoreboard)
scoreboard_bg = None
try:
    if os.path.exists("scoreboard.png"):
        scoreboard_bg = pygame.image.load("scoreboard.png").convert_alpha()
except Exception:
    scoreboard_bg = None

# Optional title image
title_img = None
try:
    if os.path.exists("title.png"):
        title_img = pygame.image.load("title.png").convert_alpha()
except Exception:
    title_img = None

# Optional cat background for main menu (static first frame of cat.gif)
cat_bg = None
try:
    if os.path.exists("cat.gif"):
        try:
            # Try to load animated frames via Pillow
            from PIL import Image
            im = Image.open("cat.gif")
            frames = []
            durations = []
            try:
                while True:
                    frame = im.convert('RGBA')
                    fw, fh = frame.size
                    mode = frame.mode
                    data = frame.tobytes()
                    surf = pygame.image.frombuffer(data, (fw, fh), 'RGBA').convert_alpha()
                    frames.append(surf)
                    # duration in seconds
                    dur = im.info.get('duration', 100) / 1000.0
                    durations.append(dur)
                    im.seek(im.tell() + 1)
            except EOFError:
                pass
            if frames:
                cat_bg = {
                    'frames': frames,
                    'durations': durations,
                    'index': 0,
                    'last_time': time.time()
                }
            else:
                cat_bg = None
        except Exception:
            # Pillow not available or failed; fall back to single-frame load
            try:
                cat_s = pygame.image.load("cat.gif").convert_alpha()
                cat_bg = cat_s
            except Exception:
                cat_bg = None
except Exception:
    cat_bg = None

# ---------- CAMERA / HAND INPUT (optional) ----------
camera_enabled = False
cap = None
mp_hands = None
hand_hit_cooldown = 0.35
# last_hand_hit_time will be kept in sync with the active lane count below
last_hand_hit_time = [0.0] * LANES_KEYBOARD

use_camera_controls = False
camera_available = False
camera_inverted = False
if HAVE_MEDIAPIPE:
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap is not None and cap.isOpened():
            camera_available = True
            mp_hands = mp.solutions.hands.Hands(static_image_mode=False,
                                                max_num_hands=2,
                                                min_detection_confidence=0.5,
                                                min_tracking_confidence=0.5)
        else:
            camera_available = False
    except Exception as e:
        print("Camera init failed:", e)
        camera_available = False
else:
    camera_available = False

# ---------- LOAD SONGS ----------
songs = []
if not os.path.exists(SONG_DIR):
    os.makedirs(SONG_DIR)

songs = find_songs(SONG_DIR)

if not songs:
    print(f"No songs found in {SONG_DIR}/. Using dummy logic.")

# ---------- SETTINGS STATE ----------
difficulty_level = 1
MOEILIJKHEID = 100  # Startwaarde
current_color_idx = 0
show_settings = False
settings_from_pause = False

# ---------- MENU STATE ----------
selected_song = 0
in_menu = True
running = True
awaiting_name = False
pending_song_index = None
player_name = ""
current_song_key = None
scores_file = "scores.json"
show_scoreboard = False
scoreboard_entries = []
current_song_length = 0.0
end_of_song = False
bar_full_at = None  # timestamp when progress bar first reached 100%

# ---------- GAME STATE ----------
started = False
music_started = False
start_time = None
active_blocks = []
active_pieces = []
notes = []
score = 0
score_multiplier = 1
music_play_scheduled = False
music_play_time = None
paused = False
pause_start = None
pause_offset = 0
error_flash = 0  
pause_button_selected = 0  # 0 = Back, 1 = Settings, 2 = Exit
streak = 0
last_hand_positions = []
last_frame_preview = None

# ---------- CONSTANTS ----------
LANE_SPACING = 20
lane_width = int(screen.get_width() * 0.12)
# pixels per second for block movement (must match game_logic)
PIXELS_PER_SECOND = 300
# lane_area_width and lane_left are computed per-frame based on active lanes
lane_area_width = lane_width * LANES_KEYBOARD + LANE_SPACING * (LANES_KEYBOARD - 1)
lane_left = (screen.get_width() - lane_area_width) // 2
hit_y = int(screen.get_height() * 0.8)
hit_window = 40

# Gear Icon Area
gear_rect = pygame.Rect(screen.get_width() - 80, 30, 50, 50)

# ---------- SCOREBOARD HELPERS ----------
def _load_scores_file(path):
    try:
        import json
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_scores_file(path, data):
    try:
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def save_score_entry(song_key, name, sc, level, path):
    scores = _load_scores_file(path)
    lst = scores.get(song_key, [])
    from datetime import datetime
    entry = {"name": name, "score": sc, "level": level, "date": datetime.now().isoformat()}
    lst.append(entry)
    lst = sorted(lst, key=lambda x: x.get('score', 0), reverse=True)[:50]
    scores[song_key] = lst
    _save_scores_file(path, scores)
    return lst

# ---------- FUNCTIONS ----------
# load_song and draw_gear moved to separate modules: songs.py and draw_utils.py

def _seg_intersects_rect(p1, p2, rect):
    # p1, p2 are (x,y). rect is pygame.Rect
    # quick check: either endpoint inside rect
    if rect.collidepoint(p1) or rect.collidepoint(p2):
        return True

    # helper for segment intersection
    def _orient(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

    def _on_segment(a, b, c):
        return min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])

    a = p1; b = p2
    # rectangle corners
    rx1, ry1 = rect.topleft
    rx2, ry2 = rect.topright
    rx3, ry3 = rect.bottomright
    rx4, ry4 = rect.bottomleft
    edges = [((rx1, ry1), (rx2, ry2)), ((rx2, ry2), (rx3, ry3)),
             ((rx3, ry3), (rx4, ry4)), ((rx4, ry4), (rx1, ry1))]

    for (c, d) in edges:
        o1 = _orient(a, b, c)
        o2 = _orient(a, b, d)
        o3 = _orient(c, d, a)
        o4 = _orient(c, d, b)

        if o1 == 0 and _on_segment(a, b, c):
            return True
        if o2 == 0 and _on_segment(a, b, d):
            return True
        if o3 == 0 and _on_segment(c, d, a):
            return True
        if o4 == 0 and _on_segment(c, d, b):
            return True

        if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0):
            return True

    return False
# ---------- MAIN LOOP ----------
background = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # If scoreboard is showing in the main menu, any key or click closes it and returns to menu
        if show_scoreboard and in_menu and (event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)):
            show_scoreboard = False
            end_of_song = False
            in_menu = True
            background = None
            player_name = ""
            current_song_key = None
            active_blocks.clear()
            active_pieces.clear()
            notes = []
            score = 0
            music_started = False
            started = False
            bar_full_at = None
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if show_settings:
                show_settings = False
                # If settings were opened from the pause menu, return to paused gameplay
                if settings_from_pause:
                    in_menu = False
                    paused = True
                    settings_from_pause = False
            elif in_menu:
                running = False
            else:
                # Toggle pause in-game
                if not paused:
                    paused = True
                    pause_start = time.time()
                    pause_button_selected = 0
                    try: pygame.mixer.music.pause()
                    except: pass
                else:
                    paused = False
                    if pause_start:
                        pause_offset += time.time() - pause_start
                    pause_start = None
                    try: pygame.mixer.music.unpause()
                    except: pass

        # -------- MOUSE INPUT (GLOBAL) --------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            # 1. Handle Settings Menu Clicks
            if in_menu and show_settings:
                cx = screen.get_width() // 2
                cy = screen.get_height() // 2
                
                # Difficulty Rects
                diff_left = pygame.Rect(cx - 150, cy - 100, 40, 40)
                diff_right = pygame.Rect(cx + 110, cy - 100, 40, 40)
                
                # Color Rects
                col_left = pygame.Rect(cx - 150, cy + 40, 40, 40)
                col_right = pygame.Rect(cx + 110, cy + 40, 40, 40)

                # Input method rects
                im_left = pygame.Rect(cx - 150, cy + 140, 40, 40)
                im_right = pygame.Rect(cx + 110, cy + 140, 40, 40)

                # Invert camera toggle rect
                inv_label_y = cy + 190
                inv_rect = pygame.Rect(cx - 60, cy + 210, 120, 36)
                
                # Close Button (moved down to make space)
                close_rect = pygame.Rect(cx - 100, cy + 270, 200, 50)

                if diff_left.collidepoint(mx, my):
                    if difficulty_level > 1: difficulty_level -= 1
                elif diff_right.collidepoint(mx, my):
                    if difficulty_level < 3: difficulty_level += 1
                
                elif col_left.collidepoint(mx, my):
                    current_color_idx = (current_color_idx - 1) % len(BLOCK_COLORS)
                elif col_right.collidepoint(mx, my):
                    current_color_idx = (current_color_idx + 1) % len(BLOCK_COLORS)

                elif im_left.collidepoint(mx, my):
                    # select keyboard
                    use_camera_controls = False
                elif im_right.collidepoint(mx, my):
                    # try to enable camera if available
                    if camera_available:
                        use_camera_controls = True
                    else:
                        print("Camera not available on this system.")
                elif inv_rect.collidepoint(mx, my):
                    # toggle invert
                    camera_inverted = not camera_inverted
                
                elif close_rect.collidepoint(mx, my):
                    show_settings = False
                    # If settings were opened from pause, go back to paused game view
                    if settings_from_pause:
                        in_menu = False
                        paused = True
                        settings_from_pause = False

                # Update difficulty constant
                if difficulty_level == 3: MOEILIJKHEID = 50
                elif difficulty_level == 2: MOEILIJKHEID = 75
                elif difficulty_level == 1: MOEILIJKHEID = 100

            # 2. Handle Main Menu Clicks (Gear)
            elif in_menu and not show_settings:
                if gear_rect.collidepoint(mx, my):
                    show_settings = True
                    settings_from_pause = False

            # 2b. Handle Settings overlay clicks while in-game (opened from pause)
            elif show_settings and not in_menu:
                cx = screen.get_width() // 2
                cy = screen.get_height() // 2

                # Difficulty Rects
                diff_left = pygame.Rect(cx - 150, cy - 100, 40, 40)
                diff_right = pygame.Rect(cx + 110, cy - 100, 40, 40)

                # Color Rects
                col_left = pygame.Rect(cx - 150, cy + 40, 40, 40)
                col_right = pygame.Rect(cx + 110, cy + 40, 40, 40)

                # Close Button
                close_rect = pygame.Rect(cx - 100, cy + 200, 200, 50)

                if diff_left.collidepoint(mx, my):
                    if difficulty_level > 1: difficulty_level -= 1
                elif diff_right.collidepoint(mx, my):
                    if difficulty_level < 3: difficulty_level += 1

                elif col_left.collidepoint(mx, my):
                    current_color_idx = (current_color_idx - 1) % len(BLOCK_COLORS)
                elif col_right.collidepoint(mx, my):
                    current_color_idx = (current_color_idx + 1) % len(BLOCK_COLORS)

                elif close_rect.collidepoint(mx, my):
                    show_settings = False
                    if settings_from_pause:
                        # return to paused gameplay
                        in_menu = False
                        paused = True
                        settings_from_pause = False

                # Update difficulty constant
                if difficulty_level == 3: MOEILIJKHEID = 50
                elif difficulty_level == 2: MOEILIJKHEID = 75
                elif difficulty_level == 1: MOEILIJKHEID = 100

            # 3. Handle Pause Menu Clicks (Back, Settings, Exit)
            elif not in_menu and paused:
                bw, bh, spacing = 360, 56, 20
                cx = screen.get_rect().centerx
                total_h = bh * 3 + spacing * 2
                top_y = screen.get_height() // 2 - total_h // 2
                bx = cx - bw // 2
                back_rect = pygame.Rect(bx, top_y, bw, bh)
                settings_rect = pygame.Rect(bx, top_y + (bh + spacing), bw, bh)
                exit_rect = pygame.Rect(bx, top_y + 2 * (bh + spacing), bw, bh)

                if back_rect.collidepoint(mx, my):
                    in_menu = True
                    background = None
                    show_settings = False
                    try: pygame.mixer.music.stop()
                    except: pass
                    started = False
                    paused = False
                    music_started = False
                    start_time = None
                    active_blocks.clear()
                    score = 0
                    for n in notes:
                        if "spawned" in n: del n["spawned"]
                elif settings_rect.collidepoint(mx, my):
                    # Open settings from pause without switching to the song-selection menu
                    show_settings = True
                    settings_from_pause = True
                    # keep started/paused state so we can return
                elif exit_rect.collidepoint(mx, my):
                    try: pygame.mixer.music.stop()
                    except: pass
                    running = False

        # -------- MENU INPUT (KEYBOARD) --------
        if in_menu and not show_settings:
            # If awaiting name input overlay, handle typing here
            if awaiting_name:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        # commit name and start song
                        awaiting_name = False
                        if player_name.strip() == "":
                            player_name = "Player"
                        # load the pending song
                        if pending_song_index is not None and songs:
                            bg, notes, length = load_song(songs[pending_song_index], screen)
                            background = bg
                            active_blocks.clear()
                            active_pieces.clear()
                            score = 0
                            started = False
                            music_started = False
                            in_menu = False
                            current_song_key = songs[pending_song_index]["name"]
                            current_song_length = length
                            pending_song_index = None
                            bar_full_at = None
                    elif event.key == pygame.K_ESCAPE:
                        awaiting_name = False
                        pending_song_index = None
                    else:
                        # append printable characters
                        if event.unicode and len(player_name) < 20:
                            player_name += event.unicode
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if songs: selected_song = (selected_song + 1) % len(songs)
                elif event.key == pygame.K_UP:
                    if songs: selected_song = (selected_song - 1) % len(songs)
                elif event.key == pygame.K_RETURN:
                    if songs:
                        # prompt for player name before starting
                        awaiting_name = True
                        pending_song_index = selected_song

        # -------- GAME INPUT (KEYBOARD) --------
        if not in_menu:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not started:
                start_time = time.time()
                started = True
                paused = False
                pause_start = None
                pause_offset = 0
                # schedule playback after visual lead time so notes match blocks
                # use block center (half the block height) so the note plays when
                # the hitline crosses the middle of the block
                block_center_offset = MOEILIJKHEID / 2
                lead_time = (hit_y - block_center_offset) / PIXELS_PER_SECOND
                music_play_time = start_time + lead_time
                music_play_scheduled = True
                bar_full_at = None

            elif event.type == pygame.KEYDOWN and started and not paused:
                if event.key in LANE_KEYS:
                    lane_index = LANE_KEYS.index(event.key)
                    
                    # --- HIER ZAT DE FOUT: VARIABELE NAAM ---
                    hit_any = False

                    for block in active_blocks:
                        b_lane = int((block["rect"].centerx - lane_left) // (lane_width + LANE_SPACING))
                        if b_lane == lane_index:
                            # Use MOEILIJKHEID as hit window (centered check by update_game)
                            if abs(block["rect"].y - hit_y) < MOEILIJKHEID:
                                score += 100 * score_multiplier
                                block["color"] = (0, 255, 0)  # green feedback
                                block["hit"] = True
                                hit_any = True
                                break

                    if hit_any:
                        streak += 1
                        # enable 2x booster when streak reaches 25
                        if streak >= 25:
                            score_multiplier = 2
                        if streak >= 100:
                            score_multiplier = 3
                        if streak >= 250:
                            score_multiplier = 5
                    else:
                        streak = 0
                        score_multiplier = 1
                        score -= 20
                        error_flash = 15

            # Mouse hover for pause menu
            if paused and event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                bw, bh, spacing = 360, 56, 20
                cx = screen.get_rect().centerx
                total_h = bh * 3 + spacing * 2
                top_y = screen.get_height() // 2 - total_h // 2
                bx = cx - bw // 2
                back_rect = pygame.Rect(bx, top_y, bw, bh)
                settings_rect = pygame.Rect(bx, top_y + (bh + spacing), bw, bh)
                exit_rect = pygame.Rect(bx, top_y + 2 * (bh + spacing), bw, bh)

                if back_rect.collidepoint(mx, my):
                    pause_button_selected = 0
                elif settings_rect.collidepoint(mx, my):
                    pause_button_selected = 1
                elif exit_rect.collidepoint(mx, my):
                    pause_button_selected = 2

            # Keyboard nav for pause (Back, Settings, Exit)
            if paused and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    pause_button_selected = (pause_button_selected + 1) % 3
                elif event.key in (pygame.K_UP, pygame.K_w):
                    pause_button_selected = (pause_button_selected - 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if pause_button_selected == 0:
                        in_menu = True
                        background = None
                        show_settings = False
                        try: pygame.mixer.music.stop()
                        except: pass
                        started = False
                        paused = False
                        music_started = False
                        start_time = None
                        active_blocks.clear()
                        score = 0
                        for n in notes:
                            if "spawned" in n: del n["spawned"]
                    elif pause_button_selected == 1:
                        # Open settings from pause without switching to song-selection
                        show_settings = True
                        settings_from_pause = True
                    else:
                        try: pygame.mixer.music.stop()
                        except: pass
                        running = False

    # ---------- DRAW MENU ----------
    if in_menu:
        menu.render_menu(screen, songs, selected_song, show_settings,
                         difficulty_level, current_color_idx, BLOCK_COLORS,
                         font_small, font_medium, font_big, gear_rect,
                         use_camera=use_camera_controls, camera_available=camera_available,
                         camera_inverted=camera_inverted, background_image=cat_bg, title_image=title_img)

        # Draw name entry overlay if awaiting_name
        if awaiting_name:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            w, h = screen.get_size()
            title = font_big.render("Enter Your Name", True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(w//2, h//2 - 100)))
            box_rect = pygame.Rect(w//2 - 300, h//2 - 30, 600, 72)
            pygame.draw.rect(screen, (40,40,40), box_rect, border_radius=8)
            pygame.draw.rect(screen, (200,200,200), box_rect, 2, border_radius=8)
            name_text = player_name if player_name else "Type your name..."
            txt = font_medium.render(name_text, True, (230,230,230))
            screen.blit(txt, txt.get_rect(midleft=(box_rect.x + 16, box_rect.centery)))
            hint = font_small.render("Press ENTER to confirm — ESC to cancel", True, (180,180,180))
            screen.blit(hint, hint.get_rect(center=(w//2, h//2 + 60)))

        # Draw scoreboard overlay if requested
        if show_scoreboard:
            # If this scoreboard is shown as end-of-song overlay and a background image
            # is available, draw it behind the translucent overlay for a nicer look.
            if end_of_song and scoreboard_bg is not None:
                try:
                    bg_s = pygame.transform.smoothscale(scoreboard_bg, screen.get_size())
                    screen.blit(bg_s, (0, 0))
                except Exception:
                    pass
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((8, 12, 30, 230))
            screen.blit(overlay, (0, 0))
            cx = screen.get_width()//2
            header = font_big.render("Scoreboard", True, (255, 215, 0))
            screen.blit(header, header.get_rect(center=(cx, 80)))
            song_name = os.path.splitext(os.path.basename(current_song_key))[0] if current_song_key else "Unknown"
            sub = font_small.render(f"{song_name}  —  Level {difficulty_level}", True, (200,200,200))
            screen.blit(sub, sub.get_rect(center=(cx, 120)))
            start_y = 170
            max_show = 10
            for i, e in enumerate(scoreboard_entries[:max_show]):
                rank = font_small.render(f"{i+1}", True, (240,200,50))
                name = font_medium.render(e.get('name','?'), True, (255,255,255))
                score_txt = font_medium.render(str(e.get('score',0)), True, (0,220,120))
                level_txt = font_small.render(f"L{e.get('level','?')}", True, (180,180,180))
                y = start_y + i * 56
                screen.blit(rank, rank.get_rect(midleft=(cx - 240, y+20)))
                screen.blit(name, name.get_rect(midleft=(cx - 200, y+18)))
                screen.blit(level_txt, level_txt.get_rect(midleft=(cx + 40, y+18)))
                screen.blit(score_txt, score_txt.get_rect(midright=(cx + 240, y+18)))
            footer = font_small.render("Press any key or click to return to menu", True, (170,170,170))
            screen.blit(footer, footer.get_rect(center=(cx, screen.get_height() - 60)))

        pygame.display.flip()
        clock.tick(60)
        continue

    # ---------- GAME UPDATE ----------
    # Determine active lanes based on input method and recompute layout
    current_lanes = LANES_CAMERA if (use_camera_controls and camera_available) else LANES_KEYBOARD
    # Resize hand hit timers if lane count changed
    if len(last_hand_hit_time) != current_lanes:
        last_hand_hit_time = [0.0] * current_lanes

    # Recompute lane layout for the active lane count
    lane_area_width = lane_width * current_lanes + LANE_SPACING * (current_lanes - 1)
    lane_left = (screen.get_width() - lane_area_width) // 2

    # Process camera hand input (optional) - Fruit Ninja style slicing for camera mode
    if use_camera_controls and camera_available and started and not paused:
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # apply inversion for preview and mapping if enabled
            if camera_inverted:
                frame_rgb_preview = cv2.flip(frame_rgb, 1)
            else:
                frame_rgb_preview = frame_rgb
            last_frame_preview = frame_rgb_preview.copy()
            results = mp_hands.process(frame_rgb)

            # keep previous hand positions to detect motion segments
            prev_hand_positions = list(last_hand_positions)
            last_hand_positions = []

            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Use index finger tip (landmark 8) for slice position
                    lm = hand_landmarks.landmark[8]
                    lm_x = 1.0 - lm.x if camera_inverted else lm.x
                    x_pixel = int(lm_x * screen.get_width())
                    y_pixel = int(lm.y * screen.get_height())
                    curr_pos = (x_pixel, y_pixel)
                    last_hand_positions.append(curr_pos)

                    # find a previous point for this hand (prefer same index, else nearest)
                    prev = None
                    if idx < len(prev_hand_positions):
                        prev = prev_hand_positions[idx]
                    else:
                        # find nearest previous point within reasonable distance
                        best = None
                        best_d = None
                        for p in prev_hand_positions:
                            dx = p[0] - curr_pos[0]
                            dy = p[1] - curr_pos[1]
                            d = dx*dx + dy*dy
                            if best is None or d < best_d:
                                best = p; best_d = d
                        if best is not None and best_d < (screen.get_width()*0.25)**2:
                            prev = best

                    # If we have a previous point with meaningful motion, check intersection
                    if prev is not None:
                        dx = curr_pos[0] - prev[0]
                        dy = curr_pos[1] - prev[1]
                        dist2 = dx*dx + dy*dy
                        MIN_SLICE_DIST = 20  # pixels - require movement to register a slice
                        if dist2 >= (MIN_SLICE_DIST * MIN_SLICE_DIST):
                            for block in list(active_blocks):
                                rect = block["rect"]
                                if _seg_intersects_rect(prev, curr_pos, rect):
                                    # spawn two pieces from block and remove block
                                    bx, by = rect.x, rect.y
                                    bw, bh = rect.width, rect.height
                                    col = block.get("color", (255,255,255))
                                    # left piece
                                    lp = {"rect": pygame.Rect(bx, by, bw//2, bh//2),
                                          "vx": -200 + -50 * (dy/ (abs(dy)+0.001)), "vy": -200,
                                          "color": col, "life": 1.2}
                                    # right piece
                                    rp = {"rect": pygame.Rect(bx + bw//2, by, bw - bw//2, bh//2),
                                          "vx": 200 + 50 * (dy/ (abs(dy)+0.001)), "vy": -200,
                                          "color": col, "life": 1.2}
                                    active_pieces.append(lp)
                                    active_pieces.append(rp)
                                    try:
                                        active_blocks.remove(block)
                                    except Exception:
                                        pass
                                    score += 100 * score_multiplier
                                    streak += 1
                                    if streak >= 25:
                                        score_multiplier = 2
                                    if streak >= 50:
                                        score_multiplier = 3
                                    break
            else:
                last_hand_positions = []

    if started and not paused:
        elapsed = time.time() - start_time - pause_offset if start_time else 0
        music_started, missed = game_logic.update_game(elapsed, notes, active_blocks,
                   BLOCK_COLORS, current_color_idx,
                   lane_left, lane_width, LANE_SPACING,
                   MOEILIJKHEID, hit_y, music_started,
                   lanes=current_lanes, pixels_per_second=PIXELS_PER_SECOND)
        # reset streak and trigger error flash on any missed notes removed by the logic
        if missed and missed > 0:
            streak = 0
            error_flash = 15
            score_multiplier = 1

    # ---------- DRAW GAME ----------
    # Pass only the active lane labels (camera mode shows fewer lanes)
    active_labels = LANE_LABELS[:current_lanes]
    # compute elapsed for HUD/progress bar (even when paused we show progress)
    elapsed_for_draw = time.time() - start_time - pause_offset if start_time else 0
    game_draw.render_game(screen, background, BLOCK_COLORS, active_blocks,
                          active_labels, lane_left, lane_width, LANE_SPACING,
                          hit_y, font_small, font_big, pause_button_selected,
                          paused, started, score, streak, error_flash,
                          use_camera=use_camera_controls and camera_available,
                          hand_positions=last_hand_positions,
                          hand_hit_times=last_hand_hit_time,
                          hand_hit_cooldown=hand_hit_cooldown,
                          preview_frame=last_frame_preview,
                          active_pieces=active_pieces,
                          elapsed=elapsed_for_draw, song_length=current_song_length,
                          score_multiplier=score_multiplier)

    # Additional robustness: if the progress fraction reaches 100% (visual),
    # start the same 5s timer to show the scoreboard. This ensures the
    # scoreboard appears even if notes/blocks logic didn't fully clear.
    try:
        if current_song_length and current_song_length > 0 and not show_scoreboard:
            frac = elapsed_for_draw / current_song_length
            if frac >= 0.999:
                if bar_full_at is None:
                    bar_full_at = time.time()
                    print(f"[DEBUG] bar_full_at set from progress fraction at {bar_full_at:.3f}, frac={frac:.3f}", flush=True)
    except Exception:
        pass

    # Centralized finalization: if bar_full_at was set (by any branch) and 5s passed,
    # commit score and display scoreboard. This guarantees the overlay appears.
    try:
        if bar_full_at is not None and not show_scoreboard:
            if time.time() - bar_full_at >= 5.0:
                print(f"[DEBUG] 5s passed since bar_full_at ({bar_full_at:.3f}); finalizing scoreboard.", flush=True)
                if current_song_key:
                    scoreboard_entries = save_score_entry(current_song_key, player_name or "Player", score, difficulty_level, scores_file)
                else:
                    scoreboard_entries = []
                show_scoreboard = True
                music_started = False
                started = False
                end_of_song = True
                bar_full_at = None
                print(f"[DEBUG] show_scoreboard=True (central), end_of_song={end_of_song}", flush=True)
    except Exception:
        pass

    # If settings opened from pause, render the settings overlay on top of the game
    if show_settings and not in_menu:
        menu.render_settings_overlay(screen, show_settings, difficulty_level,
                                    current_color_idx, BLOCK_COLORS,
                                    font_small, font_medium, font_big)

    # If the 5s timer is running (bar_full_at set) but the scoreboard hasn't appeared yet,
    # draw a fade so the player sees the background dim before the scoreboard appears.
    if bar_full_at is not None and not show_scoreboard:
        try:
            elapsed_since_full = max(0.0, time.time() - bar_full_at)
            t = min(1.0, elapsed_since_full / 5.0)
            alpha = int(180 * t)  # fade-in alpha over 5 seconds
            fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fade.fill((0, 0, 0, alpha))
            screen.blit(fade, (0, 0))
            # show small countdown text
            remaining = max(0, 5 - int(elapsed_since_full))
            info = font_small.render(f"Scoreboard in {remaining}s...", True, (220,220,220))
            screen.blit(info, info.get_rect(center=(screen.get_width()//2, screen.get_height() - 120)))
        except Exception:
            pass

    # Keep decrementing error_flash locally (render_game doesn't mutate it)
    if error_flash > 0:
        error_flash -= 1

    # Update piece physics (simple gravity and lifetime)
    if active_pieces:
        dt = clock.get_time() / 1000.0
        gravity = 800
        for p in list(active_pieces):
            p["vy"] += gravity * dt
            p["rect"].x += int(p["vx"] * dt)
            p["rect"].y += int(p["vy"] * dt)
            p["life"] -= dt
            # fade out and remove when life expired or off-screen
            if p["life"] <= 0 or p["rect"].y > screen.get_height() + 200:
                try:
                    active_pieces.remove(p)
                except Exception:
                    pass

    # If scoreboard overlay is active during gameplay, render it on top before flipping
    if show_scoreboard:
        # If this scoreboard is shown as end-of-song overlay and a background image
        # is available, draw it behind the translucent overlay for a nicer look.
        if end_of_song and scoreboard_bg is not None:
            try:
                bg_s = pygame.transform.smoothscale(scoreboard_bg, screen.get_size())
                screen.blit(bg_s, (0, 0))
            except Exception:
                pass
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 12, 30, 230))
        screen.blit(overlay, (0, 0))
        cx = screen.get_width()//2
        header = font_big.render("Scoreboard", True, (255, 215, 0))
        screen.blit(header, header.get_rect(center=(cx, 80)))
        song_name = os.path.splitext(os.path.basename(current_song_key))[0] if current_song_key else "Unknown"
        sub = font_small.render(f"{song_name}  —  Level {difficulty_level}", True, (200,200,200))
        screen.blit(sub, sub.get_rect(center=(cx, 120)))
        start_y = 170
        max_show = 10
        for i, e in enumerate(scoreboard_entries[:max_show]):
            rank = font_small.render(f"{i+1}", True, (240,200,50))
            name = font_medium.render(e.get('name','?'), True, (255,255,255))
            score_txt = font_medium.render(str(e.get('score',0)), True, (0,220,120))
            level_txt = font_small.render(f"L{e.get('level','?')}", True, (180,180,180))
            y = start_y + i * 56
            screen.blit(rank, rank.get_rect(midleft=(cx - 240, y+20)))
            screen.blit(name, name.get_rect(midleft=(cx - 200, y+18)))
            screen.blit(level_txt, level_txt.get_rect(midleft=(cx + 40, y+18)))
            screen.blit(score_txt, score_txt.get_rect(midright=(cx + 240, y+18)))
        # If this is the end-of-song overlay, show Replay and Back buttons
        if end_of_song and not in_menu:
            bw, bh = 260, 64
            spacing = 24
            left_x = cx - bw - spacing//2
            right_x = cx + spacing//2
            y = screen.get_height() - 140
            replay_rect = pygame.Rect(left_x, y, bw, bh)
            menu_rect = pygame.Rect(right_x, y, bw, bh)
            pygame.draw.rect(screen, (40,40,40), replay_rect, border_radius=8)
            pygame.draw.rect(screen, (40,40,40), menu_rect, border_radius=8)
            rtxt = font_medium.render("Replay", True, (255,255,255))
            mtxt = font_medium.render("Back to Menu", True, (255,255,255))
            screen.blit(rtxt, rtxt.get_rect(center=replay_rect.center))
            screen.blit(mtxt, mtxt.get_rect(center=menu_rect.center))
        else:
            footer = font_small.render("Press any key or click to return to menu", True, (170,170,170))
            screen.blit(footer, footer.get_rect(center=(cx, screen.get_height() - 60)))

    pygame.display.flip()
    clock.tick(60)

    # Robust end-of-song detection and scheduled playback
    try:
        # Start scheduled playback at the visual lead time
        if music_play_scheduled and not music_started and (music_play_time is not None) and time.time() >= music_play_time:
            try:
                pygame.mixer.music.play()
            except Exception:
                pass
            music_started = True
            music_play_scheduled = False

        # If music has started, detect end via mixer or elapsed vs known song length
        if music_started and not show_scoreboard:
            elapsed_check = 0.0
            if start_time:
                elapsed_check = time.time() - start_time - pause_offset

            mixer_stopped = False
            try:
                mixer_stopped = not pygame.mixer.music.get_busy()
            except Exception:
                mixer_stopped = False
            # Only finish the song if the music stopped (or the elapsed >= length) AND all notes have spawned
            all_spawned = all(n.get("spawned") for n in notes) if notes else True
            # If the track finished (mixer stopped or elapsed >= song length) and the scene is clear,
            # start a 5s timer from the moment the progress bar reaches 100% before showing scoreboard.
            if (mixer_stopped or (current_song_length and elapsed_check >= (current_song_length - 0.05))) and all_spawned and not active_blocks and not active_pieces:
                if bar_full_at is None:
                    bar_full_at = time.time()
                    print(f"[DEBUG] bar_full_at set from audio branch at {bar_full_at:.3f}, elapsed_check={elapsed_check:.3f}, mixer_stopped={mixer_stopped}")
                # after 5 seconds, commit score and show scoreboard
                if time.time() - bar_full_at >= 5.0:
                    print(f"[DEBUG] 5s elapsed since bar_full_at (audio branch). Saving score and showing scoreboard.")
                    if current_song_key:
                        scoreboard_entries = save_score_entry(current_song_key, player_name or "Player", score, difficulty_level, scores_file)
                    else:
                        scoreboard_entries = []
                    show_scoreboard = True
                    music_started = False
                    started = False
                    end_of_song = True
                    bar_full_at = None
                    print(f"[DEBUG] show_scoreboard=True, end_of_song={end_of_song}")
    except Exception:
        pass

    # ---------- END-OF-SONG CHECK ----------
    # When music started and no active blocks left and all notes spawned -> song finished
    if music_started and not paused and not started:
        pass
    if started and not paused:
        all_spawned = all(n.get("spawned") for n in notes) if notes else True
        if all_spawned and not active_blocks and not active_pieces:
            # Song finished visually — start the 5s post-bar timer if not already running
            if bar_full_at is None:
                bar_full_at = time.time()
                print(f"[DEBUG] bar_full_at set from visual branch at {bar_full_at:.3f}")
            if time.time() - bar_full_at >= 5.0:
                print(f"[DEBUG] 5s elapsed since bar_full_at (visual branch). Saving score and showing scoreboard.")
                music_started = False
                started = False
                if current_song_key:
                    scoreboard_entries = save_score_entry(current_song_key, player_name or "Player", score, difficulty_level, scores_file)
                else:
                    scoreboard_entries = []
                show_scoreboard = True
                end_of_song = True
                bar_full_at = None
                print(f"[DEBUG] show_scoreboard=True, end_of_song={end_of_song}")

    # If scoreboard overlay shown, wait for key to return to menu
    if show_scoreboard:
        # consume events specifically for the overlay; if this was an end-of-song overlay
        # offer Replay / Back buttons, otherwise return to menu on any input
        for ev in pygame.event.get():
            if end_of_song and not in_menu:
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    bw, bh = 260, 64
                    spacing = 24
                    cx = screen.get_width()//2
                    left_x = cx - bw - spacing//2
                    right_x = cx + spacing//2
                    y = screen.get_height() - 140
                    replay_rect = pygame.Rect(left_x, y, bw, bh)
                    menu_rect = pygame.Rect(right_x, y, bw, bh)
                    if replay_rect.collidepoint(mx, my):
                        # restart song immediately
                        active_blocks.clear()
                        active_pieces.clear()
                        score = 0
                        streak = 0
                        score_multiplier = 1
                        for n in notes:
                            if "spawned" in n: del n["spawned"]
                        # start playback with visual lead time
                        start_time = time.time()
                        pause_offset = 0
                        started = True
                        paused = False
                        block_center_offset = MOEILIJKHEID / 2
                        lead_time = (hit_y - block_center_offset) / PIXELS_PER_SECOND
                        music_play_time = start_time + lead_time
                        music_play_scheduled = True
                        music_started = False
                        show_scoreboard = False
                        end_of_song = False
                        bar_full_at = None
                        break
                    elif menu_rect.collidepoint(mx, my):
                        show_scoreboard = False
                        end_of_song = False
                        in_menu = True
                        background = None
                        # reset state
                        player_name = ""
                        current_song_key = None
                        active_blocks.clear()
                        active_pieces.clear()
                        notes = []
                        score = 0
                        music_started = False
                        started = False
                        bar_full_at = None
                        break
                elif ev.type == pygame.KEYDOWN:
                    # treat any key as 'back to menu'
                    show_scoreboard = False
                    end_of_song = False
                    in_menu = True
                    background = None
                    player_name = ""
                    current_song_key = None
                    active_blocks.clear()
                    active_pieces.clear()
                    notes = []
                    score = 0
                    music_started = False
                    started = False
                    break
            else:
                if ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                    show_scoreboard = False
                    end_of_song = False
                    in_menu = True
                    background = None
                    # reset state
                    player_name = ""
                    current_song_key = None
                    active_blocks.clear()
                    active_pieces.clear()
                    notes = []
                    score = 0
                    music_started = False
                    started = False
                    break

pygame.quit()
# Release camera resources if used
if 'cap' in globals() and cap is not None:
    try:
        cap.release()
    except Exception:
        pass
if 'mp_hands' in globals() and mp_hands is not None:
    try:
        mp_hands.close()
    except Exception:
        pass