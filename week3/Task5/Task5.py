import pygame
import random

class Agent:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() > 0:
            self.velocity.scale_to_length(random.uniform(2, 4))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_force = 0.2
        self.max_speed = 4
        
        self.informed = False 
        self.perception = 50

    def edges(self, width, height):
        if self.position.x > width: self.position.x = 0
        elif self.position.x < 0: self.position.x = width
        if self.position.y > height: self.position.y = 0
        elif self.position.y < 0: self.position.y = height

    def align(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < self.perception:
                steering += other.velocity
                total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0: steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force: steering.scale_to_length(self.max_force)
        return steering

    def cohesion(self, boids):
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < self.perception:
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
        sep_radius = 24
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            d = self.position.distance_to(other.position)
            if other != self and 0 < d < sep_radius:
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

    def share_information(self, boids):
        if not self.informed:
            return 

        interaction_radius = 40 
        for other in boids:
            if other != self and not other.informed:
                if self.position.distance_to(other.position) < interaction_radius:
                    if random.random() < 0.10: 
                        other.informed = True

    def flock(self, boids):
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
        color = (255, 255, 0) if self.informed else (150, 200, 255)
        size = 5 if self.informed else 3
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), size)


def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Task 5: Information Spread")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 18, bold=True)

    population = [Agent(random.uniform(0, width), random.uniform(0, height)) for _ in range(150)]

    population[0].informed = True

    running = True
    while running:
        screen.fill((20, 20, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        informed_count = 0

        for agent in population:
            agent.edges(width, height)
            agent.flock(population)
            agent.share_information(population) 
            agent.update()
            agent.draw(screen)
            
            if agent.informed:
                informed_count += 1

        img = font.render(f"Informed Agents: {informed_count} / {len(population)}", True, (255, 255, 255))
        screen.blit(img, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()