import pygame
import time


def update_game(elapsed, notes, active_blocks, BLOCK_COLORS, current_color_idx,
                lane_left, lane_width, LANE_SPACING, MOEILIJKHEID, hit_y,
                music_started, lanes=4, pixels_per_second=300,
                active_pieces=None):
    """Spawn notes whose time has come, move blocks, and start music.

    Mutates `notes` (marks spawned) and `active_blocks` in-place. Returns
    updated `music_started` boolean.
    """
    # Spawn notes and compute positions based on elapsed time so movement is
    # time-based and not tied to frame rate.
    for idx, n in enumerate(notes):
        if n.get("spawned"):
            continue
        # If the next note is in the future, we can stop early (notes are ordered)
        if n.get("time", 0) > elapsed:
            break
        if n["time"] <= elapsed:
            lane = n["note"] % lanes
            lane_x = lane_left + lane * (lane_width + LANE_SPACING)
            # position based on how long since the note's scheduled time
            y = max(0, (elapsed - n["time"]) * pixels_per_second)
            rect = pygame.Rect(lane_x + 10, int(y), lane_width - 20, MOEILIJKHEID)
            # simple overlap check using predicted y; also consider active pieces
            overlap = False
            for b in active_blocks:
                b_lane = int((b["rect"].centerx - lane_left) // (lane_width + LANE_SPACING))
                if b_lane == lane and abs(b["rect"].y - rect.y) < (MOEILIJKHEID * 1.5):
                    overlap = True
                    break
            if not overlap and active_pieces:
                for p in active_pieces:
                    try:
                        p_lane = int((p["rect"].centerx - lane_left) // (lane_width + LANE_SPACING))
                    except Exception:
                        continue
                    if p_lane == lane and abs(p["rect"].y - rect.y) < (MOEILIJKHEID * 1.5):
                        overlap = True
                        break

            if not overlap:
                active_blocks.append({"rect": rect, "color": BLOCK_COLORS[current_color_idx], "time": n["time"], "note_index": idx})
                n["spawned"] = True

    # Update block positions from their note time and current elapsed time
    for block in active_blocks:
        block_time = block.get("time", 0)
        block["rect"].y = int(max(0, (elapsed - block_time) * pixels_per_second))

    # Remove missed notes to avoid unbounded accumulation.
    # A block is considered missed once its top moves past a threshold below the hit line
    # unless it has been marked as 'hit' (visual feedback from input handling).
    miss_threshold = hit_y + int(MOEILIJKHEID * 1.5)
    kept = []
    missed_count = 0
    for block in active_blocks:
        # keep if it was hit (allow caller to mark hit blocks) or not yet past threshold
        if block.get("hit"):
            kept.append(block)
        else:
            if block["rect"].top <= miss_threshold:
                kept.append(block)
            else:
                missed_count += 1

    # mutate active_blocks in-place for caller convenience
    old_len = len(active_blocks)
    active_blocks[:] = kept

    # Note: music playback is controlled by main.py (visual lead time scheduling).
    # Do not start music here; return music_started unchanged.

    return music_started, missed_count
