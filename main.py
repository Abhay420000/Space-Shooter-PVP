import math
import threading
import time
from os import listdir, path
from os.path import isfile, join
import socket

from kivy.metrics import dp
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core import window
from kivy.core.window import Window
from kivy.graphics.context_instructions import PopMatrix, PushMatrix, Rotate
from kivy.uix.behaviors import DragBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior

class DragJS(DragBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

class RMassets(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_interval(self.ckjoypos, 0.1)

        #For Removal of Waste Widgets
        Clock.schedule_interval(self.rembullet, 0.2)

        #Loading Sounds
        self.shoot_sound = SoundLoader.load('./Sounds/1.wav')
        self.energy_over_sound = SoundLoader.load('./Sounds/2.wav')

        #Setting Energy Level(=>10 bullets at max continuesly)
        self.shots = 10
        self.energy = self.shots
        self.charge = 0
        Clock.schedule_interval(self.chragenergy, 0.5)
        self.s1_size_y = 0

        #Ship and Bullets 
        self.Bullets = ""
        self.ids.A1.source= ""

    def on_pre_enter(self):
        global Ship, Bullets
        self.ids.A1.source = Ship
        self.Bullets = Bullets

    def on_enter(self):
        global setCSize, MJSize, FJSize, setJOri
        
        #Setting Up Size of Joysticks if setCSize = 0, setCSize = 1 means "default"
        if setCSize == str(0):
            self.ids.B0.size = float(FJSize), float(FJSize)
            self.ids.B1.size = float(MJSize), float(MJSize)

        #Setting up positions of Joysticks
        if setJOri == str(1) and self.ids.B1.pos[0] < Window.size[0]/2: 
            #print(p,self.ids.B1.pos,self.ids.B0.pos)
            self.ids.B0.pos = Window.size[0]/8, Window.size[1]/6
            self.ids.B1.pos = Window.size[0]*6/8, Window.size[1]/6
            #print(p,self.ids.B1.pos,self.ids.B0.pos)
        if setJOri == str(0) and self.ids.B1.pos[0] < Window.size[0]/2:
            self.ids.B1.pos = Window.size[0]/8, Window.size[1]/6
            self.ids.B0.pos = Window.size[0]*6/8, Window.size[1]/6

    def ckjoypos(self, _ukt):
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
        
        self.angle1 = Vector(x22, y22).angle((self.ids.B1.size[0]/2, 0))
        self.ids.A1.angle = - (90 - self.angle1)

        if dist > radius:
            pcx = radius*(math.cos(self.angle1*(math.pi/180))) + x1
            pcy = radius*(math.sin(self.angle1*(math.pi/180))) + y1
            self.ids.B2.center = (pcx, pcy)
    
    def fire(self, _ukt):
        """
            Fire Sound, Fire and Fire Button
        """
        global bullets_widget_garbage, radius, setradius

        if self.energy != 0:
            if setradius == 0:
                #Setting radius
                if Window.size[0] > Window.size[1]: 
                    radius = Window.size[0]
                else:
                    radius = Window.size[1]
                setradius = 1

            
            bullet = Image(source = self.Bullets, size_hint = (None, None))
            bullet.allow_stretch = True
            bullet.size = (self.size[0]/25, self.size[0]/25)
            bullet.pos = (self.ids.A1.center[0] - bullet.size[0]/2,self.ids.A1.center[1] - bullet.size[1]/2)
            with bullet.canvas.before:
                PushMatrix()
                bullet.rotation = Rotate(angle=self.ids.A1.angle, origin=bullet.center)
            with bullet.canvas.after:
                PopMatrix()
            self.ids.FB.add_widget(bullet)

            #Further these bullets widgets are going to be removed
            bullets_widget_garbage.append(bullet)

            v = Vector(bullet.center[0],bullet.center[1] + bullet.size[1]/2).normalize()

            angle_ = Vector(v[0], v[1]).angle((self.size[0]/2, self.size[1]/2)) + 90

            pcx = radius * (math.cos(angle_*(math.pi/180))) + bullet.center[0]
            pcy = radius * (math.sin(angle_*(math.pi/180))) + bullet.center[1]
            #print(pcx,pcy)

            anim = Animation(x = pcx, y = pcy , duration = 6)
            #playing shooting sound
            self.shoot_sound.play()
            anim.start(bullet)
            self.energy -= 1
            x_eb = self.ids.energy_bar.s1pos[0]
            self.ids.energy_bar.s1size[0] = self.seteb*self.energy / self.shots
            self.ids.energy_bar.s1pos[0] = x_eb
        else:
            #Play no-ammo sound
            self.energy_over_sound.play()
    
    def startfire(self):
        #print(self.children)
        global seteb,setCSize,MJSize,FJSize
        if seteb == 1:
            self.seteb = self.ids.energy_bar.s1size[0]
            seteb = 0
        self.charge = 0#charging 'off'
        self.fire(1)
        self.fireC = Clock.schedule_interval(self.fire, 0.15)
        if setCSize == str(1):
            #print(setCSize)
            setCSize = str(0)
            FJSize = str(self.ids.B0.size[1])
            MJSize = str(self.ids.B1.size[1])
            update_User_Data()
            print(1)


    def stopfire(self):
        #Charing on after fire and Bullets stop after fire
        self.fireC.cancel()
        self.charge = 1#charging 'on'
    
    def chragenergy(self, _utk):
        if self.charge == 1 and self.energy < self.shots:
            self.energy += 1
            x_eb = self.ids.energy_bar.s1pos[0]
            self.ids.energy_bar.s1size[0] = self.seteb*self.energy / self.shots
            self.ids.energy_bar.s1pos[0] = x_eb

    def rembullet(self, _ukt):
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

    def on_touch_down(self, touch):
        if self.ids.B2.collide_point(*touch.pos):
            print("On")
        return super(RMassets, self).on_touch_down(touch)
    def on_touch_up(self, touch):
        if self.ids.B2.collide_point(*touch.pos):
            print("Off")
        return super(RMassets, self).on_touch_up(touch)

class Menu(Screen):
    
    def __init__(self, **kwargs):

        global GMode

        super().__init__(**kwargs)

        #For-Rotation-Animation
        Clock.schedule_interval(self.ckjoypos, 0.01)

        #For-Game-Mode-Display
        self.ids.GMD.text = GMode

    def on_enter(self):
        global Ship, Bullets, GMode

        self.ids.A11.source = Ship
        self.ids.BSImg.source = Bullets
        self.ids.GMD.text = GMode

    
    def ckjoypos(self, _utk):
        self.ids.A11.angle += 1
        if self.ids.A11.angle == 360:
            self.ids.A11.angle = 0
           

class Settings(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global Audio, Sound
        self.ids.SAOF.text = "Audio:" + Audio
        self.ids.SSOF.text = "Sound:" + Sound

        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'        

    def setaudio_OF(self):
        global Audio
        if self.ids.SAOF.text.split(':')[1] == "On":
            self.ids.SAOF.text = "Audio:Off"
            Audio = "Off"
        else:
            self.ids.SAOF.text = "Audio:On"
            Audio = "On"
        #print(Audio)
        update_User_Data()

    def setsound_OF(self):
        global Sound
        if self.ids.SSOF.text.split(':')[1] == "On":
            self.ids.SSOF.text = "Sound:Off"
            Sound = "Off"
        else:
            self.ids.SSOF.text = "Sound:On"
            Sound = "On"
        #print(Sound)
        update_User_Data()      

class Select_Gun(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.C_L = GridLayout(cols = 4, spacing = 0, size_hint = (None, None), size = (Window.size[0]/2, Window.size[1]))
        self.C_L.bind(minimum_height = self.C_L.setter('height'))
        self.mypath = "./Shoot/"
        onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
        self.liB = []
        
        for i in range(len(onlyfiles)):    
            self.liB.append(Button(size_hint_y = None, size_hint_x = None,width =  Window.size[0]/8, height = Window.size[0]/8, on_press = self.Display))
            #self.liB[-1].bind(pos = self.update_rect, size = self.update_rect)
            self.C_L.add_widget(self.liB[-1])
        self.cd = 1

        Window.bind(on_keyboard = self.Android_back_click)


    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'

    def on_pre_enter(self):
        self.LoadingAnim = Lding()
        self.add_widget(self.LoadingAnim)

    def on_enter(self):
        global Bullets
        #print(Bullets)
        self.LoadingAnim.incbyoneone(20,0.1)
        if self.cd == 1:
            onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
            for j in range(len(self.liB)):
                fname = self.mypath + onlyfiles[j]
                img = Image(source = fname, keep_ratio = True, allow_stretch = True)
                self.liB[j].add_widget(img)
                if (Bullets == fname):
                    self.liB[j].disabled = True
                img.pos = self.liB[j].pos
                img.size = self.liB[j].size[0]/2, self.liB[j].size[0]/2
                img.center = self.liB[j].center

            self.ids.SV1.add_widget(self.C_L)
            self.cd  = 0
        
        #Displaying details of gun while entering
        self.Display()

        self.remove_widget(self.LoadingAnim)

    def Display(self, *args):
        """
            Details of Guns is Displayed
        """

        global Bullets

        #Enabling Previous one
        for i in range(len(self.liB)):
            if (self.liB[i].disabled == True) and (args != ()):
                self.liB[i].disabled = False
                break

        #Disabling Current One
        if (args != ()):
            args[0].disabled = True

        #Clearing Initial Display
        self.ids.Prev_It.clear_widgets()

        try:
            Bullet_Name = args[0].children[0].source
            if Bullets == Bullet_Name:
                set_disable = True
            else:
                set_disable = False
        except:
            Bullet_Name = Bullets
            set_disable = True

        #Finding Bullet Info
        data = open("./Data/Gun_Res.dat","r")
        dline = data.read().split("\n")
        fdata = ""

        for i in range(1,len(dline)):
            sline = dline[i].split(":")
            if f"./Shoot/{sline[0]}" == Bullet_Name:
                fdata = sline[1]
                break
        data.close()

        fdata = fdata.split("-")

        #Adding New Display
        self.ids.Prev_It.add_widget(Label(text = fdata[0], font_name = "./Fonts/BadComic.ttf", font_size = dp(42)))
        self.ids.Prev_It.add_widget(Image(source = Bullet_Name, keep_ratio = True, allow_stretch = True))
        Container = BoxLayout(orientation = "vertical")

        Container.add_widget(Label(text = f"Damage = {fdata[1]}", font_name = "./Fonts/ComicShark.otf", font_size = dp(25)))
        Container.add_widget(Label(text = f"Ammo = {fdata[3]}", font_name = "./Fonts/ComicShark.otf", font_size = dp(25)))
        if fdata[5] == "L":
            Container.add_widget(Label(text = f"Price = {fdata[6]}", font_name = "./Fonts/ComicShark.otf", font_size = dp(25)))
        self.ids.Prev_It.add_widget(Container)
        self.selection = Bullet_Name

        if fdata[5] == "UnL":
            btn_eqp = Button(text = "Equip", on_press = self.change, size_hint = (1,0.5))
            self.ids.Prev_It.add_widget(btn_eqp)
            if set_disable:
                btn_eqp.disabled = True
                btn_eqp.text = "Equiped"
        else:
            self.ids.Prev_It.add_widget(Button(text = "Buy", size_hint = (1,0.5)))

    def change(self, _utk):
        """
            Function Binded with "Equip" Button get fired when "Equip" button pressed
        """
        global Bullets
        Bullets = self.selection
        _utk.text = "Equiped"
        _utk.disabled = True

    def on_leave(self):
        self.ids.Prev_It.clear_widgets()
        update_User_Data()

        

class Select_Ship(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.C_L = GridLayout(cols = 4, spacing = 0, size_hint = (None, None), size = (Window.size[0]/2, Window.size[1]))
        self.C_L.bind(minimum_height = self.C_L.setter('height'))
        self.mypath = "./Ship/"
        onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
        self.liB = []
        for i in range(len(onlyfiles)):    
            self.liB.append(Button(size_hint_y = None, size_hint_x = None, width =  Window.size[0]/8, height = Window.size[0]/8, on_press = self.Display))
            #self.liB[-1].bind()
            self.C_L.add_widget(self.liB[-1])
        self.cd = 1

        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'

    def on_pre_enter(self):
        self.LoadingAnim = Lding()
        self.add_widget(self.LoadingAnim)

    def on_enter(self):
        global Ship
        self.LoadingAnim.incbyoneone(20,0.1)
        if self.cd == 1:
            onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
            for j in range(len(self.liB)):
                fname = self.mypath + onlyfiles[j]
                img = Image(source = fname, keep_ratio = True, allow_stretch =True)
                self.liB[j].add_widget(img)
                if (Ship == fname):
                    self.liB[j].disabled = True
                img.pos = self.liB[j].pos
                img.size = self.liB[j].size[0]/2, self.liB[j].size[0]/2
                img.center = self.liB[j].center

            self.ids.SV2.add_widget(self.C_L)
            self.cd  = 0

        self.Display()

        self.remove_widget(self.LoadingAnim)

    def Display(self, *args):
        """
            Details of Ships is Displayed
        """

        global Ship

        #Enabling Previous one
        for i in range(len(self.liB)):
            if (self.liB[i].disabled == True) and (args != ()):
                self.liB[i].disabled = False
                break

        #Disabling Current One
        if (args != ()):
            args[0].disabled = True

        #Clearing Initial Display
        self.ids.Prev_It.clear_widgets()

        try:
            Ship_Name = args[0].children[0].source
            if Ship == Ship_Name:
                set_disable = True
            else:
                set_disable = False
        except:
            Ship_Name = Ship
            set_disable = True

        #Finding Bullet Info
        data = open("./Data/Ship_Res.dat","r")
        dline = data.read().split("\n")
        fdata = ""

        for i in range(1,len(dline)):
            sline = dline[i].split(":")
            if f"./Ship/{sline[0]}" == Ship_Name:
                fdata = sline[1]
                break
        data.close()

        fdata = fdata.split("-")

        #Adding New Display
        self.ids.Prev_It.add_widget(Label(text = fdata[0], font_name = "./Fonts/BadComic.ttf", font_size = dp(42)))
        self.ids.Prev_It.add_widget(Image(source = Ship_Name, keep_ratio = True, allow_stretch = True))
        Container = BoxLayout(orientation = "vertical")

        Container.add_widget(Label(text = f"Health = {fdata[1]}", font_name = "./Fonts/ComicShark.otf", font_size = dp(25)))
        if fdata[2] == "L":
            Container.add_widget(Label(text = f"Price = {fdata[3]}", font_name = "./Fonts/ComicShark.otf", font_size = dp(25)))
        self.ids.Prev_It.add_widget(Container)
        self.selection = Ship_Name

        if fdata[2] == "UnL":
            btn_eqp = Button(text = "Equip", on_press = self.change, size_hint = (1,0.5))
            self.ids.Prev_It.add_widget(btn_eqp)
            if set_disable:
                btn_eqp.disabled = True
                btn_eqp.text = "Equiped"
        else:
            self.ids.Prev_It.add_widget(Button(text = "Buy", size_hint = (1,0.5)))

    def change(self, _utk):
        """
            Function Binded with "Equip" Button get fired when "Equip" button pressed
        """
        global Ship
        Ship = self.selection
        _utk.text = "Equiped"
        _utk.disabled = True

    def on_leave(self):
        self.ids.Prev_It.clear_widgets()
        update_User_Data()

class Game_Over(Screen):
    pass

class Stats(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'
    
    def on_pre_enter(self):
        self.Loading = Lding()
        self.add_widget(self.Loading)
        self.Loading.incbyoneone(15,0.05)
    
    def on_enter(self):
        with open("./Data/Player_Stats.dat", "rb") as pdata:
            pfdata = pdata.read()

        pfdata = pfdata.decode()
        pfdata = pfdata.split("\r\n")

        self.ids.res_d.add_widget(Label(text=pfdata[0]))
        self.ids.res_d.add_widget(Label(text=pfdata[1]))
        self.ids.res_d.add_widget(Label(text=pfdata[2]))
        self.ids.res_d.add_widget(Label(text=pfdata[3]))
        self.ids.res_d.add_widget(Label(text=pfdata[4]))
        self.ids.res_d.add_widget(Label(text=pfdata[5]))
        self.ids.res_d.add_widget(Label(text=pfdata[6]))
        self.Loading.incrementLoading(100)
        self.remove_widget(self.Loading)

    def on_leave(self):
        self.ids.res_d.clear_widgets()

class About(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'

class GameMode(Screen):
    def __init__(self, **kwargs):
        super(GameMode, self).__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'
    
    def change_mode(self, mode):
        global GMode
        GMode = mode
    
    def on_leave(self):
        update_User_Data()

class Club(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'
    
    def on_pre_enter(self):
        #Adding Loading Widget
        self.Loading = Lding()
        self.add_widget(self.Loading)

        #Starting Loading
        self.Loading.incbyoneone(15,0.05)

    def on_enter(self):
        #Adding Table Note-Size Control while resize needs to be added
        self.gd = GridLayout(cols = 4, size_hint = (None, None), size = self.ids.SV2.size)
        
        with open('./Data/Club_Data.dat', "rb") as rd:
            self.Data = rd.read()
        self.Data = self.Data.split(b"\r\n")
        while b"" in self.Data:
            self.Data.remove(b"")
        self.cd = len(self.Data) - 1

        self.Data = self.Data[1::]
        
        self.s = Clock.schedule_interval(self.load,0.001)
    
    def load(self, _utk):
        #print(self.cd - len(self.Data) - 1)
        if self.cd != 0:
            DR = self.Data[self.cd - len(self.Data) - 1].decode()
            DR = DR.split('|||')
            self.gd.add_widget(Label(text = DR[0], size_hint= (None, None), size = (self.gd.size[0]/4, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[1], size_hint= (None, None), size = (self.gd.size[0]/4, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[2], size_hint= (None, None), size = (self.gd.size[0]/4, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[3], size_hint= (None, None), size = (self.gd.size[0]/4, self.gd.size[1]/4)))     
            self.cd -= 1

        if self.cd == 0:
            self.Loading.incrementLoading(80)
            self.ids.SV2.add_widget(self.gd)
            self.gd.bind(minimum_height = self.gd.setter('height'))
            #Loading Ended Removing Loading Widget
            self.Loading.incrementLoading(100)
            self.remove_widget(self.Loading)
            self.s.cancel()

    def on_leave(self):
        self.gd.clear_widgets()
        self.ids.SV2.clear_widgets()

class Friends(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)
        

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'

    def on_pre_enter(self):
        #Adding Loading Widget
        self.Loading = Lding()
        self.add_widget(self.Loading)

        #Starting Loading
        self.Loading.incbyoneone(15,0.05)

    def on_enter(self):
        #Adding Table Note-Size Control while resize needs to be added
        self.gd = GridLayout(cols = 3, size_hint = (None, None), size = self.ids.SV2.size)
        
        with open('./Data/Friends_Data.dat', "rb") as rd:
            self.Data = rd.read()
        self.Data = self.Data.split(b"\r\n")
        while b"" in self.Data:
            self.Data.remove(b"")
        self.cd = len(self.Data) - 1

        self.Data = self.Data[1::]
        print(self.Data)
        on = []
        of = []
        for i in range(len(self.Data)):
            if self.Data[i].split(b"|||")[3] == b"Offline":
                of.append(self.Data[i])
            else:
                on.append(self.Data[i])

        self.Data = of+on

        self.s = Clock.schedule_interval(self.load,0.001)
    
    def load(self, _utk):
        #print(self.cd - len(self.Data) - 1)
        if self.cd != 0:
            DR = self.Data[self.cd - len(self.Data) - 1].decode()
            DR = DR.split('|||')
            self.gd.add_widget(Label(text = DR[1], size_hint= (None, None), size = (self.gd.size[0]/3, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[2], size_hint= (None, None), size = (self.gd.size[0]/3, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[3], size_hint= (None, None), size = (self.gd.size[0]/3, self.gd.size[1]/4)))
            self.cd -= 1
        if self.cd == 0:
            self.Loading.incrementLoading(80)
            self.ids.SV2.add_widget(self.gd)
            self.gd.bind(minimum_height = self.gd.setter('height'))
            #Loading Ended Removing Loading Widget
            self.Loading.incrementLoading(100)
            self.remove_widget(self.Loading)
            self.s.cancel()

    def on_leave(self):
        self.gd.clear_widgets()
        self.ids.SV2.clear_widgets()

class History(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'

    def on_pre_enter(self):
        #Adding Loading Widget
        self.Loading = Lding()
        self.add_widget(self.Loading)

        #Starting Loading
        self.Loading.incbyoneone(15,0.05)

    def on_enter(self):
        #Adding Table Note-Size Control while resize needs to be added
        self.gd = GridLayout(cols = 5, size_hint = (None, None), size = self.ids.SV2.size)
        
        with open('./Data/Replay_Data.dat', "rb") as rd:
            self.Data = rd.read()
        self.Data = self.Data.split(b"\r\n")
        while b"" in self.Data:
            self.Data.remove(b"")
        self.cd = len(self.Data)

        self.s = Clock.schedule_interval(self.load,0.001)
    
    def load(self, _utk):
        #print(self.cd - len(self.Data) - 1)
        if self.cd != 0:
            DR = self.Data[self.cd - len(self.Data) - 1].decode()
            DR = DR.split('|||')
            self.gd.add_widget(Label(text = DR[0], size_hint= (None, None), size = (self.gd.size[0]/5, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[1], size_hint= (None, None), size = (self.gd.size[0]/5, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[2], size_hint= (None, None), size = (self.gd.size[0]/5, self.gd.size[1]/4)))
            self.gd.add_widget(Label(text = DR[3], size_hint= (None, None), size = (self.gd.size[0]/5, self.gd.size[1]/4)))
            self.gd.add_widget(Button(text = "Play", size_hint= (None, None), size = (self.gd.size[0]/5, self.gd.size[1]/4)))
            self.cd -= 1
        if self.cd == 0:
            self.Loading.incrementLoading(80)
            self.ids.SV2.add_widget(self.gd)
            self.gd.bind(minimum_height = self.gd.setter('height'))
            #Loading Ended Removing Loading Widget
            self.Loading.incrementLoading(100)
            self.remove_widget(self.Loading)
            self.s.cancel()

    def on_leave(self):
        self.gd.clear_widgets()
        self.ids.SV2.clear_widgets()

class CUpdate(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        self.LoadingAnim = Lding()
        self.add_widget(self.LoadingAnim)

    def on_enter(self):
        """
            Setting Sider's value, Joy Stick Sizes after just entering
            and Swaping Joystick Sizes
        """
        self.LoadingAnim.incbyoneone(10, 0.001)#Starting Loading
        #Disabling Buttons while Loading
        self.ids.hpg.disabled = True
        self.ids.SPit.disabled = True

        global MJSize, FJSize, setJOri
        
        self.ids.slider0.value = float(MJSize)
        self.ids.slider1.value = float(FJSize)
        self.ids.MJI.size1 = (float(MJSize), float(MJSize))
        self.ids.FJI.size2 = (float(FJSize), float(FJSize))
        
        if setJOri == str(1):
            s = self.ids.PL.children[0]
            if s.pos == self.ids.FJI.pos:
                self.ids.PL.children[0] = self.ids.PL.children[1]
                self.ids.PL.children[1] = s
                s = self.ids.PL.children[2]
                self.ids.PL.children[2] = self.ids.PL.children[3]
                self.ids.PL.children[3] = s
                s = self.ids.PL.children[4]
                self.ids.PL.children[4] = self.ids.PL.children[5]
                self.ids.PL.children[5] = s

        self.LoadingAnim.incrementLoading(100)#Loading Compleated
        
        #Enabling Buttons after Loading
        self.ids.hpg.disabled = False
        self.ids.SPit.disabled = False


        self.remove_widget(self.LoadingAnim)#Removing Loading Widget


    def incMJS(self):
        """
            Change Movement Joystick Size
        """
        global MJSize
        MJSize = str(self.ids.slider0.value)#Updating
        self.ids.MJI.size1 = (float(MJSize), float(MJSize))

    def incFJS(self):
        """
            Change Fire Joystick Size
        """
        global FJSize
        FJSize = str(self.ids.slider1.value)#Updating
        self.ids.FJI.size2 = (float(FJSize), float(FJSize))
    
    def swapit(self):
        """
        Swaping Root Widget Right Side Childeren to Left Side Ones
        """
        global setJOri
        s = self.ids.PL.children[0]
        self.ids.PL.children[0] = self.ids.PL.children[1]
        self.ids.PL.children[1] = s
        s = self.ids.PL.children[2]
        self.ids.PL.children[2] = self.ids.PL.children[3]
        self.ids.PL.children[3] = s
        s = self.ids.PL.children[4]
        self.ids.PL.children[4] = self.ids.PL.children[5]
        self.ids.PL.children[5] = s

        if int(self.ids.MJI.pos[0]) == 0:
            setJOri = str(1)
        else:
            setJOri = str(0)
        print(setJOri)
        update_User_Data()


    def on_leave(self):
        global setCSize
        if setCSize == str(1):
            """For the frist time if user change its controls just after instaling game
            Without Playing"""
            setCSize = str(0)
            update_User_Data()
        else:
            update_User_Data()

class FeedBack(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard = self.Android_back_click)

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            self.manager.current = 'M_'

#Loading Widget
class Lding(Widget):
    def __init__(self, **kwargs):
        super(Lding, self).__init__(**kwargs)
        self.loading_value = 0
        self.value = 0
        with self.canvas:
            Color(0, 0, 0)
            #Seting the size and position of canvas
            self.rect = Rectangle(pos = self.center,
                                  size =(self.width / 2., self.height / 2.))
            Color(1, 1, 0, 1)#Loading Back Color
            self.s1 = RoundedRectangle(pos = (Window.size[0]/1000, Window.size[1]/1000),
                                       size = (Window.size[0] - Window.size[0]/1000, Window.size[1]/20))
            
            Color(1,0,1,1)#Loading Front Color
            self.s2 = RoundedRectangle(pos = (Window.size[0]/1000, Window.size[1]/1000 + self.s1.size[1]/20),
                                       size = (self.loading_value, Window.size[1]/20 - self.s1.size[1]/10))

            # Update the canvas as the screen size change
            self.bind(pos = self.update_rect, size = self.update_rect)
        
        self.L1 = Label(text = "Loading ...",)
        self.L1.size = (Window.size[0]*0.1, Window.size[0]*0.05)
        self.L1.pos = (Window.center[0] - self.L1.size[0]/2, Window.size[1]/20)
        self.add_widget(self.L1)
        self.L1.bind(pos = self.update_rect, size = self.update_rect)
  
    #Update function which makes the canvas adjustable
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.s1.pos = (Window.size[0]/1000, Window.size[1]/1000)
        self.s1.size = (Window.size[0] - Window.size[0]/1000, Window.size[1]/20)
        self.s2.pos = (Window.size[0]/1000, Window.size[1]/1000 + self.s1.size[1]/20)
        self.s2.size = (self.loading_value, Window.size[1]/20 - self.s1.size[1]/10)
        self.L1.pos = (Window.center[0] - self.L1.size[0]/2, Window.size[1]/20)
        self.L1.size = (Window.size[0]*0.1, Window.size[0]*0.05)

    
    def incrementLoading(self, n):
        """
            Used to assign the size of Loading bar.
        
            n = Provide how much percentage of Loading screen you want to fill or compleate
            int,range(0,100)
        """
        n = (Window.size[0]*n)/100
        if self.s2.size[0]+n < Window.size[0] - Window.size[0]/1000:
            self.loading_value = self.s2.size[0] + n
            self.s2.size = (self.s2.size[0] + n, self.s2.size[1])
        else:
            self.loading_value = Window.size[0] - Window.size[0]/1000
            self.s2.size = (Window.size[0] - Window.size[0]/1000, self.s2.size[1])
    
    def incbyoneone(self, value, time):
        """
            Used to increment the size of loading bar in interval.

            value = incrementing value in pixels
            time = incrementing interval
        """
        self.i1 = Clock.schedule_interval(self.incSz1, time)
        self.value = value
    
    def incSz1(self, _utk):
        if self.s2.size[0]+self.value < Window.size[0] - Window.size[0]/1000:
            self.loading_value = self.s2.size[0] + self.value
            self.s2.size = (self.s2.size[0] + self.value, self.s2.size[1])
        elif self.s2.size[0]+self.value == Window.size[0] - Window.size[0]/1000:
            self.i1.cancel()
        else:
            self.loading_value = Window.size[0] - Window.size[0]/1000
            self.s2.size = (Window.size[0] - Window.size[0]/1000, self.s2.size[1])


def update_User_Data():
    """
        Used to update user details.
        Called whenever user's game details changed by him.
    """
    global Audio, Ship, Bullets, Sound, MJSize, FJSize, setCSize, setJOri, GMode
    UDW = open("./Data/User_Data.dat", "wb")
    UDW.write(f'Ship|||{Ship}|||Bullets|||{Bullets}|||Audio|||{Audio}|||Sound|||{Sound}|||MJSize|||{MJSize}|||FJSize|||{FJSize}|||setCSize|||{setCSize}|||setJOri|||{setJOri}|||GMode|||{GMode}'.encode())
    UDW.close()

class TestApp(App):
    def build(self):

        sm = ScreenManager(transition = NoTransition())
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
        sm.add_widget(CUpdate(name = 'CUP'))
        sm.add_widget(FeedBack(name = 'FDB'))

        return sm  

#used for collecting garbage bullets that goes out of screen
bullets_widget_garbage = []

setradius = 0
radius = 0
seteb = 1

#Global User Attributes
Ship = ""
Bullets = ""
Audio = ""
Sound = ""
MJSize = ""
FJSize = ""
setCSize = ""
setJOri = ""
GMode = ""

#Load User Details(Lite)
with open("./Data/User_Data.dat","rb") as User_Data:
    Data = User_Data.read().decode("ascii").split("|||")

    Ship = Data[1]
    Bullets = Data[3]
    Audio = Data[5]
    Sound = Data[7]
    MJSize = Data[9]
    FJSize = Data[11]
    setCSize = Data[13]
    setJOri = Data[15]
    GMode = Data[17]
    
    del Data#No neeed of Data


TestApp().run()