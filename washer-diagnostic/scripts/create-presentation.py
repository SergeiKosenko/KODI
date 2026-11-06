#!/usr/bin/env python3
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image
R=Path(__file__).resolve().parents[1]; OUT=R/'dist/mastercode-presentation.pdf'
for name,file in [('Regular','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=1280,720
navy='#102d32';mint='#b7f0d6';off='#f4f6f5';muted='#70877c'
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('МастерКод — Android-справочник мастера');c.setAuthor('МастерКод')
idx=0

def rect(x,y,w,h,color,r=0):
 c.setFillColor(HexColor(color));c.setStrokeColor(HexColor(color))
 if r:c.roundRect(x,y,w,h,r,fill=1,stroke=0)
 else:c.rect(x,y,w,h,fill=1,stroke=0)
def txt(text,x,y,size=18,color=navy,bold=False):
 c.setFillColor(HexColor(color));c.setFont('Bold' if bold else 'Regular',size);c.drawString(x,y,text)
def para(text,x,top,width,size=18,color=muted,leading=None):
 style=ParagraphStyle('p',fontName='Regular',fontSize=size,leading=leading or size*1.5,textColor=HexColor(color))
 p=Paragraph(text,style);_,h=p.wrap(width,H);p.drawOn(c,x,top-h);return h

def begin(kicker,title,dark=False):
 global idx;idx+=1
 rect(0,0,W,H,navy if dark else off)
 txt('мастерКОД',55,665,18,mint if dark else navy,True)
 txt(kicker.upper(),55,602,11,mint if dark else '#548371',True)
 if title:txt(title,55,550,34,off if dark else navy,True)
 c.setStrokeColor(HexColor('#31504f' if dark else '#dce4df'));c.line(55,48,1225,48)
 txt('Android · справочник для специалистов · версия 0.1',55,27,10,'#7b9b91' if dark else muted)
 txt(f'{idx:02}',1198,27,11,mint if dark else muted)
def end():c.showPage()
def bullet(n,title,body,x,y,width=480):
 rect(x,y-6,34,34,'#deeee3',8);txt(f'{n:02}',x+7,y+5,12,'#3e7557',True)
 txt(title,x+52,y+8,19,navy,True);para(body,x+52,y-8,width-52,15)
def image(path,x,y,w,h):
 im=Image.open(path);iw,ih=im.size;scale=min(w/iw,h/ih)
 c.drawImage(ImageReader(im),x+(w-iw*scale)/2,y+(h-ih*scale)/2,width=iw*scale,height=ih*scale,mask='auto')

def phone(path,x,y,w=233,h=500):
 rect(x-7,y-7,w+14,h+14,'#23483f',22);rect(x,y,w,h,'#f4f6f5',15);image(path,x,y,w,h)

begin('Рабочая версия / 06 ноября 2026','',True)
txt('От кода ошибки',55,492,49,off,True);txt('к плану проверки.',55,425,49,mint,True)
para('МастерКод — офлайн-приложение для мастеров по ремонту стиральных машин.',55,370,600,23,'#a9c6b8')
for x,num,label in [(55,'79','карточек кодов'),(270,'15','марок с кодами'),(485,'40','марок в указателе')]:
 txt(num,x,220,43,mint,True);txt(label,x,185,13,'#abc5b8')
para('Стартовая справочная база. Полный охват моделей и проверка сервисных инструкций ещё требуют работы.',55,134,600,13,'#abc5b8')
phone(R/'docs/screen-phone.png',900,118,230,498);end()

begin('01 / Задача','Рабочий инструмент на выезде')
bullet(1,'Быстро найти направление проверки','Фильтры по марке, модели, коду и узлу. Возможные причины и шаги проверки в одной карточке.',55,465,540)
bullet(2,'Сохранить результаты','Избранное, заметки мастера и история открытых карточек хранятся локально.',55,335,540)
bullet(3,'Не путать серии машин','Область применимости и статус данных видны в интерфейсе. Общая справка не выдаётся за инструкцию точной модели.',55,205,540)
rect(700,145,515,350,'#e3ede5',18)
txt('Для кого',735,448,15,'#56806c',True)
para('Выездные мастера<br/>Сервисные мастерские<br/>Специалисты по диагностике',735,408,430,26,navy,42)
para('Приложение не выполняет измерения и не управляет техникой. Решение о ремонте принимает специалист.',735,230,430,15)
end()

begin('02 / Поиск','Марка → модель → код → проверка')
image(R/'docs/screen-desktop.png',55,115,760,400)
rect(850,135,360,370,'#ffffff',16)
for y,n,t,b in [(445,1,'Идентификация','Модель с таблички, код изделия и ревизия электроники.'),(335,2,'Точный код','Разделение по маркам. OE и 0E не считаются одним кодом.'),(225,3,'Работа без сети','Поиск и карточки доступны полностью офлайн.')]:
 txt(f'0{n}',875,y,13,'#80ac91',True);txt(t,917,y,17,navy,True);para(b,917,y-16,260,13)
end()

begin('03 / Карточка диагностики','Один код — несколько возможных причин')
phone(R/'docs/screen-detail-phone.png',100,105,215,412)
bullet(1,'Причины и проверяемый узел','Код OE в справочной карточке LG указывает направление поиска в системе слива; он не доказывает поломку насоса.',410,457,740)
bullet(2,'Последовательность действий','Зафиксировать условия ошибки, безопасно слить воду, проверить тракт слива, затем насос и контроль уровня.',410,322,740)
bullet(3,'Заметки и избранное','Сохранить результаты осмотра и измерений, вернуться к карточке на следующем выезде.',410,187,740)
end()

begin('04 / Каталог','Что есть в стартовой базе')
for x,num,title,desc in [(55,'79','карточек кодов','Включая варианты написания кода.'),(455,'15','марок с карточками','Samsung, LG, Bosch, Siemens и другие.'),(855,'40','марок в указателе','Не означает охват моделей этих марок.')]:
 rect(x,295,365,205,'#ffffff',14);txt(num,x+25,426,60,'#2c6855',True);txt(title,x+25,380,20,navy,True);para(desc,x+25,350,315,14)
para('Карточки: Samsung · LG · Bosch · Siemens · Indesit · Hotpoint-Ariston · Beko · Candy · Electrolux · Zanussi · AEG · Whirlpool · Atlant · Haier · Gorenje',55,240,1120,19,navy)
rect(55,92,1165,85,'#f3e9d4',12);para('Все штатные записи имеют справочный статус. Первичные сервисные документы не приложены. Каталог не является перечнем всех моделей, используемых в России.',78,153,1110,16,'#846a35')
end()

begin('05 / Тестовый режим','Процедура зависит от модели и панели')
image(R/'docs/screen-service.png',55,120,670,390)
rect(760,135,460,375,'#ffffff',14)
txt('Текущая реализация',785,465,19,navy,True)
para('Один справочный черновик LG: F1096ND3 / F1296ND3. Не подтверждён первичным документом.',785,435,400,17,'#947434')
para('Шаги открываются после подтверждения специалистом сверки маркировки, панели и документации.',785,327,400,16)
para('Подготовка, вход и выход описаны отдельно. Полная таблица тестовых этапов отсутствует.',785,238,400,16)
para('Для других моделей приложение сообщает об отсутствии инструкции; импорт требует точного списка моделей и источника.',55,100,1150,14)
end()

begin('06 / Расширение базы','Новые данные без переустановки приложения')
for x,n,t,b in [(55,1,'Документ','Найти сервисное руководство для модели и ревизии.'),(355,2,'Структура','Описать код, применимость, проверки и ссылку на страницу.'),(655,3,'Импорт JSON','Пакет проверяется по структуре. Сведения имеют статус базы мастера.'),(955,4,'Резервная копия','Экспортировать импортированную базу, избранное и заметки.')]:
 rect(x,220,270,280,'#ffffff',14);txt(f'0{n}',x+20,450,32,'#7eaa8d',True);txt(t,x+20,392,18,navy,True);para(b,x+20,359,230,16)
para('Ссылка на источник не равна независимой проверке. Перед рабочим использованием нужны проверка документа и испытание на соответствующей машине.',55,160,1150,18,navy)
end()

begin('07 / Технология','Локальная работа и минимум разрешений')
bullet(1,'Android 8.0+','Нативная оболочка Java + WebView. Каталог и интерфейс включены в APK.',55,460,610)
bullet(2,'Без аккаунта и облака','У приложения нет разрешения INTERNET. Нет аналитики, рекламы и отправки заметок на сервер.',55,330,610)
bullet(3,'Файлы через системный диалог','Импорт и экспорт через Android Storage Access Framework. Ссылки на документы открываются во внешнем браузере.',55,200,610)
rect(780,145,430,355,navy,18)
txt('Данные на устройстве',810,450,20,mint,True)
para('Каталог кодов<br/>Процедуры<br/>Избранное<br/>Заметки мастера<br/>История карточек',810,410,360,21,'#e0eee4',38)
end()

begin('08 / Проверка','Сборка и сценарии проверены')
rows=[('APK','Собран; подпись v2/v3 и манифест проверены.'),('Логика','7 тестов: поиск, изоляция марок, модели, импорт и источник.'),('Интерфейс','Поиск, заметки, избранное, импорт, экспорт и восстановление.'),('Адаптивность','Мобильный экран 390 px; переполнения по ширине нет.'),('Ограничение','На физическом Android-устройстве и эмуляторе не запускался.')]
for i,(label,body) in enumerate(rows):
 y=445-i*65;rect(55,y-17,1160,55,'#ffffff',8);txt(label,75,y+2,16,navy,True);txt(body,280,y+2,15,muted)
para('APK подписан отладочным ключом: для тестовой установки. Для публикации нужна отдельная release-подпись и проверка на реальных устройствах.',55,92,1140,13)
end()

begin('09 / Дальнейшее развитие','От справочника к проверенной базе',True)
for x,n,t,b in [(55,1,'Подтвердить сведения','Собрать документы производителей, полные модели, коды изделий и ревизии.'),(455,2,'Испытать сценарии','Проверить коды и тестовые последовательности на соответствующей технике.'),(855,3,'Подготовить выпуск','Испытать Android-оболочку на устройствах, настроить release-подпись и обновления базы.')]:
 txt(f'0{n}',x,452,45,mint,True);txt(t,x,385,21,off,True);para(b,x,350,350,19,'#abc5b8')
para('Сейчас: рабочая тестовая версия приложения, APK, исходники и эта презентация. Полный российский парк моделей пока не покрыт.',55,170,1130,23,mint)
end()
c.save();print(OUT)
