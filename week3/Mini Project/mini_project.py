import pygame
import random
import time

class Civilian:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length() > 0:
            self.velocity.scale_to_length(random.uniform(2, 4))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_force = 0.25
        self.max_speed = 3.5
        self.perception = 50
        
        self.danger_pos = None
        self.panic_timer = 0

    def edges(self, width, height):
        if self.position.x > width - 10 or self.position.x < 10:
            self.velocity.x *= -1
        if self.position.y > height - 10 or self.position.y < 10:
            self.velocity.y *= -1

    def flock(self, civilians):
        align = pygame.Vector2(0, 0)
        cohes = pygame.Vector2(0, 0)
        separ = pygame.Vector2(0, 0)
        total = 0

        for other in civilians:
            d = self.position.distance_to(other.position)
            if other != self and d < self.perception:
                align += other.velocity
                cohes += other.position
                if d < 24 and d > 0:
                    diff = self.position - other.position
                    diff /= (d * d)
                    separ += diff
                total += 1

        if total > 0:
            align /= total
            if align.length() > 0: align.scale_to_length(self.max_speed)
            align -= self.velocity
            if align.length() > self.max_force: align.scale_to_length(self.max_force)

            cohes /= total
            cohes -= self.position
            if cohes.length() > 0: cohes.scale_to_length(self.max_speed)
            cohes -= self.velocity
            if cohes.length() > self.max_force: cohes.scale_to_length(self.max_force)

            separ /= total
            if separ.length() > 0: separ.scale_to_length(self.max_speed)
            separ -= self.velocity
            if separ.length() > self.max_force: separ.scale_to_length(self.max_force)

        cohesion_weight = 0.2 if self.panic_timer > 0 else 1.0
        self.acceleration += align * 1.0 + cohes * cohesion_weight + separ * 1.5

    def react_to_danger(self, zombies, civilians):
        closest_zombie = None
        record = float('inf')
        for z in zombies:
            d = self.position.distance_to(z.position)
            if d < record:
                record = d
                closest_zombie = z

        if closest_zombie and record < 100:
            self.danger_pos = pygame.Vector2(closest_zombie.position)
            self.panic_timer = 60

        if self.panic_timer > 0 and self.danger_pos:
            for other in civilians:
                if other != self and self.position.distance_to(other.position) < 60:
                    if random.random() < 0.20:
                        other.danger_pos = pygame.Vector2(self.danger_pos)
                        other.panic_timer = 60

        if self.panic_timer > 0 and self.danger_pos:
            desired = self.position - self.danger_pos
            if desired.length() > 0:
                desired.scale_to_length(self.max_speed)
            steer = desired - self.velocity
            if steer.length() > self.max_force * 2:
                steer.scale_to_length(self.max_force * 2)
            self.acceleration += steer * 3.0
            
            self.panic_timer -= 1

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        self.acceleration *= 0

    def draw(self, screen):
        color = (255, 255, 0) if self.panic_timer > 0 else (150, 200, 255)
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), 3)

class Zombie:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_speed = 3.8
        self.max_force = 0.15

    def edges(self, width, height):
        if self.position.x > width - 10 or self.position.x < 10: self.velocity.x *= -1
        if self.position.y > height - 10 or self.position.y < 10: self.velocity.y *= -1

    def seek_and_infect(self, civilians, new_zombies_list):
        closest = None
        record = float('inf')
        for c in civilians:
            d = self.position.distance_to(c.position)
            if d < record:
                record = d
                closest = c
        
        if closest:
            if record < 8:
                civilians.remove(closest)
                new_zombies_list.append(Zombie(closest.position.x, closest.position.y))
                return

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
        pygame.draw.circle(screen, (255, 50, 50), (int(self.position.x), int(self.position.y)), 5)

def calculate_groups(civilians, radius=40):
    visited = set()
    groups = 0
    for c in civilians:
        if c not in visited:
            groups += 1
            queue = [c]
            visited.add(c)
            while queue:
                curr = queue.pop(0)
                for other in civilians:
                    if other not in visited and curr.position.distance_to(other.position) < radius:
                        visited.add(other)
                        queue.append(other)
    return groups

def main():
    pygame.init()
    width, height = 1000, 700
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mini Project: Zombie Evacuation Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 18, bold=True)

    initial_civilians = 200
    civilians = [Civilian(random.uniform(50, width-50), random.uniform(50, height-50)) for _ in range(initial_civilians)]
    
    zombies = [Zombie(50, 50), Zombie(width-50, height-50)]

    start_time = time.time()
    collapse_time = 0
    collapsed = False
    
    num_groups = 0
    avg_group_size = 0

    running = True
    while running:
        screen.fill((20, 20, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        new_zombies = []

        for c in civilians:
            c.edges(width, height)
            c.flock(civilians)
            c.react_to_danger(zombies, civilians)
            c.update()
            c.draw(screen)

        for z in zombies:
            z.edges(width, height)
            z.seek_and_infect(civilians, new_zombies)
            z.update()
            z.draw(screen)

        zombies.extend(new_zombies)

        current_civilians = len(civilians)
        survival_rate = (current_civilians / initial_civilians) * 100
        
        if pygame.time.get_ticks() % 10 == 0 and current_civilians > 0:
            num_groups = calculate_groups(civilians)
            avg_group_size = current_civilians / num_groups
        elif current_civilians == 0:
            num_groups = 0
            avg_group_size = 0

        if current_civilians > 0:
            elapsed = time.time() - start_time
        else:
            if not collapsed:
                collapse_time = time.time() - start_time
                collapsed = True
            elapsed = collapse_time

        ui_panel = pygame.Surface((300, 140))
        ui_panel.set_alpha(200)
        ui_panel.fill((0, 0, 0))
        screen.blit(ui_panel, (10, 10))

        texts = [
            f"Civilians Alive: {current_civilians}",
            f"Survival Rate:   {survival_rate:.1f}%",
            f"Groups Formed:   {num_groups}",
            f"Avg Group Size:  {avg_group_size:.1f}",
            f"Time Elapsed:    {elapsed:.1f}s"
        ]
        
        if collapsed:
            texts.append("TOTAL COLLAPSE ACHIEVED")

        for i, text in enumerate(texts):
            color = (255, 50, 50) if "COLLAPSE" in text else (255, 255, 255)
            img = font.render(text, True, color)
            screen.blit(img, (20, 20 + (i * 20)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()