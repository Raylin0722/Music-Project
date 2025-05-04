import pygame
from font_manager import FontManager

class Button:
    def __init__(self, text, x, y, width, height, callback, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = font

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 255), self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_value):
        self.rect = pygame.Rect(x, y, width, 8)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value
        self.handle_radius = 10
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.get_handle_rect().collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = min(max(event.pos[0], self.rect.left), self.rect.right)
            percent = (rel_x - self.rect.left) / self.rect.width
            self.value = int(self.min_val + percent * (self.max_val - self.min_val))

    def draw(self, screen):
        pygame.draw.rect(screen, (180, 180, 180), self.rect)
        handle_x = self.rect.left + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        pygame.draw.circle(screen, (0, 0, 0), (int(handle_x), self.rect.centery), self.handle_radius)

    def get_value(self):
        return self.value

class TextInput:
    def __init__(self, x, y, width, font):
        self.rect = pygame.Rect(x, y, width, 40)
        self.font = font
        self.text = ""
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode
    def draw(self, screen):
        color = (0, 128, 0) if self.active else (128, 128, 128)
        pygame.draw.rect(screen, color, self.rect, 2)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 8))
    def get_text(self):
        return self.text


