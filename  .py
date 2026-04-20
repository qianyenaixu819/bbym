import pygame
import math

pygame.init()

WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("跨性别骄傲旗帜")

LIGHT_BLUE = (91, 206, 250)
PINK = (246, 163, 206)
WHITE = (255, 255, 255)

flag_x = 50
flag_y = 50
flag_w = 300
flag_h = 200
stripe_h = flag_h // 5

# 飘动参数
time = 0
amplitude = 5
frequency = 0.05

# 文字与交互
font = pygame.font.SysFont("Arial", 18)
text = "Trans Rights Are Human Rights"
text_color = WHITE
bg_color = (30, 30, 30)

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(bg_color)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # 鼠标点击切换文字颜色
        if event.type == pygame.MOUSEBUTTONDOWN:
            text_color = (
                pygame.Color(random.randint(0,255)),
                pygame.Color(random.randint(0,255)),
                pygame.Color(random.randint(0,255))
            )

    # 绘制飘动旗帜
    for stripe in range(5):
        if stripe in [0, 4]:
            color = LIGHT_BLUE
        elif stripe in [1, 3]:
            color = PINK
        else:
            color = WHITE
            
        base_y = flag_y + stripe * stripe_h
        
        for x in range(flag_w):
            offset = int(amplitude * math.sin(frequency * (x + time)))
            y = base_y + offset
            pygame.draw.rect(screen, color, (flag_x + x, y, 1, stripe_h))

    # 绘制文字标语
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT - 20))
    screen.blit(text_surf, text_rect)

    time += 2
    if time > 360:
        time = 0

    pygame.display.flip()
    clock.tick(60)

pygame.quit()