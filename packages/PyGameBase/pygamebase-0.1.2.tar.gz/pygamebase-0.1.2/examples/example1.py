#modulos
import pygame
import os
import sys
#inicialização de modulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyGameBase import desing as ds
pygame.init()
#variaveis Grobais
close_control = ds.Close()
screen_loop = ds.Screen_loop("main", close_control)
#classe principal
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800,600),pygame.RESIZABLE)
        self.cena = 0
        self.blocopulador = ds.box(width=400,height=100,position_x=0,position_y=500)
        self.coleção = ds.Collection(grupo=[ds.box(width=100,height=100,position_x=400,position_y=500),self.blocopulador,ds.box(width=100,height=100,position_x=800,position_y=500),ds.box(width=300,height=100,position_x=900,position_y=500)])
        self.pesonagen = ds.Characters(colision_color=False,width=70,padding_image=60,height=200,position_x=200,position_y=800,Collection=self.coleção,colision=True,directory="animation_spritesheets",width_image=200,height_image=200,animation_name="personagem")
        self.mobs = ds.Entity(colision=True,padding_image=3,directory="animation_spritesheets",name_animation="furacao",width_image=100,height_image=100,width=100,height=100,position_x=40,position_y=100,Collection=self.coleção,not_Penetrate=[self.pesonagen],colision_color=False)
        self.colecão_players = ds.Collection([self.pesonagen])
        self.item = ds.item("animation_spritesheets/furacao.png",position_x=400,position_y=200,scale=2,grupo=self.colecão_players)
        self.coleção.add_textures("textures/bloco.png")
        self.cenas_lista = [self.pesonagen,self.coleção,self.mobs,self.item]
    def test1(self):
        self.pesonagen.position_y = 0
        quadrado = ds.Square(self.screen,position_x="center",position_y="center",width="responsive",height="responsive",color=ds.Colors.DARK_GREEN,responsive_magin=0.9,border_radius=ds.BorderRadius(40))
        quadrado2 = ds.Square(self.screen,position_x="center",position_y="center",width="responsive",height="responsive",color=ds.Colors.RED,space_inside=3,responsive_magin=0.9)
        text = ds.Font_text(self.screen,text="começa jogo",position_x="center",position_y=100,sizepy=70)
        button = ds.ButtonElement(self.screen,"bem vindo",position_x="center",position_y=200,width="responsive",height=70, color=ds.Colors.DARK_PURPLE,text_color= ds.Colors.WHITE, sizepy=40,hover=ds.Colors.RED,responsive_magin=0.95,border_radius=10)
        button1 = ds.ButtonElement(self.screen,"",position_x=0,position_y=200,width=300,height=70, color=None,text_color= ds.Colors.WHITE, sizepy=40,hover=ds.Colors.RED)
        button2 = ds.ButtonElement(self.screen,"",position_x=0,position_y=200,width=300,height=70, color=None,text_color= ds.Colors.WHITE, sizepy=40,hover=ds.Colors.RED)
        screen_loop.VerticalStack(controls=[button,button1,button2],position_y=200,spacing=60)
        
        for event in pygame.event.get():
            close_control.check(event)
            if button.is_clicked(event):
                self.cena = 1 

        screen_loop.add_cena(self.screen, [quadrado,quadrado2,text,button,button1,button2], ds.Colors.LIGHT_GRAY)
        pygame.time.Clock().tick(60)
        return True,self.cena

    def test2(self):
        text = ds.Font_text(self.screen,text="cena 2",position_x=250)
        button = ds.ButtonElement(self.screen,"Clique aqui", 300, 200, 200, 50, ds.Colors.GREEN, ds.Colors.WHITE, sizepy=40)
        #dados = ds.Text_box(self.screen,text="jjj",position_x=300,position_y=200,width=400,height=100)
        newpress = ds.function_lists_keyboard_press(
                keys=[pygame.K_a],
                functions_def=[lambda: print("a pressionada")]  
            )
        self.cenas_lista.append(button)
        for event in pygame.event.get():
            #dados.To_write(event)
            newclick = ds.function_lists_keyboard_click(keys_click=[pygame.K_SPACE],functions_def=[lambda: print("hellow world")])
            close_control.check(event)
            self.pesonagen.button_functions_on_clicked(evento=event,strength=(20,10,10,10),potencia=(1,1,1,1),disable=ds.Disable(up=False,down=True,left=True,right=True),key_control=newclick)
            self.pesonagen.handle_key_release(event,animation_name="personagem")
        if self.item.drop():
            if self.item in self.cenas_lista:
                self.cenas_lista.remove(self.item)
        self.pesonagen.button_functions_on_press(disable=ds.Disable(True,False,False,False),potencia=[10,10,10,10],animation_right="andando",animation_left="esquerda",key_control=newpress)
        self.pesonagen.Physical(gravity=9.8,barrier=False,desable_button=True)
        self.mobs.Physical(gravity=9.8)
        self.item.animation_move()
        screen_loop.add_cena(self.screen,self.cenas_lista, ds.Colors.BRONZE)
        pygame.time.Clock().tick(30)
        return True,self.cena
#chamando a classe
game = Game()
screen_loop.initiation(scene=1,scenes=[game.test2,game.test1])
pygame.quit()