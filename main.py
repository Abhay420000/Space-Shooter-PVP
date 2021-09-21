import math
import threading
import time

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


class DragJS(DragBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

class RMassets(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #For Movement-JoyStick
        Clock.schedule_interval(self.ckjoypos,0.01)

        #For Removal of Waste Widgets
        Clock.schedule_interval(self.rembullet,0.2)

        #Loading Sounds
        self.shoot_sound = SoundLoader.load('./Sounds/1.wav')
        self.energy_over_sound = SoundLoader.load('./Sounds/2.wav')

        #Setting Energy Level(=>10 bullets at max continuesly)
        self.shots = 10
        self.energy = self.shots
        self.charge = 0
        Clock.schedule_interval(self.chragenergy,0.5)
        self.s1_size_y = 0


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
        global bullets_widget_garbage,radius,setradius

        if self.energy != 0:
            if setradius == 0:
                #Setting radius
                if Window.size[0] > Window.size[1]: 
                    radius = Window.size[0]
                else:
                    radius = Window.size[1]
                setradius = 1

            
            bullet = Image(source = "./Shoot/1.png",size_hint = (None,None))
            bullet.allow_stretch = True
            bullet.size = (self.size[0]/25,self.size[0]/25)
            bullet.pos = (self.ids.A1.center[0] - bullet.size[0]/2,self.ids.A1.center[1]- bullet.size[1]/2)
            with bullet.canvas.before:
                PushMatrix()
                bullet.rotation = Rotate(angle=self.ids.A1.angle, origin=bullet.center)
            with bullet.canvas.after:
                PopMatrix()
            self.add_widget(bullet)

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
        self.fireC.cancel()
        self.charge = 1#charging 'on'
    
    def chragenergy(self,_utk):
        if self.charge == 1 and self.energy < self.shots:
            self.energy += 1
            x_eb = self.ids.energy_bar.s1pos[0]
            self.ids.energy_bar.s1size[0] = self.seteb*self.energy/self.shots
            self.ids.energy_bar.s1pos[0] = x_eb

    def rembullet(self,_ukt):
        global bullets_widget_garbage
        #print(bullets_widget_garbage)
        try:
            bullet = bullets_widget_garbage[0]
            if (bullet.pos[1] > (Window.size[1] + 200)) or (bullet.pos[0] > (Window.size[0] + 200)):
                self.remove_widget(bullet)
                bullets_widget_garbage.remove(bullet)
            elif ((bullet.pos[0] - 200) < 0) or ((bullet.pos[1] - 200) < 0):
                self.remove_widget(bullet)
                bullets_widget_garbage.remove(bullet)
        except IndexError:
            pass

class TestApp(App):
    pass

bullets_widget_garbage = []

setradius = 0
radius = 0
seteb = 1

TestApp().run()