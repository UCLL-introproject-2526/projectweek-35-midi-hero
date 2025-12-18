import pygame
import time
from draw_utils import draw_gear


def render_menu(screen, songs, selected_song, show_settings, difficulty_level,
                current_color_idx, BLOCK_COLORS, font_small, font_medium,
                font_big, gear_rect, use_camera=False, camera_available=False,
                camera_inverted=False, background_image=None, title_image=None, currently_playing_song=None):
    # base background
    screen.fill((20, 20, 30))
    # optional decorative background image (e.g. cat.gif) drawn with partial alpha
    if background_image is not None:
        try:
            mw, mh = screen.get_size()
            # If background_image is an animation dict (created in main), animate frames
            if isinstance(background_image, dict) and 'frames' in background_image:
                frames = background_image['frames']
                durations = background_image.get('durations', [0.1] * len(frames))
                idx = background_image.get('index', 0)
                last = background_image.get('last_time', time.time())
                now = time.time()
                # advance frame if its duration passed
                try:
                    if now - last >= durations[idx]:
                        idx = (idx + 1) % len(frames)
                        background_image['index'] = idx
                        background_image['last_time'] = now
                except Exception:
                    background_image['index'] = 0
                    background_image['last_time'] = now
                bg_s = frames[background_image['index']]
                bw, bh = bg_s.get_size()
            else:
                # single surface
                bg_s = background_image
                bw, bh = bg_s.get_size()

            max_w = int(mw * 0.3)
            scale = 1.0
            if bw > max_w:
                scale = max_w / bw
            new_w = int(bw * scale)
            new_h = int(bh * scale)
            bg_s = pygame.transform.smoothscale(bg_s, (new_w, new_h))
            # draw at bottom-left with slight transparency
            temp = bg_s.copy()
            try:
                temp.set_alpha(160)
            except Exception:
                pass
            screen.blit(temp, (20, screen.get_height() - new_h - 20))
        except Exception:
            pass

    # Title
    if title_image is not None:
        try:
            # Scale title image to fit nicely at top (pixel art - use scale not smoothscale)
            title_w, title_h = title_image.get_size()
            max_width = int(screen.get_width() * 0.5)
            scale = max_width / title_w
            new_w = int(title_w * scale)
            new_h = int(title_h * scale)
            title_img_scaled = pygame.transform.scale(title_image, (new_w, new_h))
            screen.blit(title_img_scaled, title_img_scaled.get_rect(center=(screen.get_width() // 2, 100)))
        except Exception:
            # Fallback to text if image fails
            title = font_big.render("MIDI Hero", True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 100)))
    else:
        # Text fallback
        title = font_big.render("MIDI Hero", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 100)))

    # settings icoon
    mouse_pos = pygame.mouse.get_pos()
    gear_color = (200, 200, 200)
    if gear_rect.collidepoint(mouse_pos) and not show_settings:
        gear_color = (255, 255, 0)
    draw_gear(screen, gear_rect, gear_color)

    # Song List
    start_y = 240
    if songs:
        # Calculate bounds for all songs
        song_left = screen.get_width() // 2 - 200
        song_right = screen.get_width() // 2 + 200
        song_top = start_y - 25
        song_bottom = start_y + len(songs) * 45 + 25
        
        # Draw border around all songs
        song_list_rect = pygame.Rect(song_left, song_top, song_right - song_left, song_bottom - song_top)
        pygame.draw.rect(screen, (72, 210, 203), song_list_rect, 3, border_radius=8)
        
        for i, song in enumerate(songs):
            color = (255, 176, 31) if i == selected_song else (150, 150, 150)
            text = font_small.render(song["name"], True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, start_y + i * 45))
            
            screen.blit(text, rect)
            
            if i == selected_song:
                pygame.draw.polygon(screen, (255, 176, 31), [
                    (rect.left - 20, rect.centery),
                    (rect.left - 30, rect.top),
                    (rect.left - 30, rect.bottom)
                ])
        # scoreboard preview per song
        try:
            import json, os
            scores = {}

            if os.path.exists('scores.json'):
                with open('scores.json', 'r', encoding='utf-8') as f:
                    scores = json.load(f)

            sel = songs[selected_song]
            key = sel.get('name')
            entries = scores.get(key, [])
            
            panel_w = 420
            panel_h = 300
            panel_x = screen.get_width() - panel_w - 80
            panel_y = 200
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(screen, (40, 50, 70), panel_rect, border_radius=8)
            pygame.draw.rect(screen, (72, 210, 203), panel_rect, 2, border_radius=8)
            hdr = font_medium.render('Top Scores', True, (255, 176, 31))
            screen.blit(hdr, hdr.get_rect(midtop=(panel_rect.centerx, panel_rect.top + 12)))
            y = panel_rect.top + 56

            for i, e in enumerate(entries[:6]):
                rank = font_small.render(str(i+1), True, (255, 176, 31))
                name = font_small.render(e.get('name','?'), True, (230,230,230))
                sc = font_small.render(str(e.get('score',0)), True, (72, 210, 203))
                screen.blit(rank, rank.get_rect(topleft=(panel_rect.left + 12, y)))
                screen.blit(name, name.get_rect(topleft=(panel_rect.left + 48, y)))
                screen.blit(sc, sc.get_rect(topright=(panel_rect.right - 12, y)))
                y += 42

            if not entries:
                hint = font_small.render('No scores yet for this song', True, (160,160,160))
                screen.blit(hint, hint.get_rect(center=(panel_rect.centerx, panel_rect.centery)))

        except Exception:
            pass
    else:
        warn = font_small.render("No songs found in 'songs' folder!", True, (255, 100, 100))
        screen.blit(warn, warn.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))

    # settings overlay
    if show_settings:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        cx, cy = screen.get_width() // 2, screen.get_height() // 2
        box_width, box_height = 600, 550
        box_rect = pygame.Rect(cx - box_width//2, cy - box_height//2, box_width, box_height)
        pygame.draw.rect(screen, (40, 50, 70), box_rect, border_radius=15)
        pygame.draw.rect(screen, (72, 210, 203), box_rect, 3, border_radius=15)

        # settings opties
        s_title = font_medium.render("SETTINGS", True, (255, 255, 255))
        screen.blit(s_title, s_title.get_rect(center=(cx, cy - 180)))

        # moeiljkheid selector
        d_label = font_small.render("DIFFICULTY", True, (180, 180, 180))
        screen.blit(d_label, d_label.get_rect(center=(cx, cy - 130)))
        diff_left = pygame.Rect(cx - 150, cy - 100, 40, 40)
        diff_right = pygame.Rect(cx + 110, cy - 100, 40, 40)
        pygame.draw.rect(screen, (70, 70, 80), diff_left, border_radius=5)
        pygame.draw.rect(screen, (70, 70, 80), diff_right, border_radius=5)
        screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=diff_left.center))
        screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=diff_right.center))
        d_val = font_medium.render(f"Level {difficulty_level}", True, (255, 176, 31))
        screen.blit(d_val, d_val.get_rect(center=(cx, cy - 50)))

        # kleur selector
        c_label = font_small.render("BLOCK COLOR", True, (180, 180, 180))
        screen.blit(c_label, c_label.get_rect(center=(cx, cy + 10)))
        col_left = pygame.Rect(cx - 150, cy + 40, 40, 40)
        col_right = pygame.Rect(cx + 110, cy + 40, 40, 40)
        pygame.draw.rect(screen, (70, 70, 80), col_left, border_radius=5)
        pygame.draw.rect(screen, (70, 70, 80), col_right, border_radius=5)
        screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=col_left.center))
        screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=col_right.center))

        preview_rect = pygame.Rect(cx - 40, cy + 30, 80, 60)
        pygame.draw.rect(screen, BLOCK_COLORS[current_color_idx], preview_rect, border_radius=10)
        pygame.draw.rect(screen, (72, 210, 203), preview_rect, 2, border_radius=10)

        # input method selector
        im_label = font_small.render("INPUT METHOD", True, (180, 180, 180))
        screen.blit(im_label, im_label.get_rect(center=(cx, cy + 110)))
        im_left = pygame.Rect(cx - 150, cy + 140, 40, 40)
        im_right = pygame.Rect(cx + 110, cy + 140, 40, 40)
        pygame.draw.rect(screen, (70, 70, 80), im_left, border_radius=5)
        pygame.draw.rect(screen, (70, 70, 80), im_right, border_radius=5)
        screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=im_left.center))
        screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=im_right.center))
        im_text = "Camera" if use_camera else "Keyboard"

        if use_camera and not camera_available:
            im_text = "Camera (Unavailable)"

        im_val = font_medium.render(im_text, True, (255, 215, 0))
        screen.blit(im_val, im_val.get_rect(center=(cx, cy + 160)))

        # invert camera
        inv_label = font_small.render("INVERT CAMERA", True, (180, 180, 180))
        screen.blit(inv_label, inv_label.get_rect(center=(cx, cy + 190)))
        inv_rect = pygame.Rect(cx - 60, cy + 210, 120, 36)
        inv_color = (40, 50, 70)
        pygame.draw.rect(screen, inv_color, inv_rect, border_radius=6)
        inv_text = "ON" if camera_inverted else "OFF"
        inv_col = (72, 210, 203) if camera_inverted else (160, 160, 160)
        inv_val = font_small.render(inv_text, True, (255,255,255))
        pygame.draw.rect(screen, inv_col, (inv_rect.left + 6, inv_rect.top + 6, inv_rect.width - 12, inv_rect.height - 12), border_radius=4)
        screen.blit(inv_val, inv_val.get_rect(center=inv_rect.center))

        close_rect = pygame.Rect(cx - 100, cy + 270, 200, 50)
        c_color = (255, 176, 31) if close_rect.collidepoint(mouse_pos) else (255, 170, 20)
        pygame.draw.rect(screen, c_color, close_rect, border_radius=10)
        close_txt = font_small.render("SAVE & CLOSE", True, (255, 255, 255))
        screen.blit(close_txt, close_txt.get_rect(center=close_rect.center))


def render_settings_overlay(screen, 
                            show_settings, 
                            difficulty_level,
                            current_color_idx, 
                            BLOCK_COLORS,
                            font_small, 
                            font_medium, 
                            font_big):
    
    if not show_settings:
        return
    
    mouse_pos = pygame.mouse.get_pos()
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_width() // 2, screen.get_height() // 2
    box_width, box_height = 600, 550
    box_rect = pygame.Rect(cx - box_width//2, cy - box_height//2, box_width, box_height)
    pygame.draw.rect(screen, (40, 50, 70), box_rect, border_radius=15)
    pygame.draw.rect(screen, (72, 210, 203), box_rect, 3, border_radius=15)

    # settings opties
    s_title = font_medium.render("SETTINGS", True, (255, 255, 255))
    screen.blit(s_title, s_title.get_rect(center=(cx, cy - 180)))

    # moeilijkheid selector
    d_label = font_small.render("DIFFICULTY", True, (180, 180, 180))
    screen.blit(d_label, d_label.get_rect(center=(cx, cy - 130)))
    diff_left = pygame.Rect(cx - 150, cy - 100, 40, 40)
    diff_right = pygame.Rect(cx + 110, cy - 100, 40, 40)
    pygame.draw.rect(screen, (70, 70, 80), diff_left, border_radius=5)
    pygame.draw.rect(screen, (70, 70, 80), diff_right, border_radius=5)
    screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=diff_left.center))
    screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=diff_right.center))
    d_val = font_medium.render(f"Level {difficulty_level}", True, (255, 176, 31))
    screen.blit(d_val, d_val.get_rect(center=(cx, cy - 50)))

    # kleur selector
    c_label = font_small.render("BLOCK COLOR", True, (180, 180, 180))
    screen.blit(c_label, c_label.get_rect(center=(cx, cy + 10)))
    col_left = pygame.Rect(cx - 150, cy + 40, 40, 40)
    col_right = pygame.Rect(cx + 110, cy + 40, 40, 40)
    pygame.draw.rect(screen, (70, 70, 80), col_left, border_radius=5)
    pygame.draw.rect(screen, (70, 70, 80), col_right, border_radius=5)
    screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=col_left.center))
    screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=col_right.center))

    preview_rect = pygame.Rect(cx - 40, cy + 30, 80, 60)
    pygame.draw.rect(screen, BLOCK_COLORS[current_color_idx], preview_rect, border_radius=10)
    pygame.draw.rect(screen, (72, 210, 203), preview_rect, 2, border_radius=10)

    close_rect = pygame.Rect(cx - 100, cy + 200, 200, 50)
    c_color = (255, 176, 31) if close_rect.collidepoint(mouse_pos) else (255, 170, 20)
    pygame.draw.rect(screen, c_color, close_rect, border_radius=10)
    close_txt = font_small.render("SAVE & CLOSE", True, (255, 255, 255))
    screen.blit(close_txt, close_txt.get_rect(center=close_rect.center))
