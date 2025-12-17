import pygame
from draw_utils import draw_gear


def render_menu(screen, songs, selected_song, show_settings, difficulty_level,
                current_color_idx, BLOCK_COLORS, font_small, font_medium,
                font_big, gear_rect, use_camera=False, camera_available=False,
                camera_inverted=False):
    screen.fill((20, 20, 30))

    # Title
    title = font_big.render("MIDI Hero", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 80)))

    # Gear Icon
    mouse_pos = pygame.mouse.get_pos()
    gear_color = (200, 200, 200)
    if gear_rect.collidepoint(mouse_pos) and not show_settings:
        gear_color = (255, 255, 0)
    draw_gear(screen, gear_rect, gear_color)

    # Song List
    start_y = 180
    if songs:
        for i, song in enumerate(songs):
            color = (255, 215, 0) if i == selected_song else (150, 150, 150)
            text = font_small.render(song["name"], True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, start_y + i * 45))
            screen.blit(text, rect)
            
            if i == selected_song:
                pygame.draw.polygon(screen, (255, 215, 0), [
                    (rect.left - 20, rect.centery),
                    (rect.left - 30, rect.top),
                    (rect.left - 30, rect.bottom)
                ])
    else:
        warn = font_small.render("No songs found in 'songs' folder!", True, (255, 100, 100))
        screen.blit(warn, warn.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))

    # Settings Overlay
    if show_settings:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        cx, cy = screen.get_width() // 2, screen.get_height() // 2
        box_width, box_height = 550, 580
        box_rect = pygame.Rect(cx - box_width//2, cy - box_height//2, box_width, box_height)
        pygame.draw.rect(screen, (40, 40, 50), box_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 120), box_rect, 3, border_radius=15)

        s_title = font_medium.render("SETTINGS", True, (255, 255, 255))
        screen.blit(s_title, s_title.get_rect(center=(cx, cy - 240)))

        # DIFFICULTY section
        d_label = font_small.render("DIFFICULTY", True, (180, 180, 180))
        screen.blit(d_label, d_label.get_rect(center=(cx, cy - 185)))
        diff_left = pygame.Rect(cx - 150, cy - 155, 40, 40)
        diff_right = pygame.Rect(cx + 110, cy - 155, 40, 40)
        pygame.draw.rect(screen, (70, 70, 80), diff_left, border_radius=5)
        pygame.draw.rect(screen, (70, 70, 80), diff_right, border_radius=5)
        screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=diff_left.center))
        screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=diff_right.center))
        d_val = font_medium.render(f"Level {difficulty_level}", True, (255, 215, 0))
        screen.blit(d_val, d_val.get_rect(center=(cx, cy - 115)))

        # BLOCK COLOR section
        c_label = font_small.render("BLOCK COLOR", True, (180, 180, 180))
        screen.blit(c_label, c_label.get_rect(center=(cx, cy - 70)))
        col_left = pygame.Rect(cx - 150, cy - 40, 40, 40)
        col_right = pygame.Rect(cx + 110, cy - 40, 40, 40)
        pygame.draw.rect(screen, (70, 70, 80), col_left, border_radius=5)
        pygame.draw.rect(screen, (70, 70, 80), col_right, border_radius=5)
        screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=col_left.center))
        screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=col_right.center))

        preview_rect = pygame.Rect(cx - 40, cy - 50, 80, 60)
        pygame.draw.rect(screen, BLOCK_COLORS[current_color_idx], preview_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), preview_rect, 2, border_radius=10)

        # INPUT METHOD section
        im_label = font_small.render("INPUT METHOD", True, (180, 180, 180))
        screen.blit(im_label, im_label.get_rect(center=(cx, cy + 20)))
        im_left = pygame.Rect(cx - 150, cy + 50, 40, 40)
        im_right = pygame.Rect(cx + 110, cy + 50, 40, 40)
        pygame.draw.rect(screen, (70, 70, 80), im_left, border_radius=5)
        pygame.draw.rect(screen, (70, 70, 80), im_right, border_radius=5)
        screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=im_left.center))
        screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=im_right.center))
        im_text = "Camera" if use_camera else "Keyboard"
        if use_camera and not camera_available:
            im_text = "Camera (Unavailable)"
        im_val = font_medium.render(im_text, True, (255, 215, 0))
        screen.blit(im_val, im_val.get_rect(center=(cx, cy + 90)))

        # INVERT CAMERA section
        inv_label = font_small.render("INVERT CAMERA", True, (180, 180, 180))
        screen.blit(inv_label, inv_label.get_rect(center=(cx, cy + 130)))
        inv_rect = pygame.Rect(cx - 60, cy + 160, 120, 36)
        inv_color = (70, 70, 80)
        pygame.draw.rect(screen, inv_color, inv_rect, border_radius=6)
        inv_text = "ON" if camera_inverted else "OFF"
        inv_col = (0, 200, 0) if camera_inverted else (160, 160, 160)
        inv_val = font_small.render(inv_text, True, (255,255,255))
        pygame.draw.rect(screen, inv_col, (inv_rect.left + 6, inv_rect.top + 6, inv_rect.width - 12, inv_rect.height - 12), border_radius=4)
        screen.blit(inv_val, inv_val.get_rect(center=inv_rect.center))

        close_rect = pygame.Rect(cx - 100, cy + 230, 200, 50)
        c_color = (200, 50, 50) if close_rect.collidepoint(mouse_pos) else (150, 40, 40)
        pygame.draw.rect(screen, c_color, close_rect, border_radius=10)
        close_txt = font_small.render("SAVE & CLOSE", True, (255, 255, 255))
        screen.blit(close_txt, close_txt.get_rect(center=close_rect.center))


def render_settings_overlay(screen, show_settings, difficulty_level,
                           current_color_idx, BLOCK_COLORS,
                           font_small, font_medium, font_big):
    # Draw only the translucent settings overlay (does not clear the screen)
    if not show_settings:
        return
    mouse_pos = pygame.mouse.get_pos()
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    cx, cy = screen.get_width() // 2, screen.get_height() // 2
    box_width, box_height = 550, 380
    box_rect = pygame.Rect(cx - box_width//2, cy - box_height//2, box_width, box_height)
    pygame.draw.rect(screen, (40, 40, 50), box_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 100, 120), box_rect, 3, border_radius=15)

    s_title = font_medium.render("SETTINGS", True, (255, 255, 255))
    screen.blit(s_title, s_title.get_rect(center=(cx, cy - 160)))

    # DIFFICULTY section
    d_label = font_small.render("DIFFICULTY", True, (180, 180, 180))
    screen.blit(d_label, d_label.get_rect(center=(cx, cy - 110)))
    diff_left = pygame.Rect(cx - 150, cy - 80, 40, 40)
    diff_right = pygame.Rect(cx + 110, cy - 80, 40, 40)
    pygame.draw.rect(screen, (70, 70, 80), diff_left, border_radius=5)
    pygame.draw.rect(screen, (70, 70, 80), diff_right, border_radius=5)
    screen.blit(font_small.render("<", True, (255,255,255)), font_small.render("<", True, (255,255,255)).get_rect(center=diff_left.center))
    screen.blit(font_small.render(">", True, (255,255,255)), font_small.render(">", True, (255,255,255)).get_rect(center=diff_right.center))
    d_val = font_medium.render(f"Level {difficulty_level}", True, (255, 215, 0))
    screen.blit(d_val, d_val.get_rect(center=(cx, cy - 40)))

    # BLOCK COLOR section
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
    pygame.draw.rect(screen, (255, 255, 255), preview_rect, 2, border_radius=10)

    close_rect = pygame.Rect(cx - 100, cy + 120, 200, 50)
    c_color = (200, 50, 50) if close_rect.collidepoint(mouse_pos) else (150, 40, 40)
    pygame.draw.rect(screen, c_color, close_rect, border_radius=10)
    close_txt = font_small.render("SAVE & CLOSE", True, (255, 255, 255))
    screen.blit(close_txt, close_txt.get_rect(center=close_rect.center))