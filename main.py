import math
import threading
import time
from os import listdir, path
from os.path import isfile, join

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.context_instructions import PopMatrix, PushMatrix, Rotate
from kivy.uix.behaviors import DragBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout


class DragJS(DragBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

class RMassets(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #For Movement-JoyStick
        Clock.schedule_interval(self.ckjoypos,0.01)

        #For Removal of Waste Widgets
        Clock.schedule_interval(self.rembullet,0.2)

        #Loading Sounds
        self.shoot_sound = SoundLoader.load('./Sounds/1.wav')
        self.energy_over_sound = SoundLoader.load('./Sounds/2.wav')
        print(self.size)

        #Setting Energy Level(=>10 bullets at max continuesly)
        self.shots = 10
        self.energy = self.shots
        self.charge = 0
        Clock.schedule_interval(self.chragenergy,0.5)
        self.s1_size_y = 0

        #Ship and Bullets 
        self.Bullets = ""
        self.ids.A1.source= ""

    def on_pre_enter(self):
        global Ship, Bullets
        self.ids.A1.source = Ship
        self.Bullets = Bullets

    def ckjoypos(self,_ukt):
        """
            Handles Joystick by not allowing small circle go out of big one.
        """
        #assuming x2,y2 are 0,0
        x1 = self.ids.B1.center[0]
        y1 = self.ids.B1.center[1]
        x2 = self.ids.B2.center[0]
        y2 = self.ids.B2.center[1]

        x22 = x2 - x1
        y22 = y2 - y1

        dist = math.sqrt((x22)**2 + (y22)**2)
        radius = self.ids.B1.size[1]/2
        
        self.angle1 = Vector(x22,y22).angle((self.ids.B1.size[0]/2, 0))
        self.ids.A1.angle = -(90 - self.angle1)

        if dist > radius:
            pcx = radius*(math.cos(self.angle1*(math.pi/180))) + x1
            pcy = radius*(math.sin(self.angle1*(math.pi/180))) + y1
            self.ids.B2.center = (pcx,pcy)
    
    def fire(self,_ukt):
        """
            Fire Sound, Fire and Fire Button
        """
        print(self.Bullets)
        global bullets_widget_garbage,radius,setradius

        if self.energy != 0:
            if setradius == 0:
                #Setting radius
                if Window.size[0] > Window.size[1]: 
                    radius = Window.size[0]
                else:
                    radius = Window.size[1]
                setradius = 1

            
            bullet = Image(source = self.Bullets,size_hint = (None,None))
            bullet.allow_stretch = True
            bullet.size = (self.size[0]/25,self.size[0]/25)
            bullet.pos = (self.ids.A1.center[0] - bullet.size[0]/2,self.ids.A1.center[1]- bullet.size[1]/2)
            with bullet.canvas.before:
                PushMatrix()
                bullet.rotation = Rotate(angle=self.ids.A1.angle, origin=bullet.center)
            with bullet.canvas.after:
                PopMatrix()
            self.ids.FB.add_widget(bullet)

            #Further these bullets widgets are going to be removed
            bullets_widget_garbage.append(bullet)

            v = Vector(bullet.center[0],bullet.center[1]+bullet.size[1]/2).normalize()

            angle_ = Vector(v[0],v[1]).angle((self.size[0]/2,self.size[1]/2)) + 90

            pcx = radius*(math.cos(angle_*(math.pi/180))) + bullet.center[0]
            pcy = radius*(math.sin(angle_*(math.pi/180))) + bullet.center[1]
            #print(pcx,pcy)

            anim = Animation(x = pcx, y = pcy , duration = 6)
            #playing shooting sound
            self.shoot_sound.play()
            anim.start(bullet)
            self.energy -= 1
            x_eb = self.ids.energy_bar.s1pos[0]
            self.ids.energy_bar.s1size[0] = self.seteb*self.energy/self.shots
            self.ids.energy_bar.s1pos[0] = x_eb
        else:
            #Play no-ammo sound
            self.energy_over_sound.play()
    
    def startfire(self):
        #print(self.children)
        global seteb
        if seteb == 1:
            self.seteb = self.ids.energy_bar.s1size[0]
            seteb = 0
        self.charge = 0#charging 'off'
        self.fire(1)
        self.fireC = Clock.schedule_interval(self.fire,0.15)


    def stopfire(self):
        #Charing on after fire and Bullets stop after fire
        self.fireC.cancel()
        self.charge = 1#charging 'on'
    
    def chragenergy(self,_utk):
        if self.charge == 1 and self.energy < self.shots:
            self.energy += 1
            x_eb = self.ids.energy_bar.s1pos[0]
            self.ids.energy_bar.s1size[0] = self.seteb*self.energy/self.shots
            self.ids.energy_bar.s1pos[0] = x_eb

    def rembullet(self,_ukt):
        #Removing Bullets which are outside of Game Window
        global bullets_widget_garbage
        #print(bullets_widget_garbage)
        try:
            bullet = bullets_widget_garbage[0]
            if (bullet.pos[1] > (Window.size[1] + 200)) or (bullet.pos[0] > (Window.size[0] + 200)):
                self.remove_widget(bullet)
                bullets_widget_garbage.remove(bullet)
            elif ((bullet.pos[0] - 200) < 0) or ((bullet.pos[1] - 200) < 0):
                self.ids.FB.remove_widget(bullet)
                bullets_widget_garbage.remove(bullet)
        except IndexError:
            pass

class Menu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #For-Rotation-Animation
        Clock.schedule_interval(self.ckjoypos,0.01)
    
    def ckjoypos(self,_utk):
        self.ids.A11.angle += 1
        if self.ids.A11.angle == 360:
            self.ids.A11.angle = 0
    
    def on_enter(self):
        global Ship, Bullets
        self.ids.A11.source = Ship
        self.ids.BSImg.source = Bullets        

class Settings(Screen):
    pass

class Select_Gun(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.C_L = GridLayout(cols = 4, spacing = 10, size_hint = (None, None), size = (Window.size[0]/2, Window.size[1]))
        self.C_L.bind(minimum_height = self.C_L.setter('height'))
        self.mypath = "./Shoot/"
        onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
        self.liB = []
        for i in range(len(onlyfiles)):    
            self.liB.append(Button(size_hint_y = None, height = 100))
            self.liB[-1].bind(on_press = self.change)
            self.C_L.add_widget(self.liB[-1])
        self.cd = 1
    def change(self,_utk):
        global Bullets
        Bullets = _utk.children[0].source
    def on_enter(self):
        if self.cd == 1:
            onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
            for j in range(len(self.liB)):
                fname = self.mypath + onlyfiles[j]
                img = Image(source = fname,keep_ratio = True)
                self.liB[j].add_widget(img)
                img.pos = self.liB[j].pos
                img.size = self.liB[j].size
                img.center = self.liB[j].center

            self.ids.SV1.add_widget(self.C_L)
            self.cd  = 0

        

class Select_Ship(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.C_L = GridLayout(cols = 4, spacing = 10, size_hint = (None, None), size = (Window.size[0]/2, Window.size[1]))
        self.C_L.bind(minimum_height = self.C_L.setter('height'))
        self.mypath = "./Ship/"
        onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
        self.liB = []
        for i in range(len(onlyfiles)):    
            self.liB.append(Button(size_hint_y = None, height = 100))
            self.liB[-1].bind(on_press = self.change)
            self.C_L.add_widget(self.liB[-1])
        self.cd = 1

    def change(self,_utk):
        global Ship
        Ship = _utk.children[0].source

    def on_enter(self):
        if self.cd == 1:
            onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
            for j in range(len(self.liB)):
                fname = self.mypath + onlyfiles[j]
                img = Image(source = fname,keep_ratio = True)
                self.liB[j].add_widget(img)
                img.pos = self.liB[j].pos
                img.size = self.liB[j].size
                img.center = self.liB[j].center

            self.ids.SV2.add_widget(self.C_L)
            self.cd  = 0

class Game_Over(Screen):
    pass

class Stats(Screen):
    pass

class About(Screen):
    pass

class GameMode(Screen):
    pass

class Club(Screen):
    pass

class Friends(Screen):
    pass

class History(Screen):
    pass


class TestApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Menu(name = 'M_'))
        sm.add_widget(RMassets(name = 'P_G_'))
        sm.add_widget(Select_Gun(name = 'S_G'))
        sm.add_widget(Select_Ship(name = 'S_S'))
        sm.add_widget(Settings(name = 'S_'))
        sm.add_widget(Stats(name = 'STAT'))
        sm.add_widget(About(name = 'ABT_'))
        sm.add_widget(Game_Over(name = 'G_O'))
        sm.add_widget(GameMode(name = 'G_M'))
        sm.add_widget(Club(name = 'C_B'))
        sm.add_widget(Friends(name = 'F_S'))
        sm.add_widget(History(name = 'HIS'))
        
        return sm

bullets_widget_garbage = []

setradius = 0
radius = 0
seteb = 1

#Global User Attributes
Ship = ""
Bullets = ""

#Load User Details(Lite)

with open("User_Data.dat","rb") as User_Data:
    Data = User_Data.read()
    Ship = Data.split(b"|||")[1].decode("ascii")
    Bullets = Data.split(b"|||")[3].decode("ascii")
    print(Ship,Bullets)
    del Data


TestApp().run()