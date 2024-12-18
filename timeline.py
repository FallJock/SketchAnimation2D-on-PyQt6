from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import QWidget
from math import floor


# константные параметры - цвет и стиль
COLORTEXT = QColor(200, 200, 200)
COLORFRAME = QColor(80, 100, 190)
TIMELINEBACKGROUND = QColor(40, 40, 80)
FONT = QFont('Decorative', 6)

# класс фрейма содержащий информацию о позиции с цветом и хранит картинку холста этой позиции
class Frame:
    def __init__(self, num, duration=1, color=COLORFRAME, picture=None):
        # продолжительность фрейма
        self.duration = duration
        # цвет фона
        self.color = color
        # ширина и длина фрейма
        self.width = 10
        self.height = 50
        # позиция/номер фрейма
        self.num = num
        # картинка холста данной позиции
        self.picture : QPixmap | None = picture
        self.minipic : QPixmap | None = picture
        # чтобы картинка влезала в фрейм
        self.setHeightPicture(self.height)
    
    # задаёт высоту для маленькой картинки
    def setHeightPicture(self, h):
        if self.minipic:
            self.minipic = self.minipic.scaledToHeight(int(h))
    
    # заменяет на новую картинку холста
    def setPic(self, pic):
        self.picture = pic
        self.minipic = pic
        self.setHeightPicture(self.height)
    
    # задаёт новый размер
    def setSize(self, w, h):
        self.width = w
        self.height = h
        self.setHeightPicture(self.height)
    
    # задаёт новую продолжительность
    def setDuration(self, dur):
        old = self.duration
        self.duration = dur
        return old
    
    # двигает фрейм (его позицию)
    def moveNum(self, step):
        self.num += step


# Виджет таймлайн содержащий фреймы, а также имеет возможность с фреймами взаимодействовать и отображать
class TimeLine(QWidget):
    def __init__(self, parent=None, w=720, h=80, fps=24):
        super().__init__(parent=parent)
        # ширина и длина таймлайна
        self.w = w
        self.h = h
        # область с временем и область с фреймами (их высоты)
        self.htime, self.hfram = self.h * 0.375, self.h * 0.625
        # ширина фрейма
        self.widthf = 10
        # FPS таймлайна
        self.fps = fps
        # промежуток отображения позиций фрееймов (текст номеров)
        self.textdur = int(self.fps / 6)
        # цвет для таймлайна, текста и характеристики текста 
        self.backgroundColor = TIMELINEBACKGROUND
        self.textColor = COLORTEXT
        self.font = FONT
        # выбранный фрейм
        self.selectedframe = None
        # хранит все существующие фреймы
        self.frames = {}
        # максимальный номер из фреймов
        self.maxnum = 0
        # насколько был совершён скролл вправо (потеренная часть)
        self.scrollX = 0
    
    # скролл вправа (передвижение по таймлайну вправа)
    def rightScrollx(self, x):
        if (self.scrollX + x) < 0:
            self.scrollX = 0
        else:
            self.scrollX += x
    
    # скролл влева (передвижение по таймлайну влева)
    def leftScrollx(self, x):
        if (self.scrollX - x) < 0:
            self.scrollX = 0
        else:
            self.scrollX -= x
    
    # начальный номер кадра в таймлайне с пременением скролла (чтобы получить начальную позицию для отрисовки)
    def getStartNumframe(self):
        return floor(self.scrollX / self.widthf)
    
    # координата в таймлайне?
    def inTimeline(self, x, y):
        fnx, fny = self.x() + self.w, self.y() + self.h
        return (((x - self.x()) * (x - fnx)) <= 0 and\
            ((y - self.y()) * (y - fny)) <= 0)
    
    # координата в области с фреймами?
    def inFrames(self, x, y):
        if self.inTimeline(x, y):
            my = y - self.y()
            fry, fry2 = self.htime, self.h
            if ((my - fry) * (my - fry2)) <= 0:
                return True
        return False
    
    # подсчёт места в таймлайне по x мыши
    def flo(self, x):
        mx = x - self.x()
        key = floor(mx / self.widthf) + 1
        return key

    # проверка есть ли фрейм на этой координате (может выбрать этот фрейм при select=True)
    def checkFrameM(self, x, y, select=False):
        if self.inFrames(x, y):
            mx = x - self.x()
            key = floor(mx / self.widthf) + 1
            k = self.inBetweenFrame(key + self.getStartNumframe())
            if k:
                key = k
            else:
                key = key + self.getStartNumframe()
            if key in self.frames:
                if select:
                    self.selectedframe = self.frames[key]
                return True
        return False
    
    # проверка есть ли фрейм позиции num (может выбрать этот фрейм при select=True)
    def checkFrame(self, num, select=False):
        k = self.inBetweenFrame(num)
        if k:
            num = k
        if num in self.frames:
            if select:
                self.selectedframe = self.frames[num]
            return True
        return False
    
    # фрейм между другими?
    def inBetweenFrame(self, key):
        if key in self.frames:
            return key
        pk = 0
        for k in sorted(self.frames):
            if key < k and pk != 0:
                if (self.frames[pk].num + self.frames[pk].duration) > key:
                    return pk
                return False
            pk = k
        else:
            if pk != 0 and (self.frames[pk].num + self.frames[pk].duration) > key:
                return pk
        return False
    
    # соседи фрейма (левый, центр, правый)
    def neibFrame(self, key):
        frs = sorted(self.frames)
        if key not in frs or self.selectedframe is None or len(frs) < 2:
            return
        pk = 0
        flag = False
        for k in frs[:-1]:
            if key == 0 and k != 0:
                return (None, key, k)
            if key == k:
                flag = True
                continue
            if flag:
                return (pk, key, k)
            if k != frs[-2]:
                pk = k
        else:
            if key == max(frs):
                return (k, key, None)
            return (pk, key, frs[-1])

    # добавить фрейм с картинкой по координате мыши
    def addFrameM(self, x, y, pic):
        if self.inFrames(x, y):
            mx = x - self.x()
            # добавление
            key = floor(mx / self.widthf) + 1 + self.getStartNumframe()
            if self.inBetweenFrame(key):
                return False
            fram = Frame(key, picture=pic)
            fram.setSize(self.widthf, self.hfram)
            self.frames[key] = fram
            self.maxnum = max(max(self.frames), self.maxnum)
            return fram
        return False
    
    # добавить фрейм с картинкой по кадру
    def addFrame(self, num, pic):
        if self.inBetweenFrame(num):
            return False
        fram = Frame(num, picture=pic)
        fram.setSize(self.widthf, self.hfram)
        self.frames[num] = fram
        self.maxnum = max(max(self.frames), self.maxnum)
        return fram
    
    # прибавить длительность фрейма
    def addSelectFrameDur(self, plus):
        if self.selectedframe:
            fr = self.selectedframe
            d = fr.duration
            if (d + plus) >= 1:
                self.setFrameDur(fr.num, d + plus)
    
    # прибавление 1 к длительности фрейма (для сочетаний клавишь)
    def plusDur(self):
        self.addSelectFrameDur(1)
        self.update()
    
    # уменьшает длительность фрейма на 1 (для сочетаний клавишь)
    def minusDur(self):
        self.addSelectFrameDur(-1)
        self.update()
    
    # задать новую длительность фрейму
    def setFrameDur(self, num, duration):
        if self.checkFrame(num) and duration >= 0:
            if duration == 0:
                self.delFrame(num)
                return False
            fram = self.frames[num]
            olddur = fram.setDuration(duration)
            cut = (duration - olddur)
            if cut <= 0:
                return False
            endp = fram.duration + (fram.num)
            stp = num
            keys = []
            # передвигает остальные фреймы если длительность заходит за них
            while stp <= self.maxnum:
                stp += 1
                if stp not in self.frames:
                    continue
                endp2 = self.frames[stp].num
                if endp2 - endp <= 0:
                    self.frames[stp].moveNum(endp - endp2)
                    keys.append((stp, self.frames[stp].num, self.frames[stp]))
                    endp = (self.frames[stp].num) + self.frames[stp].duration
                    self.maxnum = max(self.frames[stp].num, self.maxnum)
            cheked = set()
            # добавление изменений к фреймам
            for old, new, fr in keys:
                if old in cheked:
                    continue
                self.delFrame(old)
                cheked.add(new)
                self.frames[new] = fr
            self.maxnum = max(max(self.frames), self.maxnum)
        return False
    
    # заполнение пустых прорезей между фреймами
    def fillFrames(self):
        pastk = 0
        for k in sorted(self.frames):
            if pastk == 0:
                pastk = k
                continue
            pfr = self.frames[pastk]
            fr = self.frames[k]
            if (pfr.num + pfr.duration) < fr.num:
                pfr.setDuration(fr.num - (pfr.num + pfr.duration) + 1)
            pastk = k
        self.maxnum = max(max(self.frames), self.maxnum)
    
    # удаление фрейма по координате мыши
    def delFrameM(self, x, y):
        if self.inFrames(x, y) and self.checkFrame(x, y):
            mx = x - self.x()
            key = floor(mx / self.widthf) + 1 + self.getStartNumframe()
            m = self.frames.pop(key)
            self.maxnum = max(max(self.frames), self.maxnum)
            return m
        return False
    
    # удаление фрейма по кадру
    def delFrame(self, num):
        if self.checkFrame(num):
            m = self.frames.pop(num)
            self.maxnum = max(max(self.frames), self.maxnum)
            return m
        return False
    
    # очистка таймлайна
    def clear(self):
        self.frames.clear()
        self.selectedframe = None
        self.maxnum = 0
        self.scrollX = 0

    # отрисовка таймлайна
    def paintEvent(self, event):
        # позиция таймлайна
        px, py = 0, 0
        qp = QPainter()
        qp.begin(self)
        qp.setPen(self.textColor)
        qp.setFont(self.font)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        print(px, py)
        # фон для таймлайна
        path = QPainterPath()
        qp.setPen(QColor(10, 10, 10))
        path.addRect(px, py, self.w, self.h)
        qp.fillPath(path, self.backgroundColor)
        qp.drawPath(path)
        
        stfram = self.getStartNumframe()
        # перебор фреймов до ширины таймлайна
        for num in range(floor(self.w / self.widthf) + 1):
            # каждые например 24фпс пишется его секунда
            if (num + stfram) % self.fps == 0:
                qp.setPen(QColor(70, 160, 200))
                qp.drawText(int(px + ((num) * self.widthf)), py,
                self.widthf + 4, int(self.htime), Qt.AlignmentFlag.AlignLeft, str(int((num + stfram) / self.fps)) + "s")
                qp.setPen(QColor(70, 160, 200))
                qp.drawLine(int(px + ((num) * self.widthf)), py + 10,
                int(px + ((num) * self.widthf)), py + self.h)
            # каждые 24фпс / 6 = 4 тот пишет цифру кадра
            if num % self.textdur == 0:
                qp.setPen(QColor(255, 255, 255))
                qp.drawText(int(px + ((num) * self.widthf)), py + int(self.htime) - 15,
                self.widthf + 4, int(self.htime), Qt.AlignmentFlag.AlignHCenter, str((num + stfram + 1)))
                qp.setPen(QPen(self.textColor))
                qp.drawLine(int(px + ((num) * self.widthf)), py + int(self.htime) - 10,
                int(px + ((num) * self.widthf)), py + int(self.htime))
            else:
                qp.setPen(QColor(100, 200, 240))
                qp.drawLine(int(px + ((num) * self.widthf)), py + int(self.htime) - 6,
                int(px + ((num) * self.widthf)), py + int(self.htime))
        
        # отрисовка фрейма и картинок
        for num in range(1, floor(self.w / self.widthf) + 2):
            # stfram - утеренный промежуток после скрола, для верного отображения фреймов
            if (num + stfram) in self.frames:
                frm = self.frames[(num + stfram)]
                wid = self.widthf * frm.duration
                if ((num - 1) * self.widthf) + (self.widthf * frm.duration) > self.w:
                    continue
                # оболочка фрейма
                path = QPainterPath()
                path.addRoundedRect(
                    QRectF(px + ((num - 1) * self.widthf), py + self.htime,
                           wid, self.hfram),
                    2, 2)
                qp.setClipPath(path)
                
                path = QPainterPath()
                qp.setPen(QColor(90, 70, 100))
                path.addRoundedRect(
                    QRectF(px + ((num - 1) * self.widthf), py + self.htime,
                           wid, self.hfram),
                    2, 2)
                # если выбран фрейм - то ставит жёлтый цвет
                if self.selectedframe and self.selectedframe.num == num + stfram:
                    qp.fillPath(path, QColor(150, 150, 10))
                else:
                    qp.fillPath(path, COLORFRAME)
                qp.drawPath(path)
                
                # картинка фрейма (если влезает под фрейм, то отображает картинку фрейма)
                if frm.minipic is not None:
                    if frm.minipic.size().width() / 2 < frm.duration * self.widthf:
                        path2 = QPainterPath()
                        path2.addRoundedRect(QRectF(
                            px + ((num - 1) * self.widthf), int(py + self.htime + 10),
                            wid, int(self.hfram) - 15),
                                            2, 2)
                        if self.selectedframe and self.selectedframe.num == num + stfram:
                            qp.fillPath(path2, QColor(150, 150, 10))
                        else:
                            qp.fillPath(path2, COLORFRAME)
                        qp.setClipPath(path2)
                        qp.drawPixmap(QRect(px + ((num - 1) * self.widthf), int(py + self.htime), frm.minipic.size().width() - 40, int(self.hfram)), frm.minipic)
        qp.end()