class Screen:
    def __init__(self, screenSize=(800, 600)):
        self.screeWidth, self.screenHeight = screenSize
        self.UIelements = []
        
        
    def draw(self, screen):
        raise NotImplementedError("Subclasses should implement this method")    
    def handle_event(self, event):
        raise NotImplementedError("Subclasses should implement this method")
    def update(self):
        raise NotImplementedError("Subclasses should implement this method")
    def enter(self):
        raise NotImplementedError("Subclasses should implement this method")
    def exit(self):
        raise NotImplementedError("Subclasses should implement this method")