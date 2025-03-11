import time
import pygame
import socket
import json
import threading
import os

pygame.init()

global current_dot_list
current_dot_list = [[-100,-100,-100],[-100,-100,-100],[-100,-100,-100]]

def receive_data(sock):
    global current_dot_list
    while True:
        data = sock.recv(1024)
        if not data:
            break
        # Обновляем текущее состояние dot_list из JSON
        current_dot_list = json.loads(data.decode('utf-8'))
        print(f"Updated dot_list from server: {current_dot_list}")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('Noutbuk-Artem.local', 12346))

threading.Thread(target=receive_data, args=(client,), daemon=True).start()


# запись цветов интерфейса
white = (250, 235, 215)
dark_white=(255, 222, 173) 
black = (0, 0, 0)
red = (255, 0, 0)
dark_red = (233, 81, 89)
green = (171, 206, 128)
FireBrick=(220, 104, 42)
DarkOrange=(255, 140, 0)
GreenYellow=(176, 224, 230)
brown=(34, 139, 34)

# размеры поля    
dis_x=450
dis_y=dis_x+50
dis=pygame.display.set_mode((dis_x,dis_y)) # создаем игровое поле
size=40
player=1

# счет
global score_x
score_x=0
global score_o
score_o=0

# подготовка дисплея и запуск времени
pygame.display.update() # обновляем экран
pygame.display.set_caption('OX')
clock=pygame.time.Clock()
font_size=dis_x//20
txt_style=pygame.font.SysFont(None,font_size) # задание размера текста

def mapa(): # рисует поле
    for i in range (2,dis_x,dis_x//9):
        pygame.draw.line(dis,dark_white,(i,0),(i,dis_x),2)
        pygame.draw.line(dis,dark_white,(0,i),(dis_x,i),2)
    for i in range (2,dis_x+5,dis_x//3):
        pygame.draw.line(dis,dark_white,(i,0),(i,dis_x),5)
        pygame.draw.line(dis,dark_white,(0,i),(dis_x,i),5)
        
def pause(): # пишет пауза
   value = txt_style.render("Pause" , True, black)
   dis.blit(value, [0, 0]) 

def massagecord(text,color,x,y): # функция выводящая сообщение
    msg=txt_style.render(text,True,color)
    dis.blit(msg,[x,y])
           
def massage(text,color): # функция выводящая сообщение
    msg=txt_style.render(text,True,color)
    dis.blit(msg,[dis_x/2-len(text)*font_size/7,dis_x/2])           
    
def score(score_o,score_x,color): # функция выводящая сообщение
    msg=txt_style.render("score o:"+str(score_o),True,color)
    dis.blit(msg,[dis_x*0.75,10])   
    msg=txt_style.render("score x:"+str(score_x),True,color)
    dis.blit(msg,[dis_x*0.75,10+font_size])      
    
def draw_obj(dot_list): # рисует точки доставая из тапла dot_list их координаты и значения цвета   
    for i in dot_list:
        if i[2]%2==0:
            ring=pygame.image.load(os.path.join('OX_PROJECT','ring.png'))
            scale_ring=pygame.transform.scale(ring,(dis_x/11,dis_x/11))
            dis.blit(scale_ring,[i[0]-dis_x/25, i[1]-dis_x/25])
        else:
            cross=pygame.image.load(os.path.join('OX_PROJECT','cross.png'))
            scale_cross=pygame.transform.scale(cross,((dis_x+150)/11,dis_x/11))
            dis.blit(scale_cross,[i[0]-dis_x/20, i[1]-dis_x/25]) 
def gameloop():            
    global current_dot_list
    current_dot_list = [[-100,-100,-100],[-100,-100,-100],[-100,-100,-100]]
    o_wins=True #  флаг отвечающий за определение победившего цвета, по умолчанию считается, что зеленые выйграли.
    x_wins=False
    draw=False
    
    fild=[ [[5,6,7],
            [8,9,10],
            [11,13,14]], 
           [[5,6,7],
            [8,9,10],
            [11,13,14]], 
           [[5,6,7],
            [8,9,10],
            [11,13,14]], 
           [[5,6,7],
            [8,9,10],
            [11,13,14]], 
           [[5,6,7],
            [8,9,10],
            [11,13,14]],
           [[5,6,7],
            [8,9,10],
            [11,13,14]], 
           [[5,6,7],
            [8,9,10],
            [11,13,14]],
           [[5,6,7],
            [8,9,10],
            [11,13,14]],
           [[5,6,7],
            [8,9,10],
            [11,13,14]]]
    summary_fild=[[5,6,7],
                  [8,9,10],
                  [11,13,14]] 
    
    # координаты подсветки места следующего хода
    global next_x 
    global next_y
    next_x=0
    next_y=0
    
    # координаты поставленой точки
    global cords
    cords=((0,0))
    cords_preview=((0,0)) # дополнительная переменная для отсеивания невозможных нажатий 
    
    # счетчик ошибок
    global mistake
    mistake=0
    
    game_end=False # флаг отвечающий за конец игры
    game_close=False # стартовое меню
    first_move=True # флаг отвечающий за первый ход, вырубает обязанность ходить в зелёные поля
    Pause=False # флаг для октивации паузы
    timer=False # флаг для того чтобы тапл с точками не пополнялся постоянно, а только тогда когда было сделан клик мышью
    next_move=True  # флаг для проверки, что ход сделан в веделенной области 
    rule=False  # флаг отвечающий за исполнение правил
    no_lead=False # если нет указаний куда надо ходить
    
    win_fild=[[False,True,True],
              [False,True,True],
              [False,True,True],
              [False,True,True],
              [False,True,True],
              [False,True,True],
              [False,True,True],
              [False,True,True],
              [False,True,True]]
    win_cords=[[-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0],
               [-1000,-1000,0]]
    dot_list=[[-100,-100,-100]] # тапл с точками
    today_dot=[-1,-1,-2] # тапл для записи последней поставленной точки
    today_mas=[-1]
    player=1
    global score_o
    global score_x
    
    while not game_end: # главный цикл, пока gama_end=False, игра продолжается
        dot_list=current_dot_list
        rule=False
        next_move=True
        mapa()
        if Pause: # цикл экрана меню
            pygame.display.update()
        while Pause==True:
            dis.fill(white)
            massage('Press A to continue game', black)
            score(score_o,score_x,black)
            pause()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_a: # запуск новой игры
                        Pause=False
                if event.type==pygame.QUIT: # закрытие окна
                    pygame.quit() # деинициализация библиотеки
                    quit()
        if game_close: # цикл экрана меню
            dis.fill(white)
            if o_wins==True and draw==False:
                massage('o wins', green)
                score_o+=1
            elif o_wins==False and draw==False:
                massage('x wins', red)
                score_x+=1  
            else:
                massage('draw', black)
            client.send(json.dumps('end').encode('utf-8'))     
            pygame.display.update()
            time.sleep(2)
        while game_close==True:
            dis.fill(white)
            massage('Press A to start game', black)
            score(score_o,score_x,black)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_a: # запуск новой игры
                        gameloop()
                if event.type==pygame.QUIT: # закрытие окна
                    pygame.quit() # деинициализация библиотеки
                    quit() 
        for event in pygame.event.get(): # достаём все события из массива событий в библиотеке pygame. event.get() возвращает в терминал все события, которые происходят с игрой
            if event.type==pygame.QUIT: # закрытие окна
                pygame.quit() # деинициализация библиотеки
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: 
                        Pause=True
                if event.key==pygame.K_r: 
                    game_close=True     
            if event.type==pygame.MOUSEBUTTONDOWN: # отслеживание нажатия мыши
                cords_preview=event.pos # предварительная запись координат клика
                for i in dot_list:
                    if i[0]-dis_x//18<=cords_preview[0]<=i[0]+dis_x//18 and i[1]-dis_x//18<=cords_preview[1]<=i[1]+dis_x//18: 
                        mistake+=1
                        print(mistake)
                for i in win_cords:
                    if (i[0]<cords_preview[0]<=i[0]+dis_x//3 and i[1]<cords_preview[1]<=i[1]+dis_x//3):
                        mistake+=1
                if dot_list[-1][2]%2==player:
                    mistake+=1 
                if mistake>0:
                    next_move=False
                    rule=False
                    mistake=0
                else:
                    next_move=True
                    rule=True  
                for i in win_cords:
                    if (i[0]==next_x and i[1]==next_y):
                        no_lead=True  
                print(rule)            
                if rule and next_x<=cords_preview[0]<=next_x+dis_x//3 and next_y<=cords_preview[1]<=next_y+dis_x//3 or first_move or no_lead:
                      cords=cords_preview
                      first_move=False
                      no_lead=False
                      timer=True
        for i in range(0,dis_x+5,dis_x//9):
            for j in range(-9,8):    
                if (i+j*dis_x//9)<cords[0]<=(i+(j+1)*dis_x//9) and (i-dis_x//9)<=cords[1]<=i and timer==True and rule==True:
                    # Если координата мыши находится в проверяем клетке:
                    today_dot=[] # обнуляем текущую точку
                    # записываем текущую точку координаты x и y и текущий цвет
                    today_dot.append(i+j*dis_x//9+dis_x//18) 
                    today_dot.append(i-dis_x//18)
                    today_dot.append(player)
                    # запихиваем текущую точку в тапл ко всем
                    dot_list.append(today_dot)      
                    try:
                        client.send(json.dumps(today_dot).encode('utf-8'))
                    except Exception as e:
                        print(f"Error sending data: {e}")  
                    timer=False  
        for f in range(0,9,1):
            for i in range (0,dis_x//3,dis_x//9):
                for j in range (0,dis_x//3,dis_x//9):
                    if (dot_list[-1][0]==i+f%3*(dis_x//3)+dis_x//18 and dot_list[-1][1]==j+f//3*(dis_x//3)+dis_x//18):
                        if dot_list[-1][2]%2==0:
                            fild[f][j//(dis_x//9)][i//(dis_x//9)]=2
                            
                        else:
                            fild[f][j//(dis_x//9)][i//(dis_x//9)]=1
        local_count=0                   
        for i in fild:
            
            if(i[0][0]==i[0][1] and i[0][0]==i[0][2] or 
               i[1][0]==i[1][1] and i[1][0]==i[1][2] or 
               i[2][0]==i[2][1] and i[2][0]==i[2][2] or
               i[0][0]==i[1][0] and i[0][0]==i[2][0] or
               i[0][1]==i[1][1] and i[0][1]==i[2][1] or
               i[0][2]==i[1][2] and i[0][2]==i[2][2] or
               i[0][0]==i[1][1] and i[0][0]==i[2][2] or
               i[0][2]==i[1][1] and i[0][2]==i[2][0]):
                    win_fild[local_count][0]=True
                    win_cords[local_count][0]=local_count%3*(dis_x//3)
                    win_cords[local_count][1]=local_count//3*(dis_x//3)
                    
            local_count+=1        
        
        if next_move:
            for f in range(0,9,1):
                for i in range (0,dis_x//3,dis_x//9):
                    for j in range (0,dis_x//3,dis_x//9):
                        if (dot_list[-1][0]==i+f%3*(dis_x//3)+dis_x//18 and dot_list[-1][1]==j+f//3*(dis_x//3)+dis_x//18):
                                pygame.draw.rect(dis, GreenYellow, [i*3,j*3,dis_x//3,dis_x//3])
                                next_x=i*3
                                next_y=j*3
                                
        for i in range(0,9,1):
            if win_fild[i][0]:
                if win_fild[i][2]:
                    win_cords[i][2]=dot_list[-1][2]
                if win_cords[i][2]%2==0: 
                    pygame.draw.rect(dis, green, [win_cords[i][0],win_cords[i][1],dis_x//3,dis_x//3])
                    if win_fild[i][2]:
                        today_mas=[]
                        today_mas.append(win_cords[i][0]+dis_x//6)
                        today_mas.append(win_cords[i][1]+dis_x//6)
                        today_mas.append(2)
                        win_fild[i][2]=False       
                else:
                    pygame.draw.rect(dis, FireBrick, [win_cords[i][0],win_cords[i][1],dis_x//3,dis_x//3])
                    if win_fild[i][2]:
                        today_mas=[]
                        today_mas.append(win_cords[i][0]+dis_x//6)
                        today_mas.append(win_cords[i][1]+dis_x//6)
                        today_mas.append(1)
                        win_fild[i][2]=False
        
        for i in range (0,dis_x,dis_x//3):
                        for j in range (0,dis_x,dis_x//3):
                            if (today_mas[0]==i+dis_x//6 and today_mas[1]==j+dis_x//6):
                                
                                if today_mas[2]%2==0:
                                    summary_fild[j//(dis_x//3)][i//(dis_x//3)]=2
                                else:
                                    summary_fild[j//(dis_x//3)][i//(dis_x//3)]=1                                                            
        
        if(summary_fild[0][0]==summary_fild[0][1] and summary_fild[0][0]==summary_fild[0][2] or 
            summary_fild[1][0]==summary_fild[1][1] and summary_fild[1][0]==summary_fild[1][2] or 
            summary_fild[2][0]==summary_fild[2][1] and summary_fild[2][0]==summary_fild[2][2] or
            summary_fild[0][0]==summary_fild[1][0] and summary_fild[0][0]==summary_fild[2][0] or
            summary_fild[0][1]==summary_fild[1][1] and summary_fild[0][1]==summary_fild[2][1] or
            summary_fild[0][2]==summary_fild[1][2] and summary_fild[0][2]==summary_fild[2][2] or
            summary_fild[0][0]==summary_fild[1][1] and summary_fild[0][0]==summary_fild[2][2] or
            summary_fild[0][2]==summary_fild[1][1] and summary_fild[0][2]==summary_fild[2][0]):
                if today_mas[2]%2==1:
                    game_close=True
                    o_wins=False
                else:
                    game_close=True
                    o_wins=True                  
        
        
                                              
        if dot_list[-1][2]%2==0:
                        pygame.draw.rect(dis,FireBrick,(0,dis_x+5,dis_x+100,dis_x/9))   
                        massagecord("X turn",black,dis_x/2,dis_x+15) 
        else:
                        pygame.draw.rect(dis,green,(0,dis_x+5,dis_x+100,dis_x/9))  
                        massagecord("O turn",black,dis_x/2,dis_x+15) 
        draw_obj(dot_list)
        mapa()     
        pygame.display.update() 
        dis.fill(white)
        # FPS всей игры
        clock.tick(5)         
gameloop()                    