import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_card(screen, x, y, value=None, font=None):
    pygame.draw.rect(screen, WHITE, (x, y, 80, 120))
    pygame.draw.rect(screen, BLACK, (x, y, 80, 120), 2)
    text = font.render("?" if value is None else str(value), True, BLACK)
    screen.blit(text, (x + 25, y + 40))

def draw_button(screen, text, x, y, w, h, color, small_font):
    pygame.draw.rect(screen, color, (x, y, w, h))
    label = small_font.render(text, True, BLACK)
    screen.blit(label, (x + 10, y + 10))
    return pygame.Rect(x, y, w, h)
