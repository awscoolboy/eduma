from selenium import webdriver as webdriver
from time import sleep
from pyyoutube import Api
from embeddify import Embedder
import isodate
from pyvirtualdisplay import Display 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from database import Course, Lesson
import hashlib
import pickle
import telebot
import os.path
import time
from telebot import types


username = 'eduma'
password = 'strong123#123$'
url = "http://yenecademy.com/wp-admin/"
bot_token = '1140618034:AAH-LQfj5XZ1SA7p0F9oKPrg7oKZmpllsZs'
youtube_api_key = 'AIzaSyCH0rkqRliwjuSCVLm22ziYWh3VhIEZjko'

bot = telebot.TeleBot(bot_token)

# display = Display(visible=0, size=(800, 600)) 
# display.start() 

def getYoutubeEmbedCode(videoId):
    embedder = Embedder()
    code = embedder("https://www.youtube.com/watch?v=" + str(videoId), width="853", height="480")
    return code

def formatLessonName(count):
    countStr = ""
    if count <= 9:
        countStr = "00" + str(count)
    elif count <= 99 and count >= 10:
         countStr = "0" + str(count)
    else:
        countStr = str(count)
    return countStr

def login():
    opt = webdriver.ChromeOptions()
    opt.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=opt)

    driver.get(url)
    time.sleep(2)
    login_btn = driver.find_element_by_xpath('//*[@id="wp-submit"]')
    email_field = driver.find_element_by_xpath('//*[@id="user_login"]')
    pass_field = driver.find_element_by_xpath('//*[@id="user_pass"]') 
    email_field.send_keys(username)
    time.sleep(2)
    pass_field.send_keys(password)
    login_btn.click()
    driver.find_element_by_xpath('//*[@id="toplevel_page_learn_press"]').click()
    driver.find_element_by_xpath('//*[@id="toplevel_page_learn_press"]/ul/li[3]/a').click()
    driver.find_element_by_xpath('//*[@id="wpbody-content"]/div[3]/a').click()
    return driver
    
    

def loginAndUpdate(lessons,message,plid):
    bot.send_message(message.chat.id,'Login to eduma to insert data')
    driver = login()
    temp_counter = 1

    title_field = driver.find_element_by_xpath('//*[@id="title"]')
    media_field = driver.find_element_by_xpath('//*[@id="_lp_lesson_video_intro"]')
    date_field = driver.find_element_by_xpath('//*[@id="_lp_duration"]')
    publish_button = driver.find_element_by_xpath('//*[@id="publish"]')
    time_selector_path =  driver.find_element_by_xpath('//*[@id="_lp_duration_select"]')
    select = Select(driver.find_element_by_id('_lp_duration_select'))

    for lesson in lessons:
        driver.implicitly_wait(10)
 
        time_array  = str(lesson.duration).split(":") 

        final_time = 1
        if time_array[0] != "0" and time_array[0] != "00":
             select.select_by_value('hour')
             final_time = time_array[0]
        elif time_array[1] != "0" and time_array[1] != "00":
             select.select_by_value('minute')   
             final_time = time_array[1]
        else:
            select.select_by_value('minute') 

        if lesson is None or lesson.title == None or lesson.code is None or len(lesson.title) <= 0 or lesson.code is None or len(lesson.code) <= 0:
            bot.send_message(message.chat.id,"lesson failed: for playlist id = " +  str(plid) + "  = index of "  + temp_counter)
            continue

         
        title_field.clear()
        title_field.send_keys(lesson.title)
        time.sleep(1)
        media_field.clear()
        media_field.send_keys(lesson.code)
        time.sleep(1)
        date_field.clear()
        date_field.send_keys(final_time)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", publish_button)
        driver.implicitly_wait(10)
        driver.find_element_by_xpath('//*[@id="wpbody-content"]/div[3]/a').click()
        driver.implicitly_wait(10)
        time.sleep(2)
        temp_counter =  temp_counter + 1
    bot.send_message(message.chat.id,"Finsiehd adding coruse playlistid = {} , count = {}".format(plid,temp_counter))



#save the data later to get it
    

import json
def process_play_list_step(message):
    try:
        chat_id = message.chat.id
        text = message.text
        if ":" not in text:
           bot.reply_to(message,'Wrong message format')
           return

        data = str(text).split(':')
        plaid = data[0]
        title = data[1]    

        if len(plaid) <= 5 or len(title) <=5:
            bot.reply_to(message,'Wrong message format')
            return 
            
            
        api = Api(api_key=youtube_api_key)
        playlist_item_by_playlist = api.get_playlist_items(playlist_id=plaid, count=1000)
        videos = playlist_item_by_playlist.items
        if len(videos) <= 0:
           bot.send_message(message.chat.id,"No Vidoes found for playlist = " +str(title)) 
           return

        bot.send_message(message.chat.id,"Found " +str(len(videos)) + " videos from youtube") 
        real_video_count = len(videos)
        count = 0
        lessons = []
        for video in videos:
            video_by_id = api.get_video_by_id(video_id=video.snippet.resourceId.videoId,parts=('snippet', 'contentDetails', 'statistics'))
            if len(video_by_id.items) <= 0:
               real_video_count = real_video_count - 1
               continue
            count = count + 1
            item = video_by_id.items[0]
            title = title + " " + formatLessonName(count) + " " + item.snippet.title
            time_val = isodate.parse_duration(item.contentDetails.duration)
            code =  getYoutubeEmbedCode(video.snippet.resourceId.videoId)
            lesson = Lesson(title, code, time_val)
            lessons.append(lesson)
        
        bot.send_message(message.chat.id,"Total avalibale vidoe count = " +str(real_video_count)) 
        if len(lessons) <= 0:
           bot.send_message(message.chat.id,"No lesson found!")  
        loginAndUpdate(lessons,message,plaid)

    except Exception as e:
        bot.reply_to(message,str(e))


def yotubeApiKeyHandler(message):
    new_key = message.text
    connfig_file = open('config.json','r+')
    jsong_data = json.load(connfig_file)   
    connfig_file.truncate(0) 
    jsong_data['youtube_api_key'] = new_key
    r = json.dumps(jsong_data)
    loaded_r = json.loads(r)
    connfig_file.write(str(loaded_r))  
    connfig_file.close()  
    bot.send_message(message.chat.id,"Api updated Successfully!")
def emepeyHanlder():
    pass    

@bot.message_handler()
def handle_start_help(message):
    text = ''
    print(message.text)
    if message.text == '/start':
       text="Hello! Welcome to  " + str(bot.get_me().first_name)
       bot.send_message(message.chat.id,text)  
    elif message.text == '/addcoruse':
        current_course = None
        text = 'Send Playlistid of the coruse as playlistid:couse titile'
        bot.send_message(message.chat.id,text)  
        bot.register_next_step_handler(message, process_play_list_step)
    elif message.text == '/setapikey': 
        return bot.register_next_step_handler(message,"Not finished yet")
        with open('config.json', 'r+') as f:
             print("f=" + str(f)) 
             
             
            #  if len(f.read())  <= 0:
            #      bot.send_message(message.chat.id,'No api key found!')
            #      f.write('{"type": "service_account"}')
            #      f.close()
            #      return
             json_data = json.load(f)    
             print(json_data)    
             api = json_data['youtube_api_key']

             bot.send_message(message.chat.id,"Send yotube api key!" + '\n' + "current api key = " + str(api))
             bot.register_next_step_handler(message,yotubeApiKeyHandler)
    elif message.text == '/cancle':
        text = "Current Sessions cancled"  
        bot.send_message(message.chat.id,text)  
        bot.clear_reply_handlers(message)
    else:
        text = "Hi"  
        bot.send_message(message.chat.id,text)  


   
bot.polling()