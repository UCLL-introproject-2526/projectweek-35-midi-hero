import pygame
import time


def update_game(elapsed, 
                notes, 
                active_blocks, 
                BLOCK_COLORS, 
                current_color_idx,
                lane_left, 
                lane_width, 
                LANE_SPACING, 
                MOEILIJKHEID, 
                hit_y,
                music_started, 
                lanes=4, 
                pixels_per_second=300):

    # tijdgebonden noten ipv fps
    for n in notes:
        if n.get("spawned"):
            continue
        
        if n["time"] <= elapsed:
            lane = n["note"] % lanes
            lane_x = lane_left + lane * (lane_width + LANE_SPACING)
            y = max(0, (elapsed - n["time"]) * pixels_per_second)
            rect = pygame.Rect(lane_x + 10, int(y), lane_width - 20, MOEILIJKHEID)
            overlap = False

            for b in active_blocks:
                b_lane = int((b["rect"].centerx - lane_left) // (lane_width + LANE_SPACING))
                if b_lane == lane and abs(b["rect"].y - rect.y) < (MOEILIJKHEID * 1.5):
                    overlap = True
                    break

            if not overlap:
                active_blocks.append({"rect": rect, "hit": False, "hit_time": pygame.time.get_ticks(), "color": BLOCK_COLORS[current_color_idx], "time": n["time"]})
                n["spawned"] = True

    # update blok posities
    for block in active_blocks:
        block_time = block.get("time", 0)
        block["rect"].y = int(max(0, (elapsed - block_time) * pixels_per_second))

    # noten in lijst registeren (ivm streak etc)
    # werkt niet :(
    miss_threshold = hit_y + int(MOEILIJKHEID * 1.5)
    kept = []
    missed_count = 0

    import math

    for block in active_blocks:
        if block.get("hit"):
            kept.append(block)

        else:
            if block["rect"].top <= miss_threshold:
                kept.append(block)

            else:
                missed_count += 1

    # wat doet dit uberhaupt bruh
    old_len = len(active_blocks)
    active_blocks[:] = kept


    return music_started, missed_count
