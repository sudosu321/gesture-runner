import pygame
import cv2
import mediapipe as mp
import threading

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)
mp_draw = mp.solutions.drawing_utils
gesture = "HAND CLOSED"
hasJumped=False
def detect_hand():
    global gesture,hasJumped

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture = "FIST"
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
                tips = [8, 12, 16, 20]
                open_fingers = 0

                for tip in tips:
                    if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                        open_fingers += 1

                if open_fingers >= 3:
                    gesture = "OPEN"
                else: 
                    hasJumped=False
        cv2.putText(frame, gesture, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

threading.Thread(target=detect_hand, daemon=True).start()
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Gesture Runner")

clock = pygame.time.Clock()

player_y = 300
velocity = 0
gravity = 1
is_jumping = False
obstacle_vel=8
obstacle_x = 800
score = 0

font = pygame.font.SysFont('Monospace', 40)

def jump():
    global velocity, is_jumping ,hasJumped
    if not is_jumping:
        velocity = -20
        hasJumped=True
        is_jumping = True

running = True
game_over = False

while running:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
            running=False
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            break
    screen.fill((15, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        if gesture == "OPEN" and hasJumped==False:
            jump()

        velocity += gravity
        player_y += velocity

        if player_y >= 300:
            player_y = 300
            is_jumping = False

        obstacle_x -= obstacle_vel
        if obstacle_x < -50:
            obstacle_x = 800
            score += 1

        ground_rect = pygame.Rect(0,350,1000,100)
        player_rect = pygame.Rect(100, player_y, 50, 50)
        obstacle_rect = pygame.Rect(obstacle_x, 300, 50, 50)

        if player_rect.colliderect(obstacle_rect):
            game_over = True

        pygame.draw.rect(screen, (0, 255, 0), ground_rect)

        pygame.draw.rect(screen, (0, 255, 255), player_rect)
        pygame.draw.rect(screen, (255, 0, 0), obstacle_rect)
        score_text = font.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_text, (10, 10))

    else:
        text = font.render("GAME OVER - Press R", True, (255,255,255))
        screen.blit(text, (200, 180))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_over = False
            obstacle_x = 800
            score = 0
            player_y = 300
            velocity = 0

    pygame.display.update()
    clock.tick(60)

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()