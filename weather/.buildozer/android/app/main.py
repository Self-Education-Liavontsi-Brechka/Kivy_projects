import random


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader


class MultiSound(object):
    def __init__(self, file, num):
        self.num = num
        self.sounds = [SoundLoader.load(file) for n in xrange(num)]
        self.index = 0

    def play(self):
        self.sounds[self.index].play()
        self.index += 1
        if self.index == self.num:
            self.index = 0

sfx_flap = MultiSound('audio/flap.wav', 6)
sfx_score = SoundLoader.load('audio/score.wav')
sfx_die = SoundLoader.load('audio/die.wav')


class Sprite(Image):
    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.size = self.texture_size


class Background(Widget):
    def __init__(self, source, **kwargs):
        super(Background, self).__init__(**kwargs)
        self.image = Sprite(source=source)
        self.add_widget(self.image)
        self.size = self.image.size
        self.image_dupe = Sprite(source=source, x=self.width)
        self.add_widget(self.image_dupe)

    def update(self):
        self.image.x -= 2
        self.image_dupe.x -= 2

        if self.image.right <= 0:
            self.image.x = 0
            self.image_dupe.x = self.width


class Bird(Sprite):
    def __init__(self, pos, **kwargs):
        super(Bird, self).__init__(source='atlas://images/bird_anim/wing-up', pos=pos, **kwargs)
        self.velocity_y = 0
        self.gravity = -.3

    def update(self):
        self.velocity_y += self.gravity
        self.velocity_y = max(self.velocity_y, -10)
        self.y += self.velocity_y
        if self.velocity_y < -5:
            self.source = 'atlas://images/bird_anim/wing-up'
        elif self.velocity_y < 0:
            self.source = 'atlas://images/bird_anim/wing-mid'

    def on_touch_down(self, touch):
        self.velocity_y = 5.5
        self.source = 'atlas://images/bird_anim/wing-down'
        sfx_flap.play()


class Ground(Sprite):
    def update(self):
        self.x -= 2
        if self.x < -24:
            self.x += 24


class Pipe(Widget):
    def __init__(self, pos, **kwargs):
        super(Pipe, self).__init__(pos=pos, **kwargs)
        self.top_image = Sprite(source='images/pipe_top.png')
        self.top_image.pos = (self.x, self.y + 3.5 * 24)
        self.add_widget(self.top_image)
        self.bottom_image = Sprite(source='images/pipe_bottom.png')
        self.bottom_image.pos = (self.x, self.y - self.bottom_image.height)
        self.add_widget(self.bottom_image)
        self.width = self.top_image.width
        self.scored = False

    def update(self):
        self.x -= 2
        self.top_image.x = self.bottom_image.x = self.x
        if self.right < 0:
            self.parent.remove_widget(self)


class Pipes(Widget):
    add_pipe = 0

    def update(self, dt):
        for child in list(self.children):
            child.update()
        self.add_pipe -= dt
        if self.add_pipe < 0:
            y = random.randint(self.y + 50, self.height - 50 - 3.5 * 24)
            self.add_widget(Pipe(pos=(self.width, y)))
            self.add_pipe = 1.5


class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.background = Background(source='images/background.png')
        self.size = self.background.size
        self.add_widget(self.background)
        self.ground = Ground(source='images/ground.png')
        self.pipes = Pipes(pos=(0, self.ground.height), size=self.size)
        self.add_widget(self.pipes)
        self.add_widget(self.ground)
        self.score_label = Label(center_x=self.center_x,
                                 top=self.top - 30,
                                 text='0')
        self.add_widget(self.score_label)
        self.over_label = Label(center=self.center,
                                opacity=0,
                                text='Game Over')
        self.add_widget(self.over_label)
        self.bird = Bird(pos=(20, self.height / 2))
        self.add_widget(self.bird)
        Clock.schedule_interval(self.update, 1.0/60.0)
        self.game_over = False
        self.score = 0

    def update(self, dt):
        if self.game_over:
            return

        self.background.update()
        self.bird.update()
        self.ground.update()
        self.pipes.update(dt)

        if self.bird.collide_widget(self.ground):
            self.game_over = True

        for pipe in self.pipes.children:
            if not pipe.scored and pipe.right < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.score_label.text = str(self.score)
                sfx_score.play()
            if pipe.top_image.collide_widget(self.bird):
                self.game_over = True
            elif pipe.bottom_image.collide_widget(self.bird):
                self.game_over = True

        if self.game_over:
            sfx_die.play()
            self.over_label.opacity = 1
            self.bind(on_touch_down=self._on_touch_down)

    def _on_touch_down(self, instance, value):
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(Menu())


class Menu(Widget):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.add_widget(Sprite(source='images/background.png'))
        self.size = self.children[0].size
        self.add_widget(Ground(source='images/ground.png'))
        self.add_widget(Label(center=self.center,
                              text = 'Tap to start'))

    def on_touch_down(self, touch):
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(Game())


class GameApp(App):
    def build(self):
        top = Widget()
        top.add_widget(Menu())
        return top


if __name__ == '__main__':
    GameApp().run()
