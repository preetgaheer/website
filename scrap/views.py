from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd 
import numpy as np

# Create your views here.

def driversetup():
    options = webdriver.ChromeOptions()
    # options.add_argument('--disable-browser-side-navigation')
    #run Selenium in headless mode
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    #overcome limited resource problems
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("lang=en")
    #open Browser in maximized mode
    options.add_argument("start-maximized")
    #disable infobars
    options.add_argument("disable-infobars")
    #disable extension
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    return driver

def slow_scrolling(speed, driver):
  try:
    print('start waiting')
    driver.implicitly_wait(10)
    print('script1')
    total_page_height = driver.execute_script("return document.body.scrollHeight") 
    print('script2')
    current_position = driver.execute_script('return window.scrollY + window.innerHeight')
    total_page = total_page_height/speed
    # while driver.execute_script("document.addEventListener('scroll', function(e) { let documentHeight = document.body.scrollHeight;let currentScroll = window.scrollY + window.innerHeight; let modifier = 200;  if(currentScroll + modifier > documentHeight) { return false} else { return true}});"):
    for i in range(1, speed+1):
        print("scrolling .." , i)
        driver.execute_script(f"window.scrollTo(0,{total_page*i});")
        sleep(1) 
        driver.execute_script(f"window.scrollTo(0,0);")
        print(total_page*i)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    print('loading page ......')
    elm = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.XPATH, f'//ul[@id="pm-grid"]//div[@class="pm-video-thumb ripple"]//a[@title][2]//img[contains(@src,"thumbs")]')))
    print(len(elm))
  except Exception as e:
    print(e)
  print('done scrolling')

def scrap(page_number, driver):
  print('getting')
  driver.get(f'https://indiangirlporn.net/newvideos.html?&page={page_number}')
  print('sleeping')
  sleep(3)
  driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
  speed = 40
  print('start slow srolling')
  slow_scrolling(speed, driver)
  video_links_tags = driver.find_elements(By.XPATH, f'//ul[@id="pm-grid"]//div[@class="pm-video-thumb ripple"]//a[@title][2]')
  img_tags = driver.find_elements(By.XPATH, f'//ul[@id="pm-grid"]//div[@class="pm-video-thumb ripple"]//a[@title][2]//img')
  title_tags = driver.find_elements(By.XPATH, f'//ul[@id="pm-grid"]//div[@class="caption"]//h3')
  title_list=[]
  thumbnail_list = []
  videos_link_list =[]
  for a_tag in video_links_tags:
    videos_link_list.append(a_tag.get_attribute('href'))
  for img_tag in img_tags:
    thumbnail_list.append(img_tag.get_attribute('src'))
  for h3_tag in title_tags:
    title_list.append(h3_tag.text)
  print(len(thumbnail_list), thumbnail_list)

  title_list = list(dict.fromkeys(title_list))
  thumbnail_list = list(dict.fromkeys(thumbnail_list))
  videos_link_list = list(dict.fromkeys(videos_link_list))

  offset_speed = 5
  while len(thumbnail_list)<len(videos_link_list):
    thumbnail_list = []
    print("while_loop")
    if speed<=0:
      break
    slow_scrolling(speed-offset_speed)
    img_tags = driver.find_elements(By.XPATH, f'//ul[@id="pm-grid"]//div[@class="pm-video-thumb ripple"]//a[@title][2]//img')
    for img_tag in img_tags:
      thumbnail_list.append(img_tag.get_attribute('src'))
  thumbnail_list = list(dict.fromkeys(thumbnail_list))
  videos_link_list = list(dict.fromkeys(videos_link_list))
  title_list = list(dict.fromkeys(title_list))
  print("end_scraping")
  return title_list , thumbnail_list , videos_link_list






def main(request):
  driver = driversetup()
  pages_to_scrape = 3
  thumbnail_list = []
  videos_link_list = []
  title_list = []
  for i in range(1,pages_to_scrape+1):
    print("page_to_scrape:" , i)
    titles, thumbs, videos = scrap(i, driver)
    title_list.append(titles)
    thumbnail_list.append(thumbs)
    videos_link_list.append(videos)
    print('next page')

  img_tags = driver.find_elements(By.XPATH, f'//ul[@class="pm-ul-browse-videos list-unstyled"]//div[@class="pm-video-thumb ripple"]//a[@title][2]//img')
  for img_tag in img_tags:
    thumbnail_list.add(img_tag.get_attribute('src'))
    # thumbnail_list_all.append(img_tag.get_attribute('src'))
  print(len(thumbnail_list))

  # data = zip(videos_links, thumbnail_list)
  # print(list(data))
  # videos_link_slice = list(videos_link_list)[:3]
  print(list(videos_link_list))
  actual_video_link = []



  for i in (0,3):
    for d in videos_link_list[i]:
        print('in loop')
        print('getting..')
        try:
          driver.get(d)
          driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
          print('start appending...')
          actual_video_link.append(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="embedded-video"]//iframe'))).get_attribute('src'))
          print('next loop')
        except Exception as e:
          print(e)
  print(actual_video_link)

  # thumbnail_list_slice =thumbnail_list[:3]
  # title_list_slice =title_list[:3]
  # final = zip(actual_video_link , title_list_slice, thumbnail_list_slice)
  final = zip(actual_video_link , title_list[0], thumbnail_list[0])
  print(len(actual_video_link))
  print(len(title_list))

  print(len(thumbnail_list))


  final_data_zip = list(final)

  df = pd.DataFrame(final_data_zip, columns = ['Video', 'Title', 'Thumbnail'])

  df.head()

  # saving the dataframe
  df.to_csv('sample11.csv')



  len(img_tags)


  return HttpResponse('ok')