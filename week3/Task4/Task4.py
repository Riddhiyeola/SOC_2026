import pygame
import random

class Prey:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() > 0:
            self.velocity.scale_to_length(random.uniform(2, 4))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_force = 0.2
        self.max_speed = 4
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

    def flee(self, predators):
        flee_perception = 100
        steering = pygame.Vector2(0, 0)
        total = 0
        for pred in predators:
            d = self.position.distance_to(pred.position)
            if d < flee_perception:
                diff = self.position - pred.position
                diff /= d  
                steering += diff
                total += 1
        if total > 0:
            steering /= total
            if steering.length() > 0: steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force * 2.5: 
                steering.scale_to_length(self.max_force * 2.5)
        return steering

    def flock(self, boids, predators):
        alignment = self.align(boids) * 1.0
        cohes = self.cohesion(boids) * 1.0
        separ = self.separation(boids) * 1.5
        escape = self.flee(predators) * 3.5  

        self.acceleration += alignment + cohes + separ + escape

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.acceleration *= 0 

    def draw(self, screen):
        pygame.draw.circle(screen, (150, 200, 255), (int(self.position.x), int(self.position.y)), 3)



class Predator:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_speed = 3.5  
        self.max_force = 0.15 

    def edges(self, width, height):
        if self.position.x > width: self.position.x = 0
        elif self.position.x < 0: self.position.x = width
        if self.position.y > height: self.position.y = 0
        elif self.position.y < 0: self.position.y = height

    def seek(self, prey_list):
        closest = None
        record = float('inf')
        for p in prey_list:
            d = self.position.distance_to(p.position)
            if d < record:
                record = d
                closest = p
        
        if closest:
            desired = closest.position - self.position
            if desired.length() > 0:
                desired.scale_to_length(self.max_speed)
            steering = desired - self.velocity
            if steering.length() > self.max_force:
                steering.scale_to_length(self.max_force)
            self.acceleration += steering

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.acceleration *= 0

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 50, 50), (int(self.position.x), int(self.position.y)), 6)


def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Task 4: Predator and Prey")
    clock = pygame.time.Clock()

    flock = [Prey(random.uniform(0, width), random.uniform(0, height)) for _ in range(150)]
    predators = [Predator(random.uniform(0, width), random.uniform(0, height)) for _ in range(2)]

    running = True
    while running:
        screen.fill((20, 20, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        for boid in flock:
            boid.edges(width, height)
            boid.flock(flock, predators)
            boid.update()
            boid.draw(screen)

        for pred in predators:
            pred.edges(width, height)
            pred.seek(flock)
            pred.update()
            pred.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()