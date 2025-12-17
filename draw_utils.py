import pygame
import math


def draw_gear(surface, rect, color):
    """Draws a procedural gear icon"""
    cx, cy = rect.center
    radius = rect.width // 2
    
    # Draw teeth
    for i in range(8):
        angle = i * (360 / 8)
        rad = math.radians(angle)
        ox = cx + math.cos(rad) * (radius + 4)
        oy = cy + math.sin(rad) * (radius + 4)
        pygame.draw.circle(surface, color, (int(ox), int(oy)), 5)
    
    # Main body
    pygame.draw.circle(surface, color, (cx, cy), radius)
    # Inner hole
    pygame.draw.circle(surface, (10, 10, 10), (cx, cy), radius // 2.5)
