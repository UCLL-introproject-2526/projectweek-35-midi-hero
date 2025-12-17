import os
import mido
import pygame


def find_songs(song_dir):
    songs = []
    if not os.path.exists(song_dir):
        return songs

    for folder in os.listdir(song_dir):
        path = os.path.join(song_dir, folder)
        if not os.path.isdir(path):
            continue

        midi = None
        image = None
        for f in os.listdir(path):
            if f.lower().endswith((".mid", ".midi")):
                midi = os.path.join(path, f)
            elif f.lower().endswith((".png", ".jpg", ".jpeg")):
                image = os.path.join(path, f)

        if midi and image:
            songs.append({
                "name": folder,
                "midi": midi,
                "image": image
            })

    return songs


def load_song(song, screen):
    """Loads the MIDI into the mixer, parses notes and returns (background, notes).

    This function does not mutate game state; the caller should reset active
    blocks, score and other state as needed.
    """
    pygame.mixer.music.load(song["midi"])

    mid = mido.MidiFile(song["midi"])
    notes = []
    t = 0
    for msg in mid:
        t += msg.time
        if getattr(msg, "type", None) == "note_on" and getattr(msg, "velocity", 0) > 0:
            notes.append({"note": msg.note, "time": t})

    bg = pygame.image.load(song["image"]).convert()
    bg = pygame.transform.scale(bg, screen.get_size())

    # t now holds the approximate song length (seconds)
    return bg, notes, t
