import pygame
import random

params = {
    "alignment_strength": 0.0,
    "cohesion_strength": 2.5,
    "separation_strength": 2.5,
    "neighbor_radius": 100
}

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
        steering = pygame.Vector2(0, 0)
        total = 0
        for other in boids:
            if other != self and self.position.distance_to(other.position) < params["neighbor_radius"]:
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
            if other != self and self.position.distance_to(other.position) < params["neighbor_radius"]:
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
        sep_radius = params["neighbor_radius"] / 2 
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

    def flock(self, boids):
        self.acceleration += self.align(boids) * params["alignment_strength"]
        self.acceleration += self.cohesion(boids) * params["cohesion_strength"]
        self.acceleration += self.separation(boids) * params["separation_strength"]

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.acceleration *= 0 

    def draw(self, screen):
        pygame.draw.circle(screen, (100, 200, 255), (int(self.position.x), int(self.position.y)), 3)

def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Task 2: Parameter Exploration (Oscillation/Swarming)")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Courier", 16, bold=True)

    flock = [Boid(random.uniform(0, width), random.uniform(0, height)) for _ in range(120)]

    running = True
    while running:
        screen.fill((20, 20, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Adjust Alignment Strength
                if event.key == pygame.K_q: params["alignment_strength"] += 0.1
                if event.key == pygame.K_a: params["alignment_strength"] = max(0, params["alignment_strength"] - 0.1)
                # Adjust Cohesion Strength
                if event.key == pygame.K_w: params["cohesion_strength"] += 0.1
                if event.key == pygame.K_s: params["cohesion_strength"] = max(0, params["cohesion_strength"] - 0.1)
                # Adjust Separation Strength
                if event.key == pygame.K_e: params["separation_strength"] += 0.1
                if event.key == pygame.K_d: params["separation_strength"] = max(0, params["separation_strength"] - 0.1)
                # Adjust Neighbor Radius
                if event.key == pygame.K_r: params["neighbor_radius"] += 5
                if event.key == pygame.K_f: params["neighbor_radius"] = max(10, params["neighbor_radius"] - 5)

        for boid in flock:
            boid.edges(width, height)
            boid.flock(flock)
            boid.update()
            boid.draw(screen)

        ui_text = [
            "Use Keys to adjust parameters:",
            f"[Q/A] Alignment strength:  {params['alignment_strength']:.1f}",
            f"[W/S] Cohesion strength:   {params['cohesion_strength']:.1f}",
            f"[E/D] Separation strength: {params['separation_strength']:.1f}",
            f"[R/F] Neighbor radius:     {params['neighbor_radius']}"
        ]
        
        for i, text in enumerate(ui_text):
            img = font.render(text, True, (255, 255, 255))
            screen.blit(img, (10, 10 + (i * 25)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()