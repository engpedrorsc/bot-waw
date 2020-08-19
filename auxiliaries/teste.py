import os
os.chdir(os.getcwd() + '/bot-waw/core')
print(os.getcwd())

from selenium import webdriver
from selenium.webdriver.common.by import By

print(os.getcwd())

profile = webdriver.FirefoxProfile()
profile.set_preference('intl.accept_languages', 'en')

driver = webdriver.Firefox(executable_path='../drivers/geckodriver.exe', firefox_profile=profile)