import pygame
import random

align_weight = 1.0
cohesion_weight = 1.0
separation_weight = 1.0

class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() > 0:
            self.velocity.scale_to_length(random.uniform(2, 4))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_force = 0.2
        self.max_speed = 4

    def edges(self, width, height):
        if self.position.x > width: self.position.x = 0
        elif self.position.x < 0: self.position.x = width
        if self.position.y > height: self.position.y = 0
        elif self.position.y < 0: self.position.y = height

    def align(self, boids):
        perception = 50
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < perception:
                steering += other.velocity
                total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0:
                steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force:
                steering.scale_to_length(self.max_force)
        return steering

    def cohesion(self, boids):
        perception = 50
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < perception:
                steering += other.position
                total += 1
        if total > 0:
            steering /= total
            steering -= self.position
            if steering.length() > 0:
                steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force:
                steering.scale_to_length(self.max_force)
        return steering

    def separation(self, boids):
        perception = 24
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            d = self.position.distance_to(other.position)
            if other != self and d < perception and d > 0:
                diff = self.position - other.position
                diff /= (d * d) # Weight by distance
                steering += diff
                total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0:
                steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force:
                steering.scale_to_length(self.max_force)
        return steering

    def flock(self, boids):
        alignment = self.align(boids) * align_weight
        cohes = self.cohesion(boids) * cohesion_weight
        separ = self.separation(boids) * separation_weight

        self.acceleration += alignment + cohes + separ

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.acceleration *= 0 # Reset

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.position.x), int(self.position.y)), 3)

def main():
    global align_weight, cohesion_weight, separation_weight
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Task 1 & 2: Boids & Parameters")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    flock = [Boid(random.uniform(0, width), random.uniform(0, height)) for _ in range(150)]

    running = True
    while running:
        screen.fill((30, 30, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Controls for Task 2
                if event.key == pygame.K_q: align_weight += 0.1
                if event.key == pygame.K_a: align_weight = max(0, align_weight - 0.1)
                if event.key == pygame.K_w: cohesion_weight += 0.1
                if event.key == pygame.K_s: cohesion_weight = max(0, cohesion_weight - 0.1)
                if event.key == pygame.K_e: separation_weight += 0.1
                if event.key == pygame.K_d: separation_weight = max(0, separation_weight - 0.1)

        for boid in flock:
            boid.edges(width, height)
            boid.flock(flock)
            boid.update()
            boid.draw(screen)

        # UI Overlay
        controls_text = [
            f"Alignment (Q/A): {align_weight:.1f}",
            f"Cohesion (W/S): {cohesion_weight:.1f}",
            f"Separation (E/D): {separation_weight:.1f}"
        ]
        for i, text in enumerate(controls_text):
            img = font.render(text, True, (200, 200, 200))
            screen.blit(img, (10, 10 + (i * 25)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()