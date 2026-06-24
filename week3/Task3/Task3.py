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

    def avoid_obstacles(self, obstacles):
        steering = pygame.Vector2(0, 0)
        avoid_perception = 60 
        total = 0

        for obs in obstacles:
            if obs['type'] == 'circle':
                dist = self.position.distance_to(obs['pos'])
                if dist < obs['radius'] + avoid_perception:
                    diff = self.position - obs['pos']
                    if dist > 0:
                        diff /= (dist)
                    steering += diff
                    total += 1
            
            elif obs['type'] == 'rect':
                rect = obs['rect']
                closest_x = max(rect.left, min(self.position.x, rect.right))
                closest_y = max(rect.top, min(self.position.y, rect.bottom))
                closest_point = pygame.Vector2(closest_x, closest_y)
                
                dist = self.position.distance_to(closest_point)
                if 0 < dist < avoid_perception:
                    diff = self.position - closest_point
                    diff /= (dist)
                    steering += diff
                    total += 1

        if total > 0:
            steering /= total
            if steering.length() > 0: steering.scale_to_length(self.max_speed)
            steering -= self.velocity
            if steering.length() > self.max_force * 2.5: 
                steering.scale_to_length(self.max_force * 2.5)
        
        return steering

    def flock(self, boids, obstacles):
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)
        avoidance = self.avoid_obstacles(obstacles)

        self.acceleration += alignment * 1.0
        self.acceleration += cohesion * 1.0
        self.acceleration += separation * 1.5
        self.acceleration += avoidance * 3.5 

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
    pygame.display.set_caption("Task 3: Obstacle Avoidance")
    clock = pygame.time.Clock()

    flock = [Boid(random.uniform(0, width), random.uniform(0, height)) for _ in range(150)]

    obstacles = [
        {'type': 'circle', 'pos': pygame.Vector2(200, 200), 'radius': 50},
        {'type': 'circle', 'pos': pygame.Vector2(600, 400), 'radius': 70},
        {'type': 'rect', 'rect': pygame.Rect(350, 200, 50, 200)} # A wall in the middle
    ]

    running = True
    while running:
        screen.fill((30, 30, 40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for obs in obstacles:
            if obs['type'] == 'circle':
                pygame.draw.circle(screen, (200, 50, 50), (int(obs['pos'].x), int(obs['pos'].y)), obs['radius'])
            elif obs['type'] == 'rect':
                pygame.draw.rect(screen, (200, 50, 50), obs['rect'])

        for boid in flock:
            boid.edges(width, height)
            boid.flock(flock, obstacles)
            boid.update()
            boid.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()