import pygame
import time
import math


def render_game(screen, 
                background, 
                BLOCK_COLORS, 
                active_blocks, 
                LANE_LABELS,
                lane_left, 
                lane_width, 
                LANE_SPACING, 
                hit_y, 
                font_small,
                font_big, 
                pause_button_selected, 
                paused, 
                started, 
                score,
                streak, 
                error_flash, 
                use_camera=False, 
                hand_positions=None,
                hand_hit_times=None, 
                hand_hit_cooldown=0.35, 
                preview_frame=None,
                active_pieces=None, 
                elapsed=0.0, 
                song_length=0.0, 
                score_multiplier=1):
    
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((0,0,0))

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    # lanes
    for i in range(len(LANE_LABELS)):
        lx = lane_left + i * (lane_width + LANE_SPACING)
        lane_rect = pygame.Rect(lx, 0, lane_width, screen.get_height())
        strip = pygame.Surface((lane_width, screen.get_height()), pygame.SRCALPHA)
        strip.fill((30, 30, 30, 40))
        screen.blit(strip, (lx, 0))
        pygame.draw.rect(screen, (200, 200, 200), lane_rect, 4)

    # hit lijn (voor keyboard controls)
    if not use_camera:
        pygame.draw.line(screen, (255, 0, 0), (0, hit_y), (screen.get_width(), hit_y), 5)

    # lane labels
    for i, label in enumerate(LANE_LABELS):
        lane_cx = lane_left + i * (lane_width + LANE_SPACING) + lane_width // 2
        t = font_small.render(label, True, (255, 255, 255))
        r = t.get_rect(center=(lane_cx, hit_y + 40))
        screen.blit(t, r)

    # score
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 10))

    # progress bar
    try:
        if song_length and song_length > 0:
            bar_x = 20
            bar_w = 18
            bar_y = 60
            bar_h = screen.get_height() - 120
            pygame.draw.rect(screen, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
            frac = max(0.0, min(1.0, elapsed / song_length))
            fill_h = int(bar_h * frac)

            if fill_h > 0:
                pygame.draw.rect(screen, (0, 200, 200), (bar_x, bar_y, bar_w, fill_h), border_radius=6)

            # time text
            pct = int(frac * 100)
            t = font_small.render(f"{pct}%", True, (200,200,200))
            screen.blit(t, (bar_x + bar_w + 8, bar_y + bar_h - 16))

    except Exception:
        pass

    # streak
    streak_text = font_small.render(f"Streak: {streak}", True, (255, 215, 0))
    sx = screen.get_width() - 10 - streak_text.get_width()
    screen.blit(streak_text, (sx, 10))
    # score multiplier
    if score_multiplier and score_multiplier > 1:
        try:
            bx = sx - 60
            by = 8
            pygame.draw.circle(screen, (0, 180, 120), (bx+18, by+18), 18)
            bx_txt = font_small.render(f"{int(score_multiplier)}x", True, (20,20,20))
            screen.blit(bx_txt, bx_txt.get_rect(center=(bx+18, by+18)))

        except Exception:
            pass

    current_time = pygame.time.get_ticks()

    if started and not paused:
        for block in active_blocks:
            draw_rect = block["rect"]
            pygame.draw.rect(screen, block["color"], block["rect"], border_radius=10)
            if block.get("hit"):
                elapsed = current_time - block["hit_time"]
                duration = 300  # Animation lasts 300 milliseconds
        
                if elapsed < duration:
                    # Create a 'Pop' effect using a sine wave (0 to PI)
                    # This makes it grow and then shrink back to normal size
                    # math.sin(0) = 0, math.sin(pi) = 0, math.sin(pi/2) = 1 (peak)
                    timer_ratio = (elapsed / duration) * math.pi
                    pulse_size = math.sin(timer_ratio) * 20  # Grows up to 20 pixels
                    draw_rect = block["rect"].inflate(pulse_size, pulse_size)
                else:
                # Optional: Remove block or keep it green but stop pulsing
                    pass
                pygame.draw.rect(screen, block["color"], draw_rect, border_radius=10)
            

    else:
        for block in active_blocks:
            pygame.draw.rect(screen, block["color"], block["rect"], border_radius=10)


    if active_pieces:
        for p in list(active_pieces):
            try:
                pygame.draw.rect(screen, p.get("color", (255,255,255)), p["rect"], border_radius=6)
            except Exception:
                pass

    if not started:
        msg = font_big.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(msg, msg.get_rect(center=screen.get_rect().center))

    if paused:
        fade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fade.fill((0, 0, 0, 180))
        screen.blit(fade, (0, 0))

        cx = screen.get_rect().centerx
        top_y = 80
        paused_text = font_big.render("PAUSED", True, (255, 255, 255))
        screen.blit(paused_text, paused_text.get_rect(center=(cx, top_y)))

        hint_y = top_y + 60
        hint = font_small.render("Press ESC to resume", True, (200, 200, 200))
        screen.blit(hint, hint.get_rect(center=(cx, hint_y)))

        # settings knoppekes
        bw, bh, spacing = 360, 56, 20
        total_h = bh * 3 + spacing * 2
        top_y = screen.get_height() // 2 - total_h // 2
        bx = cx - bw // 2
        back_rect = pygame.Rect(bx, top_y, bw, bh)
        settings_rect = pygame.Rect(bx, top_y + (bh + spacing), bw, bh)
        exit_rect = pygame.Rect(bx, top_y + 2 * (bh + spacing), bw, bh)

        # back to main menu
        back_color = (90, 90, 90) if pause_button_selected != 0 else (120, 120, 60)
        pygame.draw.rect(screen, back_color, back_rect, border_radius=8)
        back_txt = font_small.render("Main Menu", True, (255, 255, 255))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))
        
        if pause_button_selected == 0:
            outline_rect = back_rect.inflate(10, 10)
            pygame.draw.rect(screen, (255, 215, 0), outline_rect, 4, border_radius=12)

        # settings
        settings_color = (80, 100, 140) if pause_button_selected == 1 else (90, 90, 90)
        pygame.draw.rect(screen, settings_color, settings_rect, border_radius=8)
        set_txt = font_small.render("Settings", True, (255, 255, 255))
        screen.blit(set_txt, set_txt.get_rect(center=settings_rect.center))

        if pause_button_selected == 1:
            outline_rect = settings_rect.inflate(10, 10)
            pygame.draw.rect(screen, (255, 215, 0), outline_rect, 4, border_radius=12)

        # exit game
        exit_color = (180, 70, 70) if pause_button_selected != 2 else (220, 90, 90)
        pygame.draw.rect(screen, exit_color, exit_rect, border_radius=8)
        exit_text = font_small.render("Exit Game", True, (255, 255, 255))
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))

        if pause_button_selected == 2:
            outline_rect = exit_rect.inflate(10, 10)
            pygame.draw.rect(screen, (255, 215, 0), outline_rect, 4, border_radius=12)

    if error_flash > 0:
        border = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        border.fill((255, 0, 0, 50))
        screen.blit(border, (0, 0))


    # scoreboard overlay registration
    try:
        if kwargs := {}:
            pass
    except Exception:
        pass

    # camera overlay
    if use_camera and not paused:
        now_t = time.time()

        # camera preview
        if preview_frame is not None:
            try:
                ph, pw = preview_frame.shape[:2]
                thumb_w, thumb_h = 160, 120
                surf = pygame.image.frombuffer(preview_frame.tobytes(), (pw, ph), 'RGB')
                surf = pygame.transform.scale(surf, (thumb_w, thumb_h))
                pygame.draw.rect(screen, (30,30,30), (10, 40, thumb_w+4, thumb_h+4))
                screen.blit(surf, (12, 42))
                t = font_small.render("Camera Preview", True, (200,200,200))
                screen.blit(t, (12, 16))

            except Exception:
                pass


        # pointers waar handen zijn op camera
        if hand_positions:
            for (hx, hy) in hand_positions:
                pygame.draw.circle(screen, (255, 200, 0), (int(hx), int(hy)), 14, 3)
                pygame.draw.circle(screen, (255, 200, 0, 80), (int(hx), int(hy)), 6)

        hint = font_small.render("Camera: slice the blocks with your index finger", True, (200, 200, 200))
        screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, hit_y - 80)))
