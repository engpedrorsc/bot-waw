from selenium import webdriver
import os

print(os.getcwd())

driver = webdriver.Firefox('./auxiliaries/geckodriver.exe')