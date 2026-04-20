import pygame
import math
import sys

# 初始化pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("鱼板图标动画")

# 颜色定义（严格按照图标配色）
WHITE = (255, 255, 255)
PINK = (255, 102, 153)    # 粉色螺旋
GRAY = (192, 192, 192)    # 灰色外边框
SHADOW = (128, 128, 128)  # 阴影颜色

# 中心坐标
cx, cy = WIDTH // 2, HEIGHT // 2

# 动画角度（只用于外框）
angle = 0

def draw_spiral(surface, center, radius, color, line_width, num_turns=2):
    """绘制静态阿基米德螺旋，模拟图标中的粉色图案"""
    points = []
    # 增加采样点数量，使螺旋更平滑
    for t in range(0, int(num_turns * 2 * math.pi * 200)):
        theta = t / 200.0
        r = radius * theta / (num_turns * 2 * math.pi)
        # 移除 angle，让螺旋固定不动
        x = center[0] + r * math.cos(theta)
        y = center[1] + r * math.sin(theta)
        points.append((int(x), int(y)))
    
    if len(points) > 1:
        pygame.draw.lines(surface, color, False, points, line_width)

def draw_star_polygon(surface, color, outer_radius, inner_radius, num_points=12):
    """绘制带边角的星形多边形，还原图标外框"""
    points = []
    for i in range(num_points * 2):
        theta = i * math.pi / num_points + angle
        if i % 2 == 0:
            r = outer_radius
        else:
            r = inner_radius
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color, points)

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 清空屏幕
    screen.fill((255, 255, 255))

    # 1. 绘制阴影（外边框偏移）
    draw_star_polygon(screen, SHADOW, 152, 132)

    # 2. 绘制灰色外边框
    draw_star_polygon(screen, GRAY, 148, 128)

    # 3. 绘制白色内花瓣
    draw_star_polygon(screen, WHITE, 120, 100)

    # 4. 绘制静态粉色螺旋（核心图案，加粗线条更清晰）
    draw_spiral(screen, (cx, cy), 100, PINK, 30)

    # 更新角度，只让外框旋转
    angle += 0.01

    # 刷新屏幕
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()