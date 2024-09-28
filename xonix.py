import random
import tkinter
from PIL import Image, ImageDraw

# Направления движения
DIRECTION_LEFT = 'Left'
DIRECTION_RIGHT = 'Right'
DIRECTION_UP = 'Up'
DIRECTION_DOWN = 'Down'
DIRECTION_SPACE = 'space'# Пробел для перезапуска

DIRECTIONS_HORIZONTAL = (DIRECTION_RIGHT, DIRECTION_LEFT)
DIRECTIONS_VERTICAL = (DIRECTION_UP, DIRECTION_DOWN)
DIRECTIONS_ALL = DIRECTIONS_HORIZONTAL + DIRECTIONS_VERTICAL

# Размеры игрового поля и блоков
VISIBLE_WIDTH = 15 * 2  # Видимая часть игрового поля
VISIBLE_HEIGHT = 15 * 2  # Видимая часть игрового поля
BLOCK_SIZE = 25

# Добавляем по одному блоку за пределы экрана (2 блока по ширине и высоте)
FIELD_WIDTH = VISIBLE_WIDTH + 2
FIELD_HEIGHT = VISIBLE_HEIGHT + 2

GAME_SPEED = 1000 // 15  # Начальная скорость игры

# Цвета
COLORS = {
    'PLAYER_HEAD': '#e58d51',
    'TRACE': '#FFFF00',  # Цвет следа
    'FIELD': '#37474f',
    'FIELD_LINE': '#3a4c54',
    'MESSAGE_TEXT': '#ffffff',
    'MESSAGE_BACKGROUND': '#000000',
    'CAPTURED_AREA': '#00FF00',
    'ENEMY': '#8B0000',  # Цвет врага
}

class Player:
    def __init__(self, field_width, field_height):
        self.field_width = field_width #заданный размер игрового поля
        self.field_height = field_height
        self.head = (VISIBLE_WIDTH // 2 + 1, VISIBLE_HEIGHT // 2 + 1)  # Центр видимой области
        self.area = set()  # Захваченная область
        self.trace = []  # След игрока
        self._direction = None  # Направление будет задано игроком позже
        self.started = False  # Флаг начала игры
        self.init_area()

    def init_area(self):
        """
        Инициализация изначальной области вокруг головы
        """
        x, y = self.head
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.area.add((x + dx, y + dy))

    def set_direction(self, direction):
        """
        Устанавливаем направление движения
        """
        if self._direction is None:  # Начинаем движение при первой клавише
            self._direction = direction
        else:
            new_direction = direction
            old_direction = self._direction
            if new_direction in DIRECTIONS_HORIZONTAL and old_direction not in DIRECTIONS_HORIZONTAL:
                self._direction = new_direction
            elif new_direction in DIRECTIONS_VERTICAL and old_direction not in DIRECTIONS_VERTICAL:
                self._direction = new_direction

    def move(self):
        """
        Движение головы игрока по полю
        """
        #Если направление не задано, игрок остается на месте
        if not self.started and self._direction is not None:
            self.started = True

        # Если направление движения не установлено, игрок стоит на месте
        if self._direction is None:
            return

        # Добавляем текущую позицию головы в след, если она не в захваченной области
        if self.head not in self.area and self.head not in self.trace:
            self.trace.append(self.head)
        #Измените положение игрока в зависимости от направления
        head = self.head
        if self._direction == DIRECTION_LEFT:
            head = (head[0] - 1, head[1])
        elif self._direction == DIRECTION_RIGHT:
            head = (head[0] + 1, head[1])
        elif self._direction == DIRECTION_UP:
            head = (head[0], head[1] - 1)
        elif self._direction == DIRECTION_DOWN:
            head = (head[0], head[1] + 1)

        self.head = head

    def is_bump(self):
        """
        Проверка столкновений с краями поля и с самим следом.
        Ограничиваем движение игрока в пределах видимой области.
        """
        x, y = self.head
        if not (1 <= x < self.field_width - 1 and 1 <= y < self.field_height - 1):
            return True
        if self.head in self.trace and self.head not in self.area:
            return True
        return False

    def close_loop(self):
        """
        Если игрок замыкает след в свою захваченную область,
        вся замкнутая область захватывается и заливается.
        """
        if self.started and self.head in self.area:
            # Добавляем след в захваченную область
            self.area.update(self.trace)
            self.flood_fill()  # Запускаем заливку

    def flood_fill(self):
        """
        Используем Pillow для определения замкнутой области и её заливки.
        """
        #Создаём новое изображение с теми же размерами, что и игровое поле
        img = Image.new('L', (self.field_width, self.field_height), 255)
        draw = ImageDraw.Draw(img)
        #рисуем область и обводим контур на изображении
        for x, y in self.area:
            draw.point((x, y), fill=0)

        for x, y in self.trace:
            draw.point((x, y), fill=0)

        ImageDraw.floodfill(img, xy=(0, 0), value=12)

        for x in range(self.field_width):
            for y in range(self.field_height):
                if img.getpixel((x, y)) != 12:
                    self.area.add((x, y))

        self.trace.clear()

class Enemy:
    def __init__(self, field_width, field_height, player):
        self.field_width = field_width
        self.field_height = field_height
        self.position = (random.randint(1, field_width - 2), random.randint(1, field_height - 2))  # Только внутри видимой области
        self.direction = random.choice(DIRECTIONS_ALL)
        self.player = player  # Ссылка на игрока
        self.change_direction_counter = random.randint(5, 15)  # Начальное значение

    def move(self):
        """
        Движение врага с максимальной случайностью
        """
        if self.change_direction_counter <= 0:
            self.direction = random.choice(DIRECTIONS_ALL)
            self.change_direction_counter = random.randint(5, 15)

        dx, dy = 0, 0
        if self.direction == DIRECTION_LEFT:
            dx = -1
        elif self.direction == DIRECTION_RIGHT:
            dx = 1
        elif self.direction == DIRECTION_UP:
            dy = -1
        elif self.direction == DIRECTION_DOWN:
            dy = 1

        new_position = (self.position[0] + dx, self.position[1] + dy)

        if (1 <= new_position[0] < self.field_width - 1 and
            1 <= new_position[1] < self.field_height - 1 and
            new_position not in self.player.area):
            self.position = new_position
        else:
            self.direction = random.choice(DIRECTIONS_ALL)

        self.change_direction_counter -= 1

class Game:
    def __init__(self, master, field_width=FIELD_WIDTH, field_height=FIELD_HEIGHT, block_size=BLOCK_SIZE):
        self.master = master
        self.field_width = field_width
        self.field_height = field_height
        self.block_size = block_size
        self.canvas = tkinter.Canvas(master, width=(field_width - 2) * block_size, height=(field_height - 2) * block_size)
        self.canvas.pack()
        master.bind('<KeyPress>', self.key_press)
        self.is_stop = True
        self.pressed_key = None
        self.update_id = None
        self.score = 0
        self.game_speed = GAME_SPEED
        self.is_game_over = False  # Флаг окончания игры

    def initialize(self):
        self.pressed_key = None
        self.player = Player(field_width=self.field_width, field_height=self.field_height)
        self.enemies = [Enemy(self.field_width, self.field_height, self.player) for _ in range(1)]  # Передаем игрока
        self.score = 0
        self.game_speed = GAME_SPEED
        self.is_game_over = False

    def restart(self):
        if self.update_id is not None:
            self.master.after_cancel(self.update_id)

        self.initialize()
        self.is_stop = False
        self.update()

    def start(self):
        self.initialize()
        self.is_stop = False
        self.update()

    def update(self):
        if not self.is_stop and not self.is_game_over:
            if self.pressed_key:
                self.player.set_direction(self.pressed_key)

            self.player.move()

            if self.player.is_bump():
                self.game_over()
                return

            # Проверка замыкания и захват врагов
            self.player.close_loop()

            # Удаление врагов, если они находятся в захваченной области
            for enemy in self.enemies[:]:
                if enemy.position in self.player.area:
                    self.enemies.remove(enemy)  # Удаляем врага из игры
                    self.score += 1  # Увеличиваем счет
                else:
                    enemy.move()
                    if enemy.position in self.player.trace or enemy.position == self.player.head:
                        self.game_over()
                        return

            if len(self.enemies) == 0:  # Если все враги убиты
                self.is_game_over = True
                self.show_message("Вы победили! Нажмите пробел для рестарта.")
                return

            self.draw()
            self.update_id = self.master.after(self.game_speed, self.update)


    def draw(self):
        self.canvas.delete(tkinter.ALL)
        block_size = self.block_size

        # Рисуем фон игрового поля
        for x in range(self.field_width - 2):
            for y in range(self.field_height - 2):
                fill_color = COLORS['FIELD'] if (x + y) % 2 == 0 else COLORS['FIELD_LINE']
                self.canvas.create_rectangle(x * block_size, y * block_size,
                                            (x + 1) * block_size, (y + 1) * block_size,
                                            outline=fill_color, fill=fill_color)

        # Отрисовка захваченной области
        for x, y in self.player.area:
            self.canvas.create_rectangle((x - 1) * block_size, (y - 1) * block_size,
                                        x * block_size, y * block_size,
                                        outline=COLORS['FIELD_LINE'], fill=COLORS['CAPTURED_AREA'])

        # Отрисовка следа игрока
        for x, y in self.player.trace:
            self.canvas.create_rectangle((x - 1) * block_size, (y - 1) * block_size,
                                        x * block_size, y * block_size,
                                        outline=COLORS['TRACE'], fill=COLORS['TRACE'])

        # Отрисовка головы игрока
        x, y = self.player.head
        self.canvas.create_rectangle((x - 1) * block_size, (y - 1) * block_size,
                                    x * block_size, y * block_size,
                                    outline=COLORS['PLAYER_HEAD'], fill=COLORS['PLAYER_HEAD'])

        # Отрисовка врагов
        for enemy in self.enemies:
            ex, ey = enemy.position
            self.canvas.create_oval((ex - 1) * block_size, (ey - 1) * block_size,
                                    ex * block_size, ey * block_size,
                                    outline=COLORS['ENEMY'], fill=COLORS['ENEMY'])

    def key_press(self, event):
        #Проверка, закончена ли игра и нажат ли пробел
        if self.is_game_over and event.keysym == DIRECTION_SPACE:
            self.restart()
        elif event.keysym in DIRECTIONS_ALL:
            self.pressed_key = event.keysym

    def game_over(self):
        self.is_stop = True
        self.is_game_over = True
        self.show_message("Вы проиграли, нажмите пробел для рестарта.")

    def show_message(self, text):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.create_rectangle(width // 8, height // 4, width // 8 * 7, height // 4 * 3, fill=COLORS['MESSAGE_BACKGROUND'])
        self.canvas.create_text(width // 2, height // 2, fill=COLORS['MESSAGE_TEXT'], text=text, font=("Helvetica", 24))

def main():
    root = tkinter.Tk()
    game = Game(root)
    game.start()
    root.mainloop()

if __name__ == '__main__':
    main()
