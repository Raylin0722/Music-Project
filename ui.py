# ui.py - UI 元件：Button, TextInput, Slider
import pygame

class Button:
    def __init__(self, text, x, y, width, height, callback, font, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = font
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (100, 100, 255), self.rect)
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


class TextInput:
    def __init__(self, x, y, width, font, initial_text=""):
        self.rect = pygame.Rect(x, y, width, 50)
        self.font = font
        self.text = initial_text
        self.active = False
        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_pos = len(initial_text)
        self.selection_start = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                mouse_x = event.pos[0] - self.rect.x - 8
                for i in range(len(self.text) + 1):
                    if self.font.size(self.text[:i])[0] >= mouse_x:
                        self.cursor_pos = i
                        break
                else:
                    self.cursor_pos = len(self.text)
                self.selection_start = self.cursor_pos

        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None and self.selection_start != self.cursor_pos:
                    self.delete_selection()
                elif self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None and self.selection_start != self.cursor_pos:
                    self.delete_selection()
                elif self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos + 1
                else:
                    self.selection_start = None
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos - 1
                else:
                    self.selection_start = None
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode:
                self.insert_text(event.unicode)

    def insert_text(self, content):
        if self.selection_start is not None and self.selection_start != self.cursor_pos:
            self.delete_selection()
        self.text = self.text[:self.cursor_pos] + content + self.text[self.cursor_pos:]
        self.cursor_pos += len(content)

    def delete_selection(self):
        start, end = sorted([self.selection_start, self.cursor_pos])
        self.text = self.text[:start] + self.text[end:]
        self.cursor_pos = start
        self.selection_start = None

    def update(self):
        if self.active:
            self.cursor_counter += 1
            if self.cursor_counter >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_counter = 0
        else:
            self.cursor_visible = False

    def draw(self, screen):
        color = (0, 128, 0) if self.active else (128, 128, 128)
        pygame.draw.rect(screen, color, self.rect, 2)

        text_y = self.rect.y + (self.rect.height - self.font.get_height()) // 2

        if self.selection_start is not None and self.selection_start != self.cursor_pos:
            start, end = sorted([self.selection_start, self.cursor_pos])
            x1 = self.rect.x + 8 + self.font.size(self.text[:start])[0]
            x2 = self.rect.x + 8 + self.font.size(self.text[:end])[0]
            pygame.draw.rect(screen, (180, 180, 255), (x1, text_y, x2 - x1, self.font.get_height()))

        text_surf = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surf, (self.rect.x + 8, text_y))

        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 8 + self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, text_y), (cursor_x, text_y + self.font.get_height()), 2)

    def get_text(self):
        return self.text
    

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_value):
        self.rect = pygame.Rect(x, y, width, 8)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value
        self.handle_radius = 10
        self.dragging = False
        self.width = width

    def get_handle_rect(self):
        handle_x = self.rect.left + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_y = self.rect.centery
        return pygame.Rect(int(handle_x - self.handle_radius), int(handle_y - self.handle_radius),
                           self.handle_radius * 2, self.handle_radius * 2)

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
