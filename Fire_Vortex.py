
import pygame 
import random
import math
import time
import ctypes

# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------
user_text = input("Enter the text you want to animate in fire: ").strip()
if user_text == "":
    user_text = "PRABHAKAR"

# ---------------------------------------------------------
# INITIAL SETUP
# ---------------------------------------------------------
pygame.init()
width, height = 1100, 450
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("🔥 Fire Vortex + Explosion Outro")

# Force window to front
hwnd = pygame.display.get_wm_info()['window']
ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

clock = pygame.time.Clock()

# ---------------------------------------------------------
# DYNAMIC FONT SCALING
# ---------------------------------------------------------
font_size = 180
if len(user_text) > 10:
    font_size = 150
if len(user_text) > 20:
    font_size = 120

font = pygame.font.SysFont("Arial", font_size, bold=True)

text_surface = font.render(user_text, True, (255, 255, 255))
text_width, text_height = text_surface.get_size()
offset_x = (width - text_width) // 2
offset_y = (height - text_height) // 2

mask = pygame.mask.from_surface(text_surface)
mask_points = []

# Extract all text pixels
for x in range(text_width):
    for y in range(text_height):
        if mask.get_at((x, y)):
            mask_points.append((x + offset_x, y + offset_y))

mask_points = random.sample(mask_points, min(3000, len(mask_points)))

# ---------------------------------------------------------
# PARTICLE CLASS (VORTEX + FIRE + EXPLOSION OUTRO)
# ---------------------------------------------------------
class Particle:
    def __init__(self, tx, ty):
        self.tx = tx
        self.ty = ty

        # Spawn around screen in large circle
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(350, 650)
        self.x = width//2 + math.cos(angle) * radius
        self.y = height//2 + math.sin(angle) * radius

        self.angle = angle
        self.angular_speed = random.uniform(0.02, 0.045)

        self.vx = 0
        self.vy = 0

        # Fire-like color
        self.color = (
            random.randint(200, 255), 
            random.randint(80, 120),
            random.randint(0, 40)
        )

        self.phase = "vortex"

    def update(self):
        # -----------------------------------------------------
        # VORTEX INTRO
        # -----------------------------------------------------
        if self.phase == "vortex":
            self.angle += self.angular_speed

            # Radius shrinks slowly, pulling particles inward
            r = math.dist((self.x, self.y), (width//2, height//2))
            r *= 0.965

            self.x = width//2 + math.cos(self.angle) * r
            self.y = height//2 + math.sin(self.angle) * r

            if r < 40:
                self.phase = "intro"

        # -----------------------------------------------------
        # FIRE INTRO (particles approach the text)
        # -----------------------------------------------------
        if self.phase == "intro":
            dx = self.tx - self.x
            dy = self.ty - self.y

            self.vx += dx * 0.003
            self.vy += dy * 0.003

            self.vx *= 0.90
            self.vy *= 0.90

            self.x += self.vx
            self.y += self.vy

            if abs(dx) < 1 and abs(dy) < 1:
                self.phase = "hold"

        # -----------------------------------------------------
        # HOLD (Glow pulsing)
        # -----------------------------------------------------
        if self.phase == "hold":
            glow = 120 + int(120 * math.sin(time.time() * 6))
            self.color = (255, glow, 50)

        # -----------------------------------------------------
        # OUTRO: BIG FIRE EXPLOSION
        # -----------------------------------------------------
        if self.phase == "explode":
            # Big outward velocity
            self.x += self.vx * 1.5
            self.y += self.vy * 1.5

            # Slowly change to ash color
            self.color = (
                max(60, self.color[0] - 3),
                max(40, self.color[1] - 3),
                max(20, self.color[2] - 2)
            )

        # -----------------------------------------------------
        # FALLING ASH PHASE
        # -----------------------------------------------------
        if self.phase == "ash":
            self.vy += 0.1  # gravity
            self.x += self.vx
            self.y += self.vy

            # fade out
            self.color = (
                max(30, self.color[0] - 1),
                max(20, self.color[1] - 1),
                max(10, self.color[2] - 1)
            )

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 2)

# ---------------------------------------------------------
# CREATE PARTICLES
# ---------------------------------------------------------
particles = [Particle(tx, ty) for tx, ty in mask_points]

# Smoke particles
smoke_particles = []

class Smoke:
    def __init__(self):
        self.x = random.randint(offset_x, offset_x + text_width)
        self.y = offset_y - 20
        self.alpha = random.randint(70, 140)

    def update(self):
        self.y -= 0.4
        self.alpha -= 1

    def draw(self):
        if self.alpha > 0:
            s = pygame.Surface((14, 14), pygame.SRCALPHA)
            s.fill((100, 100, 100, self.alpha))
            screen.blit(s, (self.x, self.y))

# Explosion shockwave variables
shockwave_radius = 0
shockwave_active = False

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
phase = "vortex"
hold_start = 0
running = True

while running:
    screen.fill((10, 0, 0))

    # Heatwave lines
    baseline = offset_y + text_height + 10
    for x in range(0, width, 5):
        offset = int(4 * math.sin(time.time() * 4 + x * 0.05))
        pygame.draw.line(screen, (40, 15, 0), 
                         (x, baseline + offset),
                         (x, baseline + 15 + offset), 2)

    all_ready = True

    # UPDATE PARTICLES
    for p in particles:
        p.update()
        p.draw(screen)
        if p.phase != "hold" and phase != "explode":
            all_ready = False

    # Smoke
    if phase == "hold" and random.random() < 0.25:
        smoke_particles.append(Smoke())

    for s in smoke_particles:
        s.update()
        s.draw()

    # PHASE TRANSITIONS
    if phase == "vortex":
        if all(p.phase == "intro" for p in particles):
            phase = "intro"

    elif phase == "intro":
        if all_ready:
            phase = "hold"
            hold_start = time.time()

    elif phase == "hold":
        if time.time() - hold_start > 2.0:
            # EXPLOSION!
            shockwave_active = True
            for p in particles:
                dx = p.x - (width//2)
                dy = p.y - (height//2)
                p.vx = dx * 0.12
                p.vy = dy * 0.12
                p.phase = "explode"
            phase = "explode"

    elif phase == "explode":
        shockwave_radius += 12
        pygame.draw.circle(screen, (255, 140, 40), 
                           (width//2, height//2), 
                           shockwave_radius, 4)

        if shockwave_radius > 700:
            for p in particles:
                p.phase = "ash"
            phase = "ash"

    elif phase == "ash":
        if all(p.y > height + 100 for p in particles):
            running = False

    # Exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
