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
from kivy.uix.behaviors import ButtonBehavior
from firebase import firebase
import datetime

now = datetime.datetime.now()
url = "https://internetofthings-f6256.firebaseio.com/" # URL to Firebase database
token = "CRCZ9IiX8uZCHPuD0dOYJ1XO2rSKjYzEAeUqrRPt" # unique token used for authentication
firebase = firebase.FirebaseApplication(url, token)
highTemp = 320
food_dic = {}
dayMonthList = [31,28,31,30,31,30,31,31,30,31,30,31]
high_temp_img,refresh_img,alarm_on_img,alarm_off_img,background_img = "high_temp.png","refresh.png","alarm_on.png","alarm_off.png","background.jpg"

#Testing data
food_dic_test= {"001":["Celery","050317",False,[1]],"002":["Milk","100317",False,[300,327,330]],
                "003":["Carrot","011218",False,[300,302]]}
############### debug
#firebase.put("/","food",food_dic_test)  
try:
    food_dic = firebase.get('/food')
    day,month,year = str(now.day),str(now.month),str(now.year - 2000)
    while len(day) < 2:
        day = "0" + day
    while len(month) < 2:
        month = "0" + month
    food_dic["005"][1] = day+month+year
    firebase.put('/','food',food_dic)
except:
    pass
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
def update_food_dic(keyID,itemIndex,newItem):
    for key,item in zip(food_dic.keys(),food_dic.values()):
        if keyID == key:
            item[itemIndex] = newItem
def update_firebase():
    firebase.put('/','food',food_dic)
def connected():
    try:
        food_dic = firebase.get('/food')
        
        print "connected"
        return True
    except:
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
    if yearNow < yearExp or monthNow < monthExp:
        numOfDays,monthNow = dayMonthList[monthNow-1] - dayNow, monthNow + 1
    else:
        numOfDays= 0
    
    
    while yearNow < yearExp:
        if is_leap_year(yearNow):
            dayMonthList[1] = 29
        else:
            dayMonthList[1] = 28
        numOfDays += sum(dayMonthList[monthNow-1:])
        monthNow = 1
        yearNow+=1
    if is_leap_year(yearNow):
        dayMonthList[1] = 29
    else:
        dayMonthList[1] = 28
    if monthNow < monthExp:
        numOfDays += sum(dayMonthList[monthNow - 1:monthExp-1])
        numOfDays += dayExp
    elif monthNow == monthExp:
        numOfDays += dayExp - dayNow
    dayNow,monthNow,yearNow = now.day, now.month,now.year
        
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
    
    
############################# Main Functions ##################################
################################ Callbacks ####################################

################################ Callbacks ####################################
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
            
        self.scrollView = ScrollView(
                            do_scroll_x = False,
                            do_scroll_y = True,
                            size_hint = (1,.8),
                            id = "food_scroll")
        self.headers = GridLayout(cols = 4, size_hint=(1,.1))
        self.headers.add_widget(Label(text="Name",size_hint=(.2,1),color=[0,0,0,1]))
        self.headers.add_widget(Label(text="Time until Expiry",size_hint=(.3,1),color=[0,0,0,1]))
        self.headers.add_widget(RefreshButton(source = refresh_img,size_hint=(.2,1)))
        self.headers.add_widget(Button(text="Remove",size_hint=(.3,1),color=[0,0,0,1]))
        self.mainGrid = GridLayout(rows = 3)
        self.mainGrid.add_widget(self.headers)
        self.mainGrid.add_widget(self.scrollView)
        self.mainGrid.add_widget(AddButton(text = "Add new entry",size_hint=(1,.1),color=[0,0,0,1]))
        self.add_widget(Image(source = background_img,size_hint=(1,1),keep_ratio = False,allow_stretch=True))
        self.add_widget(self.mainGrid)
        self.foodGrid = GridLayout(cols=4,row_force_default=True, row_default_height=40)
        for key,item in zip(food_dic.keys(),food_dic.values()):
            self.foodGrid.add_widget(Label(text = item[0],size_hint=(.2,.1),color=[0,0,0,1]))
            self.foodGrid.add_widget(Label(text = time_to_expiry(item[1]),size_hint=(.3,.1),color=[0,0,0,1]))
            if is_high_temp(item[3]):
                self.foodGrid.add_widget(Image(source = high_temp_img,size_hint=(.2,.1)))
            else:
                self.foodGrid.add_widget(Label(text = "",size_hint=(.2,.1),color=[0,0,0,1]))
            buzzerButton = BuzzerButton(size_hint=(.3,.1), id=key)
            buzzerButton.pressed = item[2]
            buzzerButton.change_image()
            self.foodGrid.add_widget(buzzerButton)
        # Make sure the height is such that there is something to scroll.
        self.foodGrid.bind(minimum_height = self.foodGrid.setter('height'))
        self.scrollView.add_widget(self.foodGrid)

class AddScreen(Screen):
    validList = [False] * 3
    validateLabelList = []
    textInputList = [0,0,0]
    def __init__(self,**kwargs):
        super(AddScreen,self).__init__(**kwargs)
        self.name = "add"
        self.root = GridLayout(rows = 2)
        self.inputStack = StackLayout(orientation='lr-tb', size_hint=(1,.8))
        self.inputStack.add_widget(Label(text="Tag ID",size_hint=(.3,.1),color=[0,0,0,1]))
        self.inputStack.add_widget(Label(text="Name",size_hint=(.3,.1),color=[0,0,0,1]))
        self.inputStack.add_widget(Label(text="Expiry Date",size_hint=(.4,.1),color=[0,0,0,1]))
        for key,x_pos in zip(["tagid","name","expiry"],[.3,.3,.4]):
            textInput = TextInput(id = key + "input",
                          multiline = False,
                          size_hint=(x_pos,.1))
            textInput.bind(text=self.check_input)
            self.inputStack.add_widget(textInput)
        for key,x_pos in zip(["tagid","name","expiry"],[.3,.3,.4]):
            validateLabel = ValidateLabel(id = key + "label",
                                  size_hint = (x_pos,.1),
                                  shorten = True,
                                  color = [0,0,0,1])
            self.validateLabelList.append(validateLabel)
            self.inputStack.add_widget(validateLabel)
        self.buttonStack = StackLayout(orientation='bt-lr', size_hint=(1,.2))
        self.root.add_widget(self.inputStack)
        self.buttonStack.add_widget(HomeButton(text="Back",size_hint=(1,.5),color=[0,0,0,1]))
        self.root.add_widget(self.buttonStack)
        self.add_widget(Image(source = background_img,size_hint=(1,1),keep_ratio = False,allow_stretch=True))
        self.add_widget(self.root)
            
    def check_input(self,instance,text):
        if instance.id == "tagidinput":
            validListIndex = 0
            if 0 < len(text) <= 3:
                for char in text:
                    if char not in '0123456789':
                        self.validList[0] = False
                        break
                else:
                    if int(text) in [int(key) for key in food_dic.keys()]:
                        self.validList[0] = None
                    elif int(text) != 0:
                        self.validList[0] = True
                    else:
                        self.validList[0] = False
                
            else: self.validList[0] = False

        elif instance.id == "nameinput":
            validListIndex = 1
            for char in text:
                if char not in '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM ':
                    self.validList[1] = False
                    break
            else:
                if text != '':
                    self.validList[1] = True
                else:
                    self.validList[1] = False
        elif instance.id == "expiryinput":
            validListIndex = 2
            if len(text) == 6:
                for char in text:
                    if char not in '0123456789':
                        self.validList[2] = False
                        break
                else:
                    day,month,year = int(text[:2]),int(text[2:4]),int(text[4:6])+2000
                    
                    if month>12 or month <= 0 or day > dayMonthList[month-1]: 
                        self.validList[2] = False
                    else:
                        #Check if input date is in the past or today
                        if (year < now.year) or (year == now.year and (month < now.month or month == now.month and day <= now.day)):
                            self.validList[2] = False
                        else:
                            self.validList[2] = True
            else:
                self.validList[2] = False
                    
        else:
            return
        self.validateLabelList[validListIndex].update_text(self.validList[validListIndex])
        self.textInputList[validListIndex] = text
        if self.validList[0] and validListIndex == 0:
            while len(self.textInputList[0]) < 3:
                self.textInputList[0] = '0' + self.textInputList[0]
        try:
            self.buttonStack.remove_widget(self.addValidateButton)
        except:
            pass
        if self.validList[0]==self.validList[1]==self.validList[2]==True:
            self.addValidateButton = AddValidateButton(text = "Add Item to Firebase",size_hint = (1,.5),color=[0,0,0,1])
            self.addValidateButton.textInputList = self.textInputList
            self.buttonStack.add_widget(self.addValidateButton)
            
        
class BlankScreen(Screen):
    def __init__(self,**kwargs):
        super(BlankScreen,self).__init__(**kwargs)
        self.name = "blank"


########## Widgets ############################
class BuzzerButton(ButtonBehavior,Image):
    pressed = None
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
             self.pressed = not self.pressed
             if not connected():
                sm.transition.direction = 'left'
                sm.current = "connerror"
                return True
             self.change_image()
             update_food_dic(self.id,2,self.pressed)
             print food_dic
             update_firebase()
             return True
        return super(BuzzerButton, self).on_touch_down(touch)
        
    def change_image(self):
        print self.pressed
        if self.pressed:
            self.color = [1,0,0,1]
            self.source = alarm_on_img
        else:
            self.color = [0,1,0,1]
            self.source = alarm_off_img
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
                food_dic[self.textInputList[0]] = [self.textInputList[1],self.textInputList[2],False,[1]]
                update_firebase()
                sm.transition.direction = 'left'
                sm.remove_widget(sm.get_screen("home"))
                sm.add_widget(HomeScreen())
                sm.current = "home"
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
                sm.remove_widget(sm.get_screen("home"))
                sm.add_widget(HomeScreen())
                sm.transition.direction = 'up'
                sm.current = "home"
                
            return True
        return super(RefreshButton, self).on_touch_up(touch)

class ValidateLabel(Label):

    def update_text(self,valid):

        if valid:
            self.text = ""
        else:
            if self.id == "tagidlabel":
                if valid != None:
                    self.text = "00X or 0XX or XXX"
                else:
                    self.text = "ID in use"
            elif self.id == "namelabel":
                self.text = "Alphanumeric"
            elif self.id == "expirylabel":
                self.text = "ddmmyy" 
            else:
                self.text == "Error in input"
            
        
################################# Classes #####################################



class FoodBeltApp(App):
    def build(self):
        global sm
        sm.add_widget(HomeScreen())
        sm.add_widget(ConnErrorScreen())
        sm.add_widget(AddScreen())
        sm.add_widget(BlankScreen())
        self.root = sm 
        
        
        return self.root

if is_leap_year(now.year): dayMonthList[1]+=1
if __name__ == '__main__':
    FoodBeltApp().run()
    

    
    
    
    
    
    
    
    