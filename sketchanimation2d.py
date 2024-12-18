import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import uic
import cv2
import os
from timeline import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/main.ui", self)
        # может принимать перекидывание файлов
        self.setAcceptDrops(True)
        self.setFixedSize(1000, 700)
        # окно создани я нового холста есть?
        self.okno = False
        # История сохранений - хранит предыдущие картинки (для отмены или при рисовании/отображение фигур)
        self.cahe = []
        # будущее название файла
        self.save_name = 0
        # выбранный инструмент
        self.tool = "kist"
        # толщина кисти
        self.nac = 10
        # прозрачность кисти
        self.alpha = 100
        # пипетка - пока True может брать цвет (пока зажата ПКМ)
        self.tr = False
        # использовать возможности графического планшета? (если True то меняет толщину при нажиме/ иначе False с подключенный планшетом соровно толщина меняться не будет)
        self.widtr = True
        # координаты холста
        self.coord = (600, 350)
        
        # Параметры для регулирования заливки (при выбранном инструменте заливка - появляются её параметры)
        # ползунок - радиус заливки (на сколько сильно тот закрасит окружающие области)
        self.slider_floodfill_koff.setVisible(False)
        # радиус заливки, который можно изменить написав самому значение
        self.spinBox_2.setVisible(False)
        
        # QLabel основа для создания холста
        self.label = QLabel(self)
        # Даём ему размеры холста
        self.label.resize(*self.coord)
        # создаём холст - QPixmap
        canvas = QPixmap(*self.coord)
        # даём белый фон
        canvas.fill(Qt.GlobalColor.white)
        # помещаем для отображения холста в QLabel
        self.label.setPixmap(canvas)
        # QLabel отодвигаем от инструментов
        self.dvig = 140, 60
        self.label.move(self.dvig[0], self.dvig[1])
        # делаем белый фон и для QLabel (это если в будущем появится возможность сохранять с прозрачностью, но для удобства фон белый для пользователя)
        self.label.setStyleSheet("background-color: white;")
        # основа для хоста - для отображения толщины кисти
        self.label_wid = QLabel(self)
        self.label_wid.resize(110, 110)
        # создаём холст для отображения толщины кисти
        canvas2 = QPixmap(110, 110)
        canvas2.fill(Qt.GlobalColor.white)
        self.label_wid.setPixmap(canvas2)
        # перемщаем вниз от инструментов
        self.label_wid.move(0, 250)
        # прошлое движение мыши (например инструмента для линии)
        self.xy_past = 0
        # при выходе если картина изменена и не сохранена, то предложит сохранится
        self.exit = True
        # можно рисовать с регулированной планшетом толщиной
        self.plansh = False
        # позиция в истори хранения картинов
        self.index_img = -1
        # изначальный цвет для кисти - чёрный
        self.pen_color = QColor(255, 50, 100, self.alpha)
        # создаётся картинка и сохраняется временно time_file.png, чтобы сохранить отдельно данные картинки в cv_img
        image = self.label.pixmap().toImage()
        image.save("time_file.png")
        cv_img = cv2.imread("time_file.png")
        self.cahe += [cv_img]
        # удаляем ненужный файл
        os.remove("time_file.png")
        # даём характеристики кистям для их рисования - цвет, 
        self.p_fig = QPen(self.pen_color, self.nac, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin)
        self.b = QPen(self.pen_color, self.nac, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.RoundJoin)
        self.p = QPen(self.pen_color, self.nac, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        # добавление таймлайна
        self.timel = TimeLine(parent=self)
        self.timel.setGeometry(80, 520, self.timel.w, self.timel.h)
        self.timel.addFrame(1, self.label.pixmap())
        self.timel.checkFrame(1, True)
        
        self.pathsave = "save"
        self.path = "save"
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.nowframe = 1
        self.fileUpdate()
        
        # горячие клавиши к кнопкам/функциям
        self.spinBox.valueChanged.connect(self.spin_move)
        self.slider_width.valueChanged.connect(self.slider_move)
        self.spinBox_alp.valueChanged.connect(self.spin_move_alp)
        self.slider_alpha.valueChanged.connect(self.slider_move_alp)
        self.spinBox_2.valueChanged.connect(self.spin_move_fill)
        self.slider_floodfill_koff.valueChanged.connect(self.slider_move_fill)
        self.btn_setcolor.clicked.connect(self.color_cast)
        self.btn_setcolor.setShortcut(QKeySequence("Ctrl+G"))
        self.act_save_folder.setShortcut(QKeySequence("Ctrl+S"))
        self.act_saveas_folder.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.act_add_holst.setShortcut(QKeySequence("Ctrl+N"))
        self.act_folder.setShortcut(QKeySequence("Ctrl+O"))
        self.act_save_folder.triggered.connect(self.save_folder)
        self.act_saveas_folder.triggered.connect(self.saveas_folder)
        self.act_add_holst.triggered.connect(self.open_add_form)
        self.act_folder.triggered.connect(self.openFolder)
        self.act_saveas.triggered.connect(self.saveas_cast)
        self.act_export.triggered.connect(self.exportVideo)
        self.act_wpentab.triggered.connect(self.widthpentablet_cast)
        self.act_open.triggered.connect(self.opened_new)
        self.btn_nonepen.clicked.connect(self.pen_nothing)
        self.btn_nonepen.setShortcut(QKeySequence("Ctrl+U"))
        self.btn_brush.clicked.connect(lambda sel, x="kist": self.tool_cast(x))
        self.btn_brush.setShortcut(QKeySequence("Ctrl+B"))
        self.btn_pen.clicked.connect(lambda sel, x="pen": self.tool_cast(x))
        self.btn_pen.setShortcut(QKeySequence("Ctrl+P"))
        self.btn_square.clicked.connect(lambda sel, x="kvad": self.tool_cast(x))
        self.btn_square.setShortcut(QKeySequence("Ctrl+K"))
        self.btn_arc.clicked.connect(lambda sel, x="arc": self.tool_cast(x))
        self.btn_arc.setShortcut(QKeySequence("Ctrl+A"))
        self.btn_line.clicked.connect(lambda sel, x="line": self.tool_cast(x))
        self.btn_line.setShortcut(QKeySequence("Ctrl+L"))
        self.btn_floodfill.clicked.connect(lambda sel, x="zaliv": self.tool_cast(x))
        self.btn_floodfill.setShortcut(QKeySequence("Ctrl+F"))
        self.shcut1 = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.shcut1.activated.connect(self.last)
        self.shcut2 = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shcut2.activated.connect(self.past)
        
        # регулирует толщину [ - уменьшает  ] - увеличивает
        self.shcut3 = QShortcut(QKeySequence("]"), self)
        self.shcut3.activated.connect(self.up)
        self.shcut3.activated.connect(lambda s=self, x="]":  s.labelEvent.setText(x))
        self.shcut4 = QShortcut(QKeySequence("["), self)
        self.shcut4.setKey(Qt.Key.Key_BracketLeft)
        self.shcut4.activated.connect(self.down)
        self.shcut4.activated.connect(lambda s=self, x="[":  s.labelEvent.setText(x))
        self.shcut5 = QShortcut(QKeySequence("9"), self)
        self.shcut5.activated.connect(self.timel.minusDur)
        self.shcut5.activated.connect(lambda s=self, x="9":  s.labelEvent.setText(x))
        self.shcut6 = QShortcut(QKeySequence("0"), self)
        self.shcut6.activated.connect(self.timel.plusDur)
        self.shcut6.activated.connect(lambda s=self, x="0":  s.labelEvent.setText(x))
        
        self.cur = [0, 0]
        self.isctrl = False
        self.x_past = None
        
        self.isplay = False
        self.pausef = None
        
        # для смены кадров в будущем за QTimeLine - таймер линейный (короче кривая может быть)
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.finplay)
        self.timeline.frameForTime(int(1000/self.timel.fps))
        self.timeline.setStartFrame(0)
        self.timeline.setEndFrame(1)
        self.slider_and_spin(10)
        self.initUI()
        
    def initUI(self):
        self.setWindowIcon(QIcon("icona.ico"))
        self.setWindowTitle("SketchAnimation2D")
        self.show()
        
    def startPlay(self, at=0):
        self.at = at
        self.timeline.setStartFrame(at)
        mxn = max(self.timel.frames)
        end = self.timel.frames[mxn].num + self.timel.frames[mxn].duration - 2
        self.timeline.setEndFrame(end)
        self.timeline.setDuration(int(end / 24 * 1000))
        self.timeline.frameForTime(int(1000/self.timel.fps))
        
        self.isplay = True
        self.timeline.finished.connect(self.finplay)
        self.timeline.setLoopCount(10)
        self.timeline.start()
        

    def finplay(self):
        self.isplay = False
        self.nowframe = self.at + 1
        pic = self.timel.frames[self.at + 1].picture
        if pic:
            self.label.setPixmap(pic)
        self.update()

    def animate(self, value):
        mxn = max(self.timel.frames)
        end = self.timel.frames[mxn].num + self.timel.frames[mxn].duration - 2
        time = value * self.timel.fps * (self.timeline.duration() / 1000)
        f = self.timel.inBetweenFrame((time + self.at + 1) % end)
        self.pausef = f
        if f:
            self.label.setPixmap(self.timel.frames[f].picture)
            self.update()
        
    def up(self):
        self.nac += 1
        self.slider_and_spin(self.nac)
        
    def down(self):
        if self.nac > 0:
            self.nac -= 1
            self.slider_and_spin(self.nac)

    # возможность перетаскивания файлов - состояние когда файл ещё передвигается
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # состояние когда файл уже отпустили - создаём новый холст с изображением
    def dropEvent(self, event):
        # получаем ссылки передащенных файлов
        url = event.mimeData().urls()
        if len(url) == 1:
            # если несколько файлов - то выбрается только последний из них
            self.opened_new(url[-1].toLocalFile())
            self.update()
                
    def fileUpdate(self, file : str | None = None):
        fl = self.pathsave
        if file:
            fl = file.rstrip("/")
        for filename in os.listdir(fl):
            os.remove(fl + "/" + filename)  
        for k in sorted(self.timel.frames):
            frs = self.timel.frames[k]
            frs.picture.save(f"{fl}/frame-{frs.num}_dur-{frs.duration}.png", "PNG")
        
    def loadFile(self, path):
        self.timel.clear()
        self.path = path
        for filename in sorted(os.listdir(self.path), key=lambda x: int(x[:-4].split("_")[0].split("-")[1])):
            fr, dur = filename[:-4].split("_")
            fr = int(fr.split("-")[1])
            dur = int(dur.split("-")[1])
            self.opened_new(self.path + "/" + filename)
            self.timel.addFrame(fr, self.label.pixmap())
            self.timel.setFrameDur(fr, dur)
        self.timel.checkFrame(1, True)
        self.nowframe = 1
        fram = self.timel.selectedframe
        self.label.setPixmap(fram.picture)
 
    # взаимодействие с графическим планшетом (почти тоже самое, что и мышь, только с функциональностями планшета)
    def tabletEvent(self, tabletEvent):
        # координата мыши (стилуса)
        x, y = int(tabletEvent.position().x()), int(tabletEvent.position().y())
        # если за холстом - то действия игнорируются
        if (x - self.dvig[0] < 0 or x - self.dvig[0] >= self.coord[0]
            or y - self.dvig[1] < 0 or y - self.dvig[1] > self.coord[1]) or self.isplay:
            return
        
        self.exit = False
        print(tabletEvent.isEndEvent(), tabletEvent.isInputEvent())
        if tabletEvent.buttons() == Qt.MouseButton.NoButton:
            if tabletEvent.isEndEvent():
                if self.index_img + 1 < 0:
                    # срез (убирает лишнее изображения) | каждое новое действие обнуляет все будущие
                    self.cahe = self.cahe[:self.index_img + 1]
                    self.index_img = -1
                if self.index_img < 0:
                    self.index_img = -1
                # сохраняем картнику с холста в cv_img и добавляем в историю сохранения 
                image = self.label.pixmap().toImage()
                image.save("time_file.png")
                cv_img = cv2.imread("time_file.png")
                self.cahe += [cv_img]
                os.remove("time_file.png")
                print(len(self.cahe))
        # если нажата/зажата ЛКМ
        if tabletEvent.buttons() == Qt.MouseButton.LeftButton:
            if tabletEvent.isBeginEvent():
                self.xy_past = 0
            # выбраны инструменты - кисть, ручка и ластик (для остальных инструментов применяются действия для мыши)
            if self.tool in ["pen", "kist", "last"]:
                # планшет - рисует
                self.plansh = True
                # соотношение для толщины (нажим/сила стилуса)
                self.pen_pressure = int(tabletEvent.pressure() * 100)
                tabletEvent.accept()
                # если нету координат прошлого события, то даём нынешний
                if self.xy_past == 0:
                    self.xy_past = (int(tabletEvent.position().x()), int(tabletEvent.position().y()))
                # окрываем холст
                pm = self.label.pixmap()
                # Для рисования применяется QPainter
                painter = QPainter(pm)
                # если можно использовать возможности планшета то применяем силу стилуса, иначе рисуется как обычной мышью
                if self.widtr:
                    self.p.setWidth(int(self.nac * self.pen_pressure / 100))
                    self.b.setWidth(int(self.nac * self.pen_pressure / 100))
                    self.p_fig.setWidth(int(self.nac * self.pen_pressure / 100))
                else:
                    self.p_fig.setWidth(self.nac)
                    self.p.setWidth(self.nac)
                    self.b.setWidth(self.nac)
                # если кисть или карандашь, то применяются их характеристики и даётся им цвет
                if self.tool == "kist":
                    painter.setPen(self.b)
                    self.b.setColor(self.pen_color)
                    self.p.setColor(self.pen_color)
                elif self.tool == "pen":
                    painter.setPen(self.p)
                    self.b.setColor(self.pen_color)
                    self.p.setColor(self.pen_color)
                elif self.tool == "last":
                    # у ластика всегда белый цвет - характеристики ручки
                    painter.setPen(self.p)
                # создаётся не точка, а линия чтобы гладко линия перетякала при рисовании (а то при рисовании буду образоваться прорези вместо гладких линий)
                painter.drawLine(self.xy_past[0] - self.dvig[0], self.xy_past[1] - self.dvig[1], int(tabletEvent.position().x()) - self.dvig[0], int(tabletEvent.position().y()) - self.dvig[1])
                painter.end()
                # даём новые данные для холста
                self.label.setPixmap(pm)
                # сохраняем предыдущую координату (после обработки)
                self.xy_past = (int(tabletEvent.position().x()), int(tabletEvent.position().y()))
                # даём заданнаю толщину (это при случаи если переключатся обратно к мыши)
                self.p.setWidth(self.nac)
                self.b.setWidth(self.nac)
                self.p_fig.setWidth(self.nac)
                self.update()
        elif tabletEvent.buttons() == Qt.MouseButton.RightButton:
            self.tr = True
 
    # первое нажатие мыши
    def mousePressEvent(self, e):
        x, y = int(e.position().x()), int(e.position().y())
        if e.buttons() == Qt.MouseButton.MiddleButton:
            self.cur[0] = x
            self.cur[1] = y
        # нажата ЛКМ
        if e.buttons() == Qt.MouseButton.LeftButton:
            if self.timel.checkFrameM(x, y, True):
                if self.isplay:
                    self.timeline.setPaused(True)
                    if self.pausef:
                        self.nowframe = self.pausef
                        self.timel.checkFrame(self.pausef)
                        fram = self.timel.selectedframe
                        self.label.setPixmap(fram.picture)
                    self.isplay = False
                else:
                    self.pausef = None
                    self.isplay = False
                    self.timel.frames[self.nowframe].setPic(self.label.pixmap())
                    fram = self.timel.selectedframe
                    self.label.setPixmap(fram.picture)
                    self.nowframe = fram.num
                    self.cahe.clear()
                    image = self.label.pixmap().toImage()
                    image.save("time_file.png")
                    cv_img = cv2.imread("time_file.png")
                    self.cahe += [cv_img]
                    # удаляем ненужный файл
                    os.remove("time_file.png")
                    self.fileUpdate()
            else:
                self.timel.addFrameM(x, y, self.label.pixmap())
            self.update()
                
        if e.buttons() == Qt.MouseButton.RightButton and self.isctrl:
            self.timel.fillFrames()
            self.update()
        
        if (x - self.dvig[0] < 0 or x - self.dvig[0] >= self.coord[0]
            or y - self.dvig[1] < 0 or y - self.dvig[1] > self.coord[1]) or self.isplay:
            return
        self.exit = False
        
        # нажата ЛКМ
        if e.buttons() == Qt.MouseButton.LeftButton:
            if self.tool in ["pen", "kist", "last"]:
                if not(self.plansh):
                    pm = self.label.pixmap()
                    painter = QPainter(pm)
                    self.p.setColor(self.pen_color)
                    self.b.setColor(self.pen_color)
                    self.p.setWidth(self.nac)
                    self.b.setWidth(self.nac)
                    
                    if self.tool == "kist":
                        painter.setPen(self.b)
                    elif self.tool == "pen":
                        painter.setPen(self.p)
                    # создаётся только точка в месте мыши
                    painter.drawPoint(x - self.dvig[0], y - self.dvig[1])
                    painter.end()
                    self.label.setPixmap(pm)
                    # сохраняем координаты для будущих действий зажатой мыши/стилуса
                    self.xy_past = (x, y)
            elif self.tool in ["line", "kvad", "arc"]:
                # при клике не создаёт фигуру/точку только сохраняет координаты мыши и даёт новый индекс истории сохранения для фигуры
                if not(self.plansh):
                    self.xy_past = (x, y)
                if self.index_img + 1 < 0:
                    # срез (убирает лишнее изображения) | каждое новое действие обнуляет все будущие
                    self.cahe = self.cahe[:self.index_img + 1]
                    self.index_img = -1
                # всегда текущий -1
                if self.index_img < 0:
                    self.index_img = -1
            elif self.tool == "zaliv":
                # заливка - заполняет область функцией Floodyfill_color с данным значением от slider_floodfill_koff
                x, y = x - self.dvig[0], y - self.dvig[1]
                self.Floodyfill_color(x, y, self.pen_color.getRgb(), self.slider_floodfill_koff.value())
        elif e.buttons() == Qt.MouseButton.RightButton:
            self.tr = True

    # пока мышь двигается
    def mouseMoveEvent(self, e):
        # берём координату мыши
        x, y = int(e.position().x()), int(e.position().y())
        
        if e.buttons() == Qt.MouseButton.MiddleButton and self.isctrl:
            if self.x_past:
                
                self.timel.rightScrollx(x - self.x_past)
                self.update()
            self.x_past = x
            
        if (x - self.dvig[0] < 0 or x - self.dvig[0] >= self.coord[0]
            or y - self.dvig[1] < 0 or y - self.dvig[1] > self.coord[1]) or self.isplay:
            return
        self.exit = False

        if e.buttons() == Qt.MouseButton.LeftButton:
            # те же действия, что и у плашета, только без изменения толщины
            if self.tool in ["pen", "kist", "last"]:
                if not(self.plansh):
                    self.p.setWidth(self.nac)
                    self.b.setWidth(self.nac)
                    self.p_fig.setWidth(self.nac)
                    if self.xy_past == 0:
                        self.xy_past = (x, y)
                    pm = self.label.pixmap()
                    painter = QPainter(pm)
                    if self.tool == "kist":
                        painter.setPen(self.b)
                        self.p.setColor(self.pen_color)
                        self.b.setColor(self.pen_color)
                    elif self.tool == "pen":
                        painter.setPen(self.p)
                        self.p.setColor(self.pen_color)
                        self.b.setColor(self.pen_color)
                    elif self.tool == "last":
                        painter.setPen(self.p)
                    painter.drawLine(self.xy_past[0] - self.dvig[0], self.xy_past[1] - self.dvig[1], x - self.dvig[0], y - self.dvig[1])
                    painter.end()
                    self.label.setPixmap(pm)
                    self.xy_past = (x, y)
                # отключаем планшет (при случае если планшет перестанет использоваться)
                self.plansh = False
            elif self.tool in ["line", "kvad", "arc"]:
                # инструменты - фигуры работают
                if not(self.plansh):
                    # если есть будущие кадры, стераим их
                    if self.index_img != -1:
                        # если ещё пользователь фигуру не отпутил, то возвращаем до рисования фигуры холст (чтобы не было много фигур при зажатой мыши)
                        self.index_img = -1
                        self.past()
                    else:
                        # если -1 то значит будущих нет в истории, то достаточно вернуться назад
                        image = self.label.pixmap().toImage()
                        image.save("time_file.png")
                        cv_img = cv2.imread("time_file.png")
                        # добавляем в историю предыдущих действий
                        self.cahe += [cv_img]
                        os.remove("time_file.png")
                    self.index_img = -1
                    # создаёт временные изменения с фигурой для демострации (но не сохраняем в холст, т.к. пользователь ещё ищет где-бы отпусть линию)
                    pm = self.label.pixmap()
                    painter = QPainter(pm)
                    self.past()
                    painter.setPen(self.p_fig)
                    self.p_fig.setColor(self.pen_color)
                    # создаёт прямоугольник от прошлой координаты к нынешней
                    if self.tool == "kvad":
                        p1 = (self.xy_past[0] - self.dvig[0], self.xy_past[1] - self.dvig[1])
                        p2 = (x - self.dvig[0], y - self.dvig[1])
                        painter.drawRect(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
                    elif self.tool == "line":
                        # создаёт линию от прошлой координаты к нынешней
                        p1 = (self.xy_past[0] - self.dvig[0], self.xy_past[1] - self.dvig[1])
                        p2 = (x - self.dvig[0], y - self.dvig[1])
                        painter.drawLine(p1[0], p1[1], p2[0], p2[1])
                    elif self.tool == "arc":
                        # создаёт эллипс от прошлой координаты к нынешней 
                        self.p.setColor(self.pen_color)
                        painter.setPen(self.p)
                        p1 = (self.xy_past[0] - self.dvig[0], self.xy_past[1] - self.dvig[1])
                        p2 = (x - self.dvig[0], y - self.dvig[1])
                        painter.drawEllipse(p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])
                    painter.end()
                    # сохраняем холст для демострации
                    self.label.setPixmap(pm)       
                self.plansh = False

    # мышь была отпущенна
    def mouseReleaseEvent(self, e):
        x, y = int(e.position().x()), int(e.position().y())
        self.x_past = None
        if (x - self.dvig[0] < 0 or x - self.dvig[0] >= self.coord[0]
            or y - self.dvig[1] < 0 or y - self.dvig[1] > self.coord[1]) or self.isplay:
            return
        self.exit = False
        self.timel.frames[self.nowframe].setPic(self.label.pixmap())
        # применяем пипетку если она была включенна (была нажата ПКМ)
        if self.tr:
            x, y = int(e.position().x()) - self.dvig[0], int(e.position().y() - self.dvig[1])
            # берём цвет с холста
            color = QColor(self.label.pixmap().toImage().pixel(x, y)).getRgb()
            # сохраняем новый цвет
            self.pen_color = QColor(*color)
            self.pen_color.setAlpha(self.alpha)
            # выключаем пипетку
            self.tr = False
            return
        if self.index_img + 1 < 0:
            # срез (убирает лишнее изображения) | каждое новое действие обнуляет все будущие
            self.cahe = self.cahe[:self.index_img + 1]
            self.index_img = -1
        if self.index_img < 0:
            self.index_img = -1
        # сохраняем картнику с холста в cv_img и добавляем в историю сохранения 
        image = self.label.pixmap().toImage()
        image.save("time_file.png")
        cv_img = cv2.imread("time_file.png")
        self.cahe += [cv_img]
        os.remove("time_file.png")
        # обнуляем предыдущие координаты мыши (чтобы при новом нажатии не создавались лишнии линии с предыдущей координаты)
        self.xy_past = 0
        # если авто-сохранение включенно, то сохраняем в отдельный файл
    
    # для прокрутки колёсика мыши
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.timel.rightScrollx(self.timel.widthf)
            self.timel.update()
        else:
            self.timel.leftScrollx(self.timel.widthf)
            self.timel.update()
    
    # нажатие клавиши
    def keyPressEvent(self, e):
        x, y = self.cur[0], self.cur[1]
        if e.key() == Qt.Key.Key_Control:
            self.isctrl = True
            self.x_past = None
            
        if e.key() == Qt.Key.Key_R:
            if self.isplay:
                self.timeline.setPaused(True)
                if self.pausef:
                    self.nowframe = self.pausef
                    self.timel.checkFrame(self.pausef, select=True)
                self.pausef = None
                self.isplay = False
            else:
                self.startPlay(self.nowframe - 1)
            self.update()
                
        if e.key() == Qt.Key.Key_Delete:
            if self.timel.selectedframe:
                fram = self.timel.selectedframe
                if fram.num != 1:
                    self.timel.delFrame(fram.num)
                    self.timel.checkFrame(1, True)
                    self.nowframe = 1
                    self.label.setPixmap(self.timel.frames[self.nowframe].picture)
                    self.update()

        if e.key() == Qt.Key.Key_1:
            f = self.timel.neibFrame(self.nowframe)
            if f and f[0] is not None:
                l = f[0]
                self.timel.checkFrame(l, True)
                self.timel.frames[self.nowframe].setPic(self.label.pixmap())
                fram = self.timel.selectedframe
                self.label.setPixmap(fram.picture)
                self.nowframe = fram.num
                self.cahe.clear()
                image = self.label.pixmap().toImage()
                image.save("time_file.png")
                cv_img = cv2.imread("time_file.png")
                self.cahe += [cv_img]
                # удаляем ненужный файл
                os.remove("time_file.png")
                if self.timel.getStartNumframe() > fram.num:
                    self.timel.leftScrollx((self.timel.getStartNumframe() - fram.num + 1) * 10)
                self.update()
                self.fileUpdate()
                
        if e.key() == Qt.Key.Key_2:
            f = self.timel.neibFrame(self.nowframe)
            if f and f[2] is not None:
                r = f[2]
                self.timel.checkFrame(r, True)
                self.timel.frames[self.nowframe].setPic(self.label.pixmap())
                fram = self.timel.selectedframe
                self.label.setPixmap(fram.picture)
                self.nowframe = fram.num
                self.cahe.clear()
                image = self.label.pixmap().toImage()
                image.save("time_file.png")
                cv_img = cv2.imread("time_file.png")
                self.cahe += [cv_img]
                # удаляем ненужный файл
                os.remove("time_file.png")
                if self.timel.getStartNumframe() + (self.timel.w / self.timel.widthf) < fram.num + fram.duration - 1:
                    self.timel.rightScrollx((fram.num + fram.duration - 1 - (self.timel.getStartNumframe() + (self.timel.w / self.timel.widthf))) * 10)
                self.update()
                self.fileUpdate()
                    
        if e.key() == Qt.Key.Key_A:
            if self.timel.selectedframe and not self.timel.checkFrameM(x, y):
                sl = self.timel.selectedframe
                indsl = sorted(self.timel.frames).index(sl.num) 
                if indsl + 1 < len(self.timel.frames):
                    if self.timel.flo(x) < self.timel.frames[sorted(self.timel.frames)[indsl + 1]].num:
                        self.timel.setFrameDur(sl.num, (self.timel.flo(x) - (sl.num - 1)))
                        self.update()
                else:
                    self.timel.setFrameDur(sl.num, (self.timel.flo(x) - (sl.num - 1)))
                    self.update()

    # разжатие кливиши
    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key.Key_Control:
            self.isctrl = False
            self.x_past = None
    
    # следующее действие (Перемещение по истории сохранений вправа)
    def last(self):
        # проверка диапазона, пока меньше -1 тогда вправа ,иначе -1 то дальше нечего брать
        if self.index_img + 1 < 0:
            # пребавляем 1 к индексу
            self.index_img += 1
            # перемещаемся в нужное место
            cv_img = self.cahe[self.index_img]
            cv2.imwrite("time_file.png", cv_img)
            qu = QImage("time_file.png")
            pix = QPixmap.fromImage(qu)
            # ставим на холст выбранную картинку (следующую)
            self.label.setPixmap(pix)
            os.remove("time_file.png")

    # предыдущее действие (Перемещение по истории сохранений влева)
    def past(self):
        # проверка диапазона, есть ли что-то пока abs(индекс) < длины тогда влева
        if len(self.cahe) > -(self.index_img):
            # вычитаем 1 к индексу
            self.index_img -= 1
            # перемещаемся в нужное место
            cv_img = self.cahe[self.index_img]
            cv2.imwrite("time_file.png", cv_img)
            qu = QImage("time_file.png")
            pix = QPixmap.fromImage(qu)
            # ставим на холст выбранную картинку (прошлую)
            self.label.setPixmap(pix)
            os.remove("time_file.png")
                    

            
    # при нажатии инструмента палитры - выскакивает окно палитры, которая после выбора цвета возвращает цвте
    def color_cast(self):
        color = QColorDialog.getColor()
        # если цвет взялся, то сохраняем
        if color.isValid():
            self.pen_color = QColor(*color.getRgb())
            self.pen_color.setAlpha(self.alpha)
            self.p.setColor(self.pen_color)
            self.b.setColor(self.pen_color)
        # обновляем цвет в холсте с отображением толщины кисти
        self.slider_move()
        
    def save_folder(self):
        if self.save_name == 0:
            # если до этого не сохраняли, то вызывается Сохранить как
            self.saveas_folder()
            if self.save_name == 0:
                return False
        self.timel.frames[self.nowframe].setPic(self.label.pixmap())
        self.fileUpdate(self.save_name)
        self.exit = True
        return True
    
    # сохраняет картинку как... в новую папку
    def saveas_folder(self):
        # окрываем окно с сохранением в проводник
        fille = QFileDialog.getExistingDirectory(None,"Выбрать папку",".")
        # если пусто, то не сохраняем
        if fille == "":
            return False
        # даём название и применяем сохранение
        self.save_name = fille
        self.save_folder()
        self.save_name = fille
        return True
    
    # сохраняет картинку как... в новый файл
    def saveas_cast(self):
        # окрываем окно с сохранением в проводник
        fille = QFileDialog.getSaveFileName(self, 'Выбрать картинку', '',
        'Картинка (*.jpg);;Картинка (*.png);;Картинка (*.bmp);;Все файлы (*)')[0]
        # если пусто, то не сохраняем
        if fille == "":
            return False
        # даём название и применяем сохранение
        self.label.pixmap().save(fille)
        return True
    
    def openFolder(self):
        # окрываем окно с проводником
        fille = QFileDialog.getExistingDirectory(None,"Выбрать папку",".")
        # если пусто, то ничего не делаем
        if fille == "":
            return False
        # даём название
        self.loadFile(fille)
        self.save_name = fille
        return True
    
    def exportVideo(self, file : str | None = None, coder='XVID'):
        fl = None
        if file:
            fl = file.rstrip("/")
        else:
            fl = QFileDialog.getSaveFileName(self, 'Выбрать видео', '',
            'Картинка (*.mp4);;Картинка (*.avi);;Картинка (*.mov);;Все файлы (*)')[0]
        frameSize = (self.label.width(), self.label.height())
        fourcc = cv2.VideoWriter_fourcc(*coder)
        out = cv2.VideoWriter(
            fl, fourcc, self.timel.fps, frameSize
            )
        num = 1
        img = None
        for filename in sorted(os.listdir(self.pathsave), key=lambda x: int(x[:-4].split("_")[0].split("-")[1])):
            fr, dur = filename[:-4].split("_")
            fr = int(fr.split("-")[1])
            dur = int(dur.split("-")[1])
            if fr > num + 1 and img is None:
                for _ in range(fr - num - 1):
                    out.write(img)
            img = cv2.imread(self.pathsave + "/" + filename)
            for _ in range(dur):
                out.write(img)
            num = fr + dur - 1
        out.release()

    # нажатие на параметр сверху с применением возможностей планшета - если вкл то можно выкл, или наоборот
    def widthpentablet_cast(self):
        self.widtr = not(self.widtr)
        text = "Толщина меняется при стилусе"
        # если вкл то добавляет +
        if self.widtr:
            text += "     +"
        self.act_wpentab.setText(text)

    # был нажат инструмент - ластик
    def pen_nothing(self):
        # задаём тип ластика - last
        self.tool = "last"
        pm = self.label.pixmap()
        painter = QPainter(pm)
        # применяем белый цвет
        self.pen_color = QColor(255, 255, 255, self.alpha)
        self.p.setColor(self.pen_color)
        painter.setPen(self.p)
        painter.end()
        self.label.setPixmap(pm)
    
    # применение инструмента
    def tool_cast(self, x):
        self.tool = x
        if x == "zaliv":
            # при заливки - отображаются её параметры \ иначе скрываются
            self.slider_floodfill_koff.setVisible(True)
            self.spinBox_2.setVisible(True)
        else:
            self.slider_floodfill_koff.setVisible(False)
            self.spinBox_2.setVisible(False)
            
    # ползунок толщины - задаёт её значения для толщины кисти
    def slider_move(self):
        self.slider_and_spin(self.slider_width.value())

    # тоже самое и для ввода вручную толщины
    def spin_move(self):
        self.slider_and_spin(self.spinBox.value())

    # ползунок радиуса заливки
    def slider_move_fill(self):
        self.slider_and_spin_fill(self.slider_floodfill_koff.value())

    # тоже самое и для ввода вручную радиуса заливки
    def spin_move_fill(self):
        self.slider_and_spin_fill(self.spinBox_2.value())

    # синхронизация ползунка и ввода для радиуса заливки
    def slider_and_spin_fill(self, k):
        self.spinBox_2.setValue(k)
        self.slider_floodfill_koff.setValue(k)
    
    # ползунок прозрачности
    def slider_move_alp(self):
        self.slider_and_spin_alp(self.slider_alpha.value())

    # тоже самое и для ввода вручную прозрачности
    def spin_move_alp(self):
        self.slider_and_spin_alp(self.spinBox_alp.value())
    
    # синхронизация ползунка и ввода для прозрачности
    def slider_and_spin_alp(self, w):
        self.spinBox_alp.setValue(w)
        self.slider_alpha.setValue(w)
        self.alpha = w
        self.pen_color.setAlpha(w)
        self.p.setColor(self.pen_color)
        self.b.setColor(self.pen_color)
        self.p_fig.setColor(self.pen_color)
        pm2 = self.label_wid.pixmap()
        # рисуем заного белый холст для отображения толщины кисти
        pm2.fill(Qt.GlobalColor.white)
        pen = QPen(self.pen_color, self.nac, Qt.PenStyle.DashDotLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter2 = QPainter(pm2)
        painter2.setPen(pen)
        # ставим по центру одну точку
        painter2.drawPoint(110 // 2, 110 // 2)
        painter2.end()
        # обновляем холст демонтрации толщины кисти
        self.label_wid.setPixmap(pm2)
        
    # синхронизация ползунка и ввода для толщины
    def slider_and_spin(self, w):
        self.p.setWidth(w)
        self.b.setWidth(w)
        self.p_fig.setWidth(w)
        self.nac = w
        pm2 = self.label_wid.pixmap()
        self.spinBox.setValue(w)
        self.slider_width.setValue(w)
        # рисуем заного белый холст для отображения толщины кисти
        pm2.fill(Qt.GlobalColor.white)
        pen = QPen(self.pen_color, w, Qt.PenStyle.DashDotLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter2 = QPainter(pm2)
        painter2.setPen(pen)
        # ставим по центру одну точку
        painter2.drawPoint(110 // 2, 110 // 2)
        painter2.end()
        # обновляем холст демонтрации толщины кисти
        self.label_wid.setPixmap(pm2)

    # заливка через библеотеку opencv-python для быстрого заполнения и резулирования радиуса заливки
    def Floodyfill_color(self, x, y, color, k=0):
        if x > self.coord[0] or y > self.coord[1] or x < 0 or y < 0:
            return
        image = self.label.pixmap().toImage()
        image.save("time_file.png")
        cv_img = cv2.imread("time_file.png")
        # заполняем 
        cv2.floodFill(cv_img, None, (x, y), (color[2], color[1], color[0], color[3]), (k, k, k), (k, k, k), cv2.FLOODFILL_FIXED_RANGE)
        cv2.imwrite("time_file.png", cv_img)
        qu = QImage("time_file.png")
        pix = QPixmap.fromImage(qu)
        self.label.setPixmap(pix)
        os.remove("time_file.png")

    # создание нового холста - создаёт новое окно поверх
    def open_add_form(self):
        if self.okno:
            return
        self.okno = True
        # открываем новое окно
        self.second_form = AddForm(self)
        self.second_form.show()

    # добавление нового холста
    def new_holst(self):
        # по новым координатам задаём размер
        self.label.resize(*self.coord)
        # создаём новый холст
        canvas = QPixmap(*self.coord)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        self.label.move(self.dvig[0], self.dvig[1])
        self.label.setStyleSheet("background-color: white;")
        # обнуляем все параметры
        self.xy_past = 0
        self.index_img = -1
        self.cahe.clear()
        self.save_name = 0
        self.nowframe = 1
        self.cur = [0, 0]
        self.isctrl = False
        self.isplay = False
        self.timeline.frameForTime(int(1000/self.timel.fps))
        # self.timeline.startFrame(0)
        # self.timeline.setEndFrame(1)
        self.timel.clear()
        self.timel.addFrame(1, self.label.pixmap())
        self.timel.checkFrame(1, True)
        image = self.label.pixmap().toImage()
        image.save("time_file.png")
        cv_img = cv2.imread("time_file.png")
        self.cahe += [cv_img]
        os.remove("time_file.png")
    
    # открытие картинки через проводник
    def opened_new(self, fille=False):
        try:
            if fille is False:
                fille = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Картинка (*.bmp);;Все файлы (*)')[0]
            if fille == "":
                return
            pixmap = QPixmap(fille)
            # стандартные координаты
            w, h = 800, 450
            if pixmap.width() > w or pixmap.height() > h:
                # применяем соотношение если картинка больше стандартных координат (экрана программы)
                if pixmap.width() >= pixmap.height():
                    h = (w * pixmap.height()) // pixmap.width()
                    if h > 450:
                        k = h - 450
                        h -= k
                        w -= k
                    pixmap = pixmap.scaled(w, h)
                else:
                    w = (h * pixmap.width()) // pixmap.height()
                    if w > 800:
                        k = w - 800
                        h -= k
                        w -= k
                    pixmap = pixmap.scaled(w, h)
            # выставляем полученные размер
            self.label.resize(pixmap.width(), pixmap.height())
            self.label.setPixmap(pixmap)
            self.label.move(self.dvig[0], self.dvig[1])
            # очищаем все параметры
            self.cahe.clear()
            self.xy_past = 0
            self.index_img = -1
            self.coord = (pixmap.width(), pixmap.height())
            image = self.label.pixmap().toImage()
            image.save("time_file.png")
            cv_img = cv2.imread("time_file.png")
            self.cahe += [cv_img]
            os.remove("time_file.png")
            cv_img = self.cahe[0]
            cv2.imwrite("time_file.png", cv_img)
            qu = QImage("time_file.png")
            pix = QPixmap.fromImage(qu)
            self.label.setPixmap(pix)
            os.remove("time_file.png")
        # если случилось, что-то не предвиденное (не тот формат), то очищает историю и убирает холст
        except Exception:
            self.coord = (0, 0)
            self.cahe.clear()

    # при закрытие - проверка на сохранение файла
    def closeEvent(self, event):
        if not(self.exit):
            # не даёт выйти (пока не сохранят или откажутся)
            event.ignore()
            self.setDisabled(True)
            # вызывает окно с сохранением файла
            self.second_form = AddFormClose(self)
            self.second_form.show()

# Окно с созданием нового холста
class AddForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        # все параметры который вызвал это окно
        self.arg = args[0]
        self.initUI(args[0])

    def initUI(self, args):
        uic.loadUi("gui/new_holst.ui", self) 
        # все параметры который вызвал это окно
        self.a = args
        # передаст все нужные параметры
        self.add_holst.clicked.connect(lambda s, x=args: self.add(x))

    def add(self, a):
        # те самые параметры, которые передадутся для размера холста
        # wid - значения ширины, hie - значения высоты
        a.coord = (self.wid.value(), self.hie.value())
        # окно закрывается
        a.okno = False
        # создаём новый холст с новыми данными
        self.arg.new_holst()
        # закрываем окно
        self.close()
    
    # при закрытии просто окно закроется
    def closeEvent(self, e):
        self.a.okno = False


# Окно при закрытие - если картинка не сохранена
class AddFormClose(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.arg = args[0]
        uic.loadUi("gui/close.ui", self) 
        # три кнопки - сохраняет, не сохраняет, возвращает обратно к программе и не закрывате
        self.btn_save.clicked.connect(self.save)
        self.btn_no_save.clicked.connect(self.no_save)
        self.btn_cancle.clicked.connect(self.cancle)

    # сохраняет файл и закрывает программу
    def save(self):
        if self.arg.save_folder():
            self.arg.exit = True
            self.arg.close()
        # если не сохранился, то не закроет программу
        self.close()
    
    # не сохраняет файл и закрывает
    def no_save(self):
        self.arg.exit = True
        self.arg.close()
        self.close()
        
    # не закрывает программу
    def cancle(self):
        self.arg.setDisabled(False)
        self.close()
    
    # если закрыть окно, то программа не закроется
    def closeEvent(self, e):
        self.arg.setDisabled(False)

# вызываем программу
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()