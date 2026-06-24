import pygame
import random

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
            if steering.length() > 0: steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force: steering.scale_to_length(self.max_force)
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
            if steering.length() > 0: steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force: steering.scale_to_length(self.max_force)
        return steering

    def separation(self, boids):
        perception = 24
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            d = self.position.distance_to(other.position)
            if other != self and 0 < d < perception:
                diff = self.position - other.position
                diff /= (d * d)
                steering += diff
                total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0: steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force: steering.scale_to_length(self.max_force)
        return steering

    def flock(self, boids):
        # Fixed weights for stable flocking
        self.acceleration += self.align(boids) * 1.0
        self.acceleration += self.cohesion(boids) * 1.0
        self.acceleration += self.separation(boids) * 1.5

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.acceleration *= 0 

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.position.x), int(self.position.y)), 3)

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Task 1: Basic Boids")
    clock = pygame.time.Clock()

    # Minimum 100 agents requirement
    flock = [Boid(random.uniform(0, width), random.uniform(0, height)) for _ in range(120)]

    running = True
    while running:
        screen.fill((30, 30, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for boid in flock:
            boid.edges(width, height)
            boid.flock(flock)
            boid.update()
            boid.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()