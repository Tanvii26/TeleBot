import telebot
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import types
import re
from datetime import datetime
from bob_telegram_tools.bot import TelegramBot
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials,db,firestore
from firebase import firebase

firebase = firebase.FirebaseApplication('https://castor-order-booking-bot-default-rtdb.firebaseio.com/', None) 
cred = credentials.Certificate("castornow.json")
firebase_admin.initialize_app(cred,name='app')
DEFAULT_APP = firebase_admin.initialize_app(cred, {
  'databaseURL': "https://castor-order-booking-bot-default-rtdb.firebaseio.com"
})
firestore_client = firestore.client()
ref_menu = db.reference("/Menu")
ref_combo = db.reference("/Combo")
ref_order = db.reference("/Order")
ref_bill=db.reference("/Bill")
API_TOKEN = "<KEY>"

bot = telebot.TeleBot(API_TOKEN)

def reply(message):
    global msg
    query = message.text.lower()
    replies1 = {
        "hi": "Hello",
        "how are you?": "I'm fine thank you.",
        "how are you": "I'm fine thank you",
        "what's your name?": "My name is Food Jinni.",
        "whats your name": "My name is Food Jinni.",
        "what's your name?": "My name is Food Jinni.",
        "bye": "See you!"
    }
    replies2 = [
        "whats the menu",
        "Whats all you have in menu",
        "Please display menu"
    ]
    flag=0
    for key, value in replies1.items():
        if flag==0 and query in key :
            flag=1
            msg=bot.send_message(message.chat.id,value)
            break
    for key in replies2:
        if flag==0 and query in key :
            flag=1
            ans='''Here's the menu\n'''
            cafe_menu=ref_menu.get()
            markup=types.ReplyKeyboardMarkup(row_width=1)
            itembtn1 = types.KeyboardButton('Place Order')
            markup.add(itembtn1)
            for key in cafe_menu:
                menu_key=cafe_menu[key]
                ans+=menu_key['Name']+'\n'
            msg=bot.send_message(message.chat.id,ans,reply_markup=markup)
            bot.register_next_step_handler(msg,place_order)
            break
    if flag==0:
        msg=bot.send_message(message.chat.id,"Sorry! I didn't get you")



def enter_size(message):
    size_val=message.text
    id=message.chat.id
    price=0
    menu_tab=ref_menu.get()
    for key in menu_tab:
        menu_item=menu_tab[key]
        if(menu_item['Name']==order_val):
            m=menu_item['Size-price']
            for a in m:
                if a==size_val:
                    price=m[a]
                    break
    added={"Date":today_date,"Order-id":length+1,"Phone-no":value,"Order-value":order_val,"Size":size_val,"Chat_id":id,"Status":"no","Price":price}
    ref_order.push(added)
    markup=types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/Add_Order')
    itembtn2 = types.KeyboardButton('/Bill')
    markup.add(itembtn1, itembtn2)
    msg=bot.send_message(message.chat.id,"Your order is placed ",reply_markup=markup)
@bot.message_handler(commands=["Add_Order"])
    
def place_order(message):
    global today_date
    today_date=str(datetime.now())
    global ms
    order_tab=ref_order.get()
    for key in order_tab:
        ms=key
    global length
    length=order_tab[ms]['Order-id']
    msg=bot.send_message(message.chat.id,"What's your mobile number ")
    bot.register_next_step_handler(msg,take_mobile)
    
def take_mobile(message):
    global value
    value=message.text
    markup=types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Aloo tikki Burger')
    itembtn2 = types.KeyboardButton('Fries')
    itembtn3 = types.KeyboardButton('Cold Drink')
    itembtn4 = types.KeyboardButton('Cold Coffee')
    itembtn5 = types.KeyboardButton('Sandwich')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    msg=bot.send_message(message.chat.id,"Enter your order ",reply_markup=markup)

    bot.register_next_step_handler(msg,take_order)

 

def take_order(message):
    global order_val
    order_val=message.text
    markup=types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('S')
    itembtn2 = types.KeyboardButton('M')
    itembtn3 = types.KeyboardButton('L')
    markup.add(itembtn1, itembtn2, itembtn3)
    msg=bot.send_message(message.chat.id,"Enter the size ",reply_markup=markup)
    bot.register_next_step_handler(msg,enter_size)

@bot.message_handler(commands=["Bill"])
def bill(message):
    bill_tab=ref_bill.get()
    order_tab=ref_order.get()
    val=message.chat.id
    arr=''
    amount=0
    for key in order_tab:
        o_t=order_tab[key]
        if(o_t["Chat_id"]==val and o_t["Status"]=="no"):
            amount+=o_t['Price']
            arr+=str(o_t["Order-id"])+','
            firebase.put('/Order/'+key,'Status',"yes")

    added={"Order-id":arr,"Price":amount}
    ref_bill.push(added)
    msg=bot.send_message(message.chat.id,"Your total bill is "+ str(amount)+'\nThank You!!')


@bot.message_handler(func=reply)
def display(message):
  pass
bot.enable_save_next_step_handlers(delay=2)
bot.polling()
