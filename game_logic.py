import pygame
import time
import threading


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


    #for block in active_blocks:
    #    if block.get("hit"):
    #        kept.append(block)
#
    #    else:
    #        if block["rect"].top <= miss_threshold:
    #            kept.append(block)
#
    #        else:
    #            missed_count += 1
    #            if block in active_blocks:
    #                threading.Timer(1, active_blocks.remove, args=[block]).start()
    #            



    current_time = time.time()
    kept = []

    for block in active_blocks:
        # --- 1. Handle blocks that are already "dying" (missed previously) ---
        if block.get("is_missed"):
            # If 1 second has passed since it was missed, let it go (don't append to kept)
            if current_time - block["miss_time"] > 1.0:
                continue 
            
            # Otherwise, keep it alive so it renders
            kept.append(block)
            continue

        # --- 2. Handle active blocks ---
        if block.get("hit"):
            kept.append(block)

        else:
            # Check if it just crossed the line
            if block["rect"].top <= miss_threshold:
                kept.append(block)

            else:
                # It just missed!
                missed_count += 1

                # Mark it, timestamp it, and KEEP it so it stays visible
                block["is_missed"] = True
                block["miss_time"] = current_time
                kept.append(block)

    # Update the main list
    active_blocks = kept
    
    # wat doet dit uberhaupt bruh
    old_len = len(active_blocks)
    active_blocks[:] = kept


    return music_started, missed_count
