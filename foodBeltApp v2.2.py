# -*- coding: utf-8 -*-
import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import BooleanProperty
from kivy.graphics import Rectangle
from firebase import firebase
import datetime

now = datetime.datetime.now()
url = "https://internetofthings-f6256.firebaseio.com/" # URL to Firebase database
token = "CRCZ9IiX8uZCHPuD0dOYJ1XO2rSKjYzEAeUqrRPt" # unique token used for authentication
firebase = firebase.FirebaseApplication(url, token)
highTemp = 320
highHum = 80
food_list = []
dayMonthList = [31,28,31,30,31,30,31,31,30,31,30,31]
high_temp_img = "high_temp.png"
low_temp_img = "low_temp.png"
high_hum_img = "high_hum.png"
low_hum_img = "low_hum.png"
fresh_img = "fresh.png"
refresh_img = "refresh.png"
alarm_on_img = "alarm_on.png"
alarm_off_img = "alarm_off.png"
background_img = "background.jpg"
expiring_img = "expiring.png"
expired_img = "expired.png"
highlight_img = "highlight.png"

#Testing data
food_list_test= [["Celery","050317",True],["Will to Live","100317",None],["Carrot","011218",None],["Potato","121219",None]]
temperature_list,humidity_list = [1],[1]

############### debug
#firebase.put("/","food",food_list_test)  
day,month,year = str(now.day),str(now.month),str(now.year - 2000)
while len(day) < 2:
    day = "0" + day
while len(month) < 2:
    month = "0" + month
food_list_test.append(["Hopes and Dreams",day+month+year,None])
firebase.put('/','food',[temperature_list,humidity_list,food_list_test])
############## debug

############################# Main Functions ##################################
def is_high_temp(tempList):
    counter = 0
    for item in tempList:
        if item > highTemp:
            counter+=1
        else:
            counter = 0
        if counter > 1:
            return True
    return False
def update_food_list(itemIndex,newItem):
    food_list[itemIndex] = newItem
def update_firebase():
    firebase.put('/','food',[temperature_list,humidity_list,food_list])
def connected():
    try:
        firebase_list = firebase.get('/food')
        global temperature_list,humidity_list,food_list
        temperature_list = firebase_list[0]
        humidity_list = firebase_list[1]
        food_list = firebase_list[2]
        for food in food_list:
            if len(food)==2:
                food.append(None)
        print "connected"
        return True
    except Exception as e:
        print firebase_list
        print "error", e
        return False
def is_leap_year(year):
    if year%4==0:
        if year%100==0:
            return year%400==0
        else:
            return True
    else:
        return False

def time_to_expiry(date):
    dayNow,monthNow,yearNow = now.day, now.month,now.year
    dayExp,monthExp,yearExp = int(date[:2]),int(date[2:4]),int(date[4:])+2000
    
    numOfDays = (datetime.date(yearExp,monthExp,dayExp) - datetime.date(yearNow,monthNow,dayNow)).days
    singular = ""
    
    if yearNow > yearExp or (yearNow == yearExp and (monthNow > monthExp or monthNow == monthExp and dayNow > dayExp) ):
        return "Expired"
    elif dayNow == dayExp and monthNow == monthExp and yearNow == yearExp:
        return "Today"
    elif numOfDays // 365 >= 1:
        if numOfDays // 365 > 1: singular = "s"
        return "%d year%s" %(numOfDays//365,singular)
    elif numOfDays // 30.5 >= 2:
        return "%d months" %(numOfDays//30)
    elif numOfDays // 7 >= 1:
        if numOfDays // 7 > 1: singular = "s"
        return "%d week%s" %(numOfDays//7,singular)
    elif numOfDays >= 1:
        if numOfDays > 1: singular = "s"
        return "%d day%s" %(numOfDays,singular)
def near_expiry(duration_str):
    return duration_str[len(duration_str)-3:] == 'day' or duration_str[len(duration_str)-4:]== 'days'
    
############################# Main Functions ##################################

################################# Classes #####################################
########## Screens ##################
class MyScreenManager(ScreenManager):
    pass
sm = MyScreenManager()
class ConnErrorScreen(Screen):
    def __init__(self,**kwargs):
        super(ConnErrorScreen,self).__init__(**kwargs)
        self.name = "connerror"
        self.add_widget(Label(text = "Error connecting to firebase, please check connection and restart App"))

class HomeScreen(Screen):
    def __init__(self,**kwargs):
        super(HomeScreen,self).__init__(**kwargs)
        self.name = "home"
        if not connected():
            self.add_widget(ConnErrorScreen())
            return
        self.root = GridLayout(rows = 6)
        if temperature_list[-1] > highTemp:
            self.root.add_widget(Image(source = high_temp_img,size_hint = (.5,.2)))
        else:
            self.root.add_widget(Image(source = low_temp_img,size_hint = (.5,.2)))
        self.root.add_widget(Label(text = "Temperature: %d "%(temperature_list[-1]) + u'\N{DEGREE SIGN}'+ 'C',size_hint = (.5,.1),color=[0,0,0,1]))
        if humidity_list[-1] > highHum:
            self.root.add_widget(Image(source = high_hum_img,size_hint = (.5,.2)))
        else:
            self.root.add_widget(Image(source = low_hum_img,size_hint = (.5,.2)))
        self.root.add_widget(Label(text="Humidity: %d %%"%(humidity_list[-1]),size_hint=(.5,.1),color=[0,0,0,1]))
        if "Expired" in [time_to_expiry(food[1]) for food in food_list]:
            self.root.add_widget(Image(source = expired_img,size_hint=(.5,.2)))
        else:
            self.root.add_widget(Image(source = fresh_img,size_hint=(.5,.2)))
        self.root.add_widget(FoodButton(text="View food",size_hint=(.5,.2),color=[0,0,0,1]))
        self.add_widget(Image(source = background_img,size_hint=(1,1),keep_ratio = False,allow_stretch=True))
        self.add_widget(self.root)
    
    
        

class FoodScreen(Screen):
    def __init__(self,**kwargs):
        super(FoodScreen,self).__init__(**kwargs)
        self.name = "food"
        if not connected():
            self.add_widget(ConnErrorScreen())
            return
            
        self.scrollView = ScrollView(
                            do_scroll_x = False,
                            do_scroll_y = True,
                            size_hint = (1,.8),
                            id = "food_scroll")
        # Headers
        self.headers = GridLayout(cols = 3, size_hint=(1,.1))
        self.headers.add_widget(Label(text="Name",size_hint=(.4,1),color=[0,0,0,1]))
        self.headers.add_widget(Label(text="Time until Expiry",size_hint=(.4,1),color=[0,0,0,1]))
        self.headers.add_widget(RefreshButton(source = refresh_img,size_hint=(.2,1)))
        
        # MainGrid containing everything
        self.mainGrid = GridLayout(rows = 3)
        
        # FoodGrid containing FoodGrid rows containing food items
        self.foodGrid = GridLayout(cols=3,row_force_default=True, row_default_height=50,size_hint_y=None)

        for food in food_list:
            self.foodGrid.add_widget(Label(text = food[0],size_hint=(.4,.2),color=[0,0,0,1]))
            self.foodGrid.add_widget(Label(text = time_to_expiry(food[1]),size_hint=(.4,.2),color=[0,0,0,1]))
            if near_expiry(time_to_expiry(food[1])):
                self.foodGrid.add_widget(Image(source = expiring_img,size_hint=(.2,.2)))
            elif time_to_expiry(food[1]) == "Expired":
                self.foodGrid.add_widget(Image(source = expired_img,size_hint=(.2,.2)))
            else:
                self.foodGrid.add_widget(Label(text = "",size_hint=(.2,.2),color=[0,0,0,1]))
            
        # Make sure the height is such that there is something to scroll.
        self.foodGrid.bind(minimum_height = self.foodGrid.setter('height'))
        self.scrollView.add_widget(self.foodGrid)
        # Footer
        self.footer = GridLayout(cols = 3,size_hint=(1,.1))
        self.removeButton = Button(text="Remove",size_hint = (.3,1),color=[0,0,0,1])
        self.buzzerButton = BuzzerButton(source = alarm_on_img,size_hint =(.4,1))
        self.buzzerButton.bind(pressed = self.remove_buzzer)
        self.homeButton = HomeButton(text = "Home",size_hint=(.4,1),color=[0,0,0,1])
        self.addButton = AddButton(text = "Add new entry",size_hint = (.3,1),color=[0,0,0,1])
        
        self.footer.add_widget(self.removeButton)
        
        if (True in [food[2] for food in food_list]):
            self.footer.add_widget(self.buzzerButton)
        else:
            self.footer.add_widget(self.homeButton)
        self.footer.add_widget(self.addButton)
        
        
        self.mainGrid.add_widget(self.headers)
        self.mainGrid.add_widget(self.scrollView)
        self.mainGrid.add_widget(self.footer)
        self.add_widget(Image(source = background_img, size_hint=(1,1),keep_ratio = False,allow_stretch=True))
        self.add_widget(self.mainGrid)

    def remove_buzzer(self,instance,value):
        self.footer.remove_widget(self.buzzerButton)
        self.footer.remove_widget(self.addButton)
        self.footer.add_widget(self.homeButton)
        self.footer.add_widget(self.addButton)
        
    def update_highlight(self,instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size




                
class AddScreen(Screen):
    validList = [False] * 2
    validateLabelList = []
    textInputList = [0,0]
    def __init__(self,**kwargs):
        super(AddScreen,self).__init__(**kwargs)
        self.name = "add"
        self.root = GridLayout(rows = 2)
        self.inputStack = StackLayout(orientation='lr-tb', size_hint=(1,.8))
        self.inputStack.add_widget(Label(text="Name",size_hint=(.6,.1),color=[0,0,0,1]))
        self.inputStack.add_widget(Label(text="Expiry Date",size_hint=(.4,.1),color=[0,0,0,1]))
        for key,x_pos in zip(["name","expiry"],[.6,.4]):
            textInput = TextInput(id = key + "input",
                          multiline = False,
                          size_hint=(x_pos,.1))
            textInput.bind(text=self.check_input)
            self.inputStack.add_widget(textInput)
        for key,x_pos in zip(["name","expiry"],[.6,.4]):
            validateLabel = ValidateLabel(id = key + "label",
                                  size_hint = (x_pos,.1),
                                  shorten = True,
                                  color = [0,0,0,1])
            self.validateLabelList.append(validateLabel)
            self.inputStack.add_widget(validateLabel)
        self.buttonStack = StackLayout(orientation='bt-lr', size_hint=(1,.2))
        self.root.add_widget(self.inputStack)
        self.buttonStack.add_widget(FoodButton(text="Back",size_hint=(1,.5),color=[0,0,0,1]))
        self.root.add_widget(self.buttonStack)
        self.add_widget(Image(source = background_img,size_hint=(1,1),keep_ratio = False,allow_stretch=True))
        self.add_widget(self.root)
            
    def check_input(self,instance,text):
        if instance.id == "nameinput":
            validListIndex = 0
            for char in text:
                if char not in '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM ':
                    self.validList[0] = False
                    break
            else:
                if text != '':
                    self.validList[0] = True
                else:
                    self.validList[0] = False
        elif instance.id == "expiryinput":
            validListIndex = 1
            if len(text) == 6:
                for char in text:
                    if char not in '0123456789':
                        self.validList[1] = False
                        break
                else:
                    day,month,year = int(text[:2]),int(text[2:4]),int(text[4:6])+2000
                    
                    if month>12 or month <= 0 or day > dayMonthList[month-1]: 
                        self.validList[1] = False
                    else:
                        #Check if input date is in the past or today
                        if (year < now.year) or (year == now.year and (month < now.month or month == now.month and day <= now.day)):
                            self.validList[1] = False
                        else:
                            self.validList[1] = True
            else:
                self.validList[1] = False
                    
        else:
            return
        self.validateLabelList[validListIndex].update_text(self.validList[validListIndex])
        self.textInputList[validListIndex] = text
        try:
            self.buttonStack.remove_widget(self.addValidateButton)
        except:
            pass
        if self.validList[0]==self.validList[1]==True:
            self.addValidateButton = AddValidateButton(text = "Add Item to Firebase",size_hint = (1,.5),color=[0,0,0,1])
            self.addValidateButton.textInputList = self.textInputList
            self.buttonStack.add_widget(self.addValidateButton)
            
        
class BlankScreen(Screen):
    def __init__(self,**kwargs):
        super(BlankScreen,self).__init__(**kwargs)
        self.name = "blank"


########## Widgets ############################
class BuzzerButton(ButtonBehavior,Image):
    pressed = BooleanProperty(False)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
             self.pressed = not self.pressed
             if not connected():
                sm.transition.direction = 'left'
                sm.current = "connerror"
                return True
             for food in food_list:
                if food[2] == True:
                    food[2] == False
             update_firebase() 
             return True
        return super(BuzzerButton, self).on_touch_down(touch)
        

class AddButton(Button):
    pressed = False
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            return True
        return super(AddButton, self).on_touch_down(touch)
    def on_touch_up(self,touch):
        if self.pressed:
            self.pressed = False
            if self.collide_point(*touch.pos):
                sm.transition.direction = 'left'
                sm.current = "add"
            return True
        return super(AddButton, self).on_touch_up(touch)

class AddValidateButton(Button):
    
    pressed = False
    
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            return True
        return super(AddValidateButton, self).on_touch_down(touch)
    def on_touch_up(self,touch):
        if self.pressed:
            self.pressed = False
            if self.collide_point(*touch.pos):
                if not connected():
                    sm.transition.direction = 'down'
                    sm.current = "connerror"
                    return True
                food_list.append([self.textInputList[0],self.textInputList[1],None])
                update_firebase()
                sm.transition.direction = 'left'
                sm.remove_widget(sm.get_screen("food"))
                sm.add_widget(FoodScreen())
                sm.current = "food"
                sm.remove_widget(sm.get_screen("add"))
                sm.add_widget(AddScreen())
            return True
        return super(AddValidateButton, self).on_touch_up(touch)

class HomeButton(Button):
    pressed = False
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            return True
        return super(HomeButton, self).on_touch_down(touch)
    def on_touch_up(self,touch):
        if self.pressed:
            self.pressed = False
            if self.collide_point(*touch.pos):
                sm.transition.direction = 'right'
                sm.current = 'home'
            return True
        return super(HomeButton,self).on_touch_up(touch)
    
class FoodButton(Button):
    pressed = False
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            return True
        return super(FoodButton, self).on_touch_down(touch)
    def on_touch_up(self,touch):
        if self.pressed:
            self.pressed = False
            if self.collide_point(*touch.pos):
                sm.transition.direction = 'left'
                sm.current = 'food'
            return True
        return super(FoodButton,self).on_touch_up(touch)
class RefreshButton(ButtonBehavior, Image):
    pressed = False
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            return True
        return super(RefreshButton, self).on_touch_down(touch)
    def on_touch_up(self,touch):
        if self.pressed:
            self.pressed = False
            if self.collide_point(*touch.pos):
                sm.transition.direction = 'down'
                sm.current = "blank"
                sm.remove_widget(sm.get_screen("food"))
                sm.add_widget(FoodScreen())
                sm.transition.direction = 'up'
                sm.current = "food"
                
            return True
        return super(RefreshButton, self).on_touch_up(touch)

class ValidateLabel(Label):

    def update_text(self,valid):

        if valid:
            self.text = ""
        else:
            if self.id == "namelabel":
                self.text = "Alphanumeric"
            elif self.id == "expirylabel":
                self.text = "ddmmyy" 
            else:
                self.text == "Error in input"
                
class RemoveButton(Button):
    pressed = False
    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            return True
        return super(RemoveButton, self).on_touch_down(touch)
    def on_touch_up(self,touch):
        if self.pressed:
            self.pressed = False
            for item in food_list[:]: 
                if time_to_expiry(item[1]) == 'Expired':
                    food_list.remove(item)
                    update_firebase()
            sm.transition.direction = 'down'
            sm.current = "blank"
            sm.remove_widget(sm.get_screen("food"))
            sm.add_widget(FoodScreen())
            sm.transition.direction = 'up'
            sm.current = "food"
            return True
        return super(RemoveButton,self).on_touch_up(touch)

#Who is the master of button now?

################################# Classes #####################################



class FoodBeltApp(App):
    def build(self):
        global sm
        sm.add_widget(HomeScreen())
        sm.add_widget(FoodScreen())
        sm.add_widget(ConnErrorScreen())
        sm.add_widget(AddScreen())
        sm.add_widget(BlankScreen())
        self.root = sm 
        
        
        return self.root

if is_leap_year(now.year): dayMonthList[1]+=1
if __name__ == '__main__':
    FoodBeltApp().run()
    

    
    
    
    
    
    
    
    
