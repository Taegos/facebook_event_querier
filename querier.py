import time
import random
import getpass
import smtplib
import sys
import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver

def setup_selenium():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="chromedriver.exe")
    return driver

def fb_login(driver, email, password):
    driver.get("https://www.facebook.com/")
    driver.find_element_by_xpath("""//*[@id="email"]""").send_keys(email)
    driver.find_element_by_xpath("""//*[@id="pass"]""").send_keys(password)
    time.sleep(random.uniform(3, 4))
    driver.find_element_by_xpath("""//*[@id="loginbutton"]""").find_elements_by_xpath(".//*")[0].click()
    time.sleep(random.uniform(1.5, 2.5))

def notify_keyword_match(email_addr, email_password, keyword, post, event_id):
    msg = MIMEMultipart()
    msg['Subject'] = "A KEYWORD MATCH WAS FOUND IN THE EVENT!"
    body = \
    "Keyword '{}' was found in the latest post '{}' of the event.\n\n" \
    "Go to the event feed by using the link below:\n\n" \
    "https://www.facebook.com/events/{}/?active_tab=discussion" \
    .format(keyword, post, event_id)

    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_addr, email_password)
    text = msg.as_string()
    server.sendmail(email_addr, email_addr, text)
    server.quit()
    
def query_event_loop(driver, event_id, keywords, email_address, email_password):
    driver.get("https://www.facebook.com/events/" + event_id + "/?active_tab=discussion")
    latest_match = None
    while (True):
        first = driver.find_element_by_xpath("""//*[@id="event_mall_""" + event_id + """"]/div[1]""") \
        .find_elements_by_xpath(".//*")[2] \
        .find_elements_by_xpath(".//*")[0] \
        .find_elements_by_xpath(".//*")[2] \
        .find_elements_by_xpath(".//*")[0].text
        post = first.split('\n')[2]
        for keyword in keywords:
            if keyword.lower() in post.lower() and post != latest_match:
                latest_match = post
                notify_keyword_match(email_address, email_password, keyword, post, event_id)
        time.sleep(random.uniform(1.5, 2.5))
        driver.refresh()

def main(fb_email, fb_password, event_id, keywords, email_address, email_password):
    driver = setup_selenium()
    fb_login(driver, fb_email, fb_password)
    query_event_loop(driver, event_id, keywords, email_address, email_password)
    
if __name__ == '__main__':
    args = {}
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as handle:
            args = json.loads(handle.read())
    else: 
        args["fb_email"] = input("facebook email: ")
        args["fb_password"] = getpass.getpass("facebook password: ")
        args["event_id"] = input("event id: ")
        print("Now enter the list of keywords (continue by typing 'c' and hitting enter):")        
        keywords = []
        keyword = input()
        keywords.append(keyword)
        while (keyword != "c"):
            keyword = input()
            keywords.append(keyword)
        args["keywords"] = keywords
        args["email_address"] = input("email address (gmail): ")
        args["email_password"] =  getpass.getpass("email password: ")
    main(**args)