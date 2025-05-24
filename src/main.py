import pygame, sys
from player import deck, draw_card
from game_logic import calculate_win_prob, resolve_round
from ui import draw_card as draw_ui_card, draw_button

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("확률 기반 인디언 포커")
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 28)
small_font = pygame.font.SysFont("malgungothic", 22)

GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
GRAY = (160, 160, 160)

player_money, computer_money = 1000, 1000
player_card, computer_card = None, None
player_prob, computer_prob = 0, 0
player_bets = False
round_result = ""
explanation = ""
betting_done = False

def deal():
    global player_card, computer_card, player_prob, computer_prob, player_bets, betting_done, round_result, explanation
    player_card, computer_card = draw_card(deck)
    player_prob = calculate_win_prob(player_card, computer_card)
    computer_prob = calculate_win_prob(computer_card, player_card, is_player=False)
    player_bets = False
    betting_done = False
    round_result = ""
    explanation = ""

def draw_ui():
    screen.fill(GREEN)
    screen.blit(font.render(f"내 돈: {player_money}", True, WHITE), (50, 30))
    screen.blit(font.render(f"상대 돈: {computer_money}", True, WHITE), (650, 30))
    rounds_left = len(deck) // 2
    screen.blit(small_font.render(f"남은 라운드 수: {rounds_left}", True, WHITE), (380, 30))

    draw_ui_card(screen, 300, 250, None if not betting_done else player_card, font)
    draw_ui_card(screen, 500, 250, computer_card, font)
    screen.blit(font.render("VS", True, WHITE), (430, 290))
    screen.blit(small_font.render(f"이길 확률: {player_prob}%", True, WHITE), (650, 200))
    screen.blit(font.render(round_result, True, WHITE), (300, 390))
    for i, line in enumerate(explanation.split("\n")):
        screen.blit(small_font.render(line, True, WHITE), (50, 460 + i * 20))

    if not betting_done:
        return draw_button(screen, "베팅하기", 250, 520, 140, 40, BLUE, small_font), \
               draw_button(screen, "베팅하지 않기", 450, 520, 180, 40, RED, small_font)
    else:
        return draw_button(screen, "다음 라운드", 380, 520, 180, 40, GRAY, small_font), None

deal()
running = True
while running:
    buttons = draw_ui()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if buttons and buttons[0].collidepoint(event.pos):
                if not betting_done:
                    player_bets = True
                    player_money, computer_money, round_result, explanation = resolve_round(
                        player_card, computer_card, player_bets, player_money, computer_money, player_prob, computer_prob
                    )
                    betting_done = True
                else:
                    deal()
            elif buttons[1] and buttons[1].collidepoint(event.pos):
                player_bets = False
                player_money, computer_money, round_result, explanation = resolve_round(
                    player_card, computer_card, player_bets, player_money, computer_money, player_prob, computer_prob
                )
                betting_done = True
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
