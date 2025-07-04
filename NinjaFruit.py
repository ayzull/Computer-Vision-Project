import cv2
import time
import random
import HandTrackingModule as htm
import numpy as np
import json
import os

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.75)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.randint(-10, 10)
        self.vy = random.randint(-15, -5)
        self.color = color
        self.life = 30
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5  # gravity
        self.life -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, img):
        if self.life > 0:
            cv2.circle(img, (int(self.x), int(self.y)), int(self.size), self.color, cv2.FILLED)

class Fruit:
    def __init__(self, fruit_type=None):
        self.x = random.randint(50, wCam - 50)
        self.y = 0
        self.radius = random.randint(25, 35)
        self.speed = random.randint(5, 12)
        self.sliced = False
        self.rotation = 0
        self.rotation_speed = random.randint(-10, 10)
        
        # Different fruit types
        if fruit_type is None:
            fruit_type = random.choice(['apple', 'orange', 'banana', 'strawberry', 'watermelon'])
        
        self.type = fruit_type
        if fruit_type == 'apple':
            self.color = (0, 0, 255)  # Red
            self.points = 10
        elif fruit_type == 'orange':
            self.color = (0, 165, 255)  # Orange
            self.points = 15
        elif fruit_type == 'banana':
            self.color = (0, 255, 255)  # Yellow
            self.points = 20
        elif fruit_type == 'strawberry':
            self.color = (128, 0, 255)  # Pink
            self.points = 25
        elif fruit_type == 'watermelon':
            self.color = (0, 128, 0)  # Green
            self.points = 30

    def fall(self):
        self.y += self.speed
        self.rotation += self.rotation_speed

    def draw(self, img):
        if not self.sliced:
            # Draw fruit with rotation effect
            cv2.circle(img, (self.x, self.y), self.radius, self.color, cv2.FILLED)
            cv2.circle(img, (self.x, self.y), self.radius, (255, 255, 255), 2)
            
            # Add shine effect
            shine_x = self.x - self.radius // 3
            shine_y = self.y - self.radius // 3
            cv2.circle(img, (shine_x, shine_y), self.radius // 4, (255, 255, 255), cv2.FILLED)

    def check_collision(self, tip_pos):
        dist = ((self.x - tip_pos[0])**2 + (self.y - tip_pos[1])**2)**0.5
        if dist < self.radius:
            self.sliced = True
            return True
        return False

class Bomb:
    def __init__(self):
        self.x = random.randint(50, wCam - 50)
        self.y = 0
        self.radius = 30
        self.color = (0, 0, 0)  # Black
        self.speed = random.randint(4, 8)
        self.sliced = False
        self.flash = 0

    def fall(self):
        self.y += self.speed
        self.flash = (self.flash + 1) % 20

    def draw(self, img):
        if not self.sliced:
            # Flashing bomb effect
            color = (0, 0, 255) if self.flash < 10 else (0, 0, 0)
            cv2.circle(img, (self.x, self.y), self.radius, color, cv2.FILLED)
            cv2.circle(img, (self.x, self.y), self.radius, (255, 255, 255), 3)
            
            # Draw fuse
            cv2.line(img, (self.x, self.y - self.radius), 
                    (self.x - 5, self.y - self.radius - 10), (255, 255, 0), 3)

    def check_collision(self, tip_pos):
        dist = ((self.x - tip_pos[0])**2 + (self.y - tip_pos[1])**2)**0.5
        if dist < self.radius:
            self.sliced = True
            return True
        return False

class Game:
    def __init__(self):
        self.state = MENU
        self.score = 0
        self.lives = 3
        self.high_score = self.load_high_score()
        self.fruits = []
        self.bombs = []
        self.particles = []
        self.combo = 0
        self.combo_timer = 0
        self.level = 1
        self.fruits_sliced_this_level = 0
        
    def load_high_score(self):
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.fruits = []
        self.bombs = []
        self.particles = []
        self.combo = 0
        self.combo_timer = 0
        self.level = 1
        self.fruits_sliced_this_level = 0
        self.state = PLAYING
    
    def spawn_objects(self):
        # Increase spawn rate with level
        spawn_chance = max(15, 30 - self.level * 2)
        
        if random.randint(1, spawn_chance) == 1:
            # 80% chance for fruit, 20% chance for bomb
            if random.randint(1, 5) <= 4:
                self.fruits.append(Fruit())
            else:
                self.bombs.append(Bomb())
    
    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def update_particles(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def check_level_up(self):
        if self.fruits_sliced_this_level >= 10 * self.level:
            self.level += 1
            self.fruits_sliced_this_level = 0
            return True
        return False
    
    def draw_menu(self, img):
        # Dark overlay
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (wCam, hCam), (0, 0, 0), cv2.FILLED)
        img = cv2.addWeighted(img, 0.3, overlay, 0.7, 0)
        
        # Title
        cv2.putText(img, "NINJA FRUIT", (wCam//2 - 150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        
        # Instructions
        cv2.putText(img, "Use your finger to slice fruits!", (wCam//2 - 160, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, "Avoid bombs! You have 3 lives.", (wCam//2 - 150, 230), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"High Score: {self.high_score}", (wCam//2 - 80, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Start instruction
        cv2.putText(img, "Raise your hand to start!", (wCam//2 - 130, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return img
    
    def draw_game_over(self, img):
        # Dark overlay
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (wCam, hCam), (0, 0, 0), cv2.FILLED)
        img = cv2.addWeighted(img, 0.3, overlay, 0.7, 0)
        
        # Game Over
        cv2.putText(img, "GAME OVER", (wCam//2 - 120, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        # Final Score
        cv2.putText(img, f"Final Score: {self.score}", (wCam//2 - 100, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # High Score
        if self.score > self.high_score:
            cv2.putText(img, "NEW HIGH SCORE!", (wCam//2 - 120, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(img, f"High Score: {self.high_score}", (wCam//2 - 100, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Restart instruction
        cv2.putText(img, "Raise your hand to restart", (wCam//2 - 130, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return img
    
    def draw_hud(self, img):
        # Score
        cv2.putText(img, f'Score: {self.score}', (10, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Lives
        for i in range(self.lives):
            cv2.circle(img, (10 + i * 30, 70), 10, (0, 0, 255), cv2.FILLED)
        
        # Level
        cv2.putText(img, f'Level: {self.level}', (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Combo
        if self.combo > 1 and self.combo_timer > 0:
            cv2.putText(img, f'Combo x{self.combo}!', (wCam//2 - 80, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        
        # High Score
        cv2.putText(img, f'High: {self.high_score}', (wCam - 150, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

# Initialize game
game = Game()
pTime = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img, draw=False)
    lmList = detector.findPosition(img)

    index_tip = None
    hand_detected = len(lmList) > 8
    if hand_detected:
        index_tip = (lmList[8][1], lmList[8][2])

    if game.state == MENU:
        img = game.draw_menu(img)
        if hand_detected:
            game.reset_game()
    
    elif game.state == PLAYING:
        # Draw finger tip
        if index_tip:
            cv2.circle(img, index_tip, 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, index_tip, 20, (255, 255, 255), 2)

        # Spawn objects
        game.spawn_objects()

        # Update fruits
        for fruit in game.fruits[:]:
            fruit.fall()
            fruit.draw(img)
            if index_tip and fruit.check_collision(index_tip):
                game.score += fruit.points * max(1, game.combo)
                game.combo += 1
                game.combo_timer = 60
                game.fruits_sliced_this_level += 1
                game.create_particles(fruit.x, fruit.y, fruit.color)
                
                # Check for level up
                if game.check_level_up():
                    game.score += 50  # Level bonus

        # Update bombs
        for bomb in game.bombs[:]:
            bomb.fall()
            bomb.draw(img)
            if index_tip and bomb.check_collision(index_tip):
                game.lives -= 1
                game.combo = 0
                game.create_particles(bomb.x, bomb.y, (255, 255, 255), 15)

        # Remove off-screen or sliced objects
        game.fruits = [f for f in game.fruits if not f.sliced and f.y < hCam + 50]
        game.bombs = [b for b in game.bombs if not b.sliced and b.y < hCam + 50]
        
        # Lose life for missed fruits
        missed_fruits = [f for f in game.fruits if f.y >= hCam]
        if missed_fruits:
            game.lives -= len(missed_fruits)
        
        # Update combo timer
        if game.combo_timer > 0:
            game.combo_timer -= 1
        else:
            game.combo = 0

        # Update particles
        game.update_particles()
        for particle in game.particles:
            particle.draw(img)

        # Draw HUD
        game.draw_hud(img)

        # Check game over
        if game.lives <= 0:
            if game.score > game.high_score:
                game.high_score = game.score
                game.save_high_score()
            game.state = GAME_OVER

    elif game.state == GAME_OVER:
        img = game.draw_game_over(img)
        if hand_detected:
            game.state = MENU

    # FPS Display
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (wCam - 100, hCam - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Ninja Fruit Enhanced", img)
    if cv2.waitKey(1) == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()