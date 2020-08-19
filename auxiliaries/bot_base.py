# -*- coding: utf-8 -*-
"""
Created on Thur Jul 23, 2020

@author: pedro
"""

import os

print(os.getcwd())

import math
from datetime import date
from datetime import datetime
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import socket
from sys import exit


# Classes

class Inputs:
    def __init__(self, file_name):
        self.file_name = file_name

    def read(self):
        f = open(self.file_name, "rb")
        phone = f.read().decode("UTF-8").splitlines()
        f.close()
        return phone


class Logs:
    def __init__(self, file_name):
        self.file_name = file_name

    def reset(self):
        f = open(self.file_name, "w+")
        f.close()

    def write(self, text):
        f = open(self.file_name, "a")
        f.write(text)
        f.close()


# Functions
def countdown(n, text_plural, text_singular):
    while n > 0:
        count_plural = text_plural.format(n)
        count_singular = text_singular.format(n)

        if n > 1:
            print(count_plural, end="\r")
        elif n == 1:
            print(count_singular, end="\r")
        else:
            print("Número de mensagens por hora inválido.")
            exit()

        n -= 1
        sleep(1)
        print(" " * max(len(count_plural), len(count_singular)), end="\r")


def element_presence(by, xpath, time, driver):
    element_present = EC.presence_of_element_located((by, xpath))
    WebDriverWait(driver, time).until(element_present)


def is_connected(log, attempts, max_attempts, attempts_interval):
    if attempts > max_attempts:
        print("Número máximo de tentativas excedido. Verifique a conexão com a internet.")
        exit()

    try:
        socket.create_connection(("www.google.com", 80))
        # print("Conexão OK.")

    except:
        log.write("Erro de conexão;" + str(datetime.now()) + "\n")
        print("Tentativa de conexão {}.".format(attempts))
        countdown(attempts_interval, "Erro de conexão. Nova tentativa em {} segundos.",
                  "Erro de conexão. Nova tentativa em {} segundo.")
        attempts += 1
        sleep(attempts_interval)
        is_connected(log, attempts, max_attempts, attempts_interval)


def login_whatsapp(log, max_attempts, attempts_interval):
    attempts = 1
    is_connected(log, attempts, max_attempts, attempts_interval)
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    driver.get("http://web.whatsapp.com")
    sleep(1)
    input("Pressione ENTER após escanear o código QR.")
    return driver


def send_whatsapp_msg(driver, phone_no, message, no_of_message, log_phone, log_connection, log_sent, max_attempts,
                      attempts_interval, messages_per_hour, in_between_sleep):
    sending_text = "Enviando mensagem para {}"
    print(sending_text.format(phone_no))
    attempts = 1
    is_connected(log_connection, attempts, max_attempts, attempts_interval)
    driver.get("https://web.whatsapp.com/send?phone={}&source=&data=#".format(phone_no))

    try:
        element_presence(By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]', 30, driver)
        txt_box = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')

        for x in range(no_of_message):

            for line in message:
                txt_box.send_keys(line)
                ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
            
            #print(" " * len(sending_text + phone_no), end="\r")
            countdown(math.floor(3600 / messages_per_hour)-in_between_sleep, "Envio em {} segundos.", "Envio em {} segundo.")
            txt_box.send_keys(Keys.ENTER)
            log_sent.write(str(phone_no) + ";" + str(datetime.now()) + "\n")

        print(" " * len(sending_text + phone_no), end="\r")
        print("Mensagem enviada para {}".format(phone_no))
        sleep(1)

    except Exception:
        log_phone.write(str(phone_no) + ";" + str(datetime.now()) + "\n")
        print("Telefone " + str(phone_no) + " inválido.")
        sleep(1)


def main():
    # Parameters
    messages_per_hour = 90  # Number of messages sent per hour
    no_of_message = 1  # Send the same message n times for the same number
    max_attempts = 20  # Max connection attempts
    attempts_interval = 30  # Time between attempts in seconds
    in_between_sleep = 1 # Time between message sent and next call
    print("Parâmetros inicializados.")

    # Input files
    mobile_no_list = Inputs("./inputs/00Telefones.txt").read()
    print("Lista de telefones carregada.")
    message_text = Inputs("./inputs/10Mensagem.txt").read()
    print("Mensagem carregada.")

    # Initialize stuff
    phones_error_log = Logs("./logs/30Erros de telefone " + str(date.today()) + ".txt")
    connection_error_log = Logs("./logs/40Erros de conexão " + str(date.today()) + ".txt")
    contacted_phones = Logs("./logs/20Telefones contactados " + str(date.today()) + ".txt")
    phones_error_log.reset()
    connection_error_log.reset()
    print("Logs inicializados.")

    target = login_whatsapp(connection_error_log, max_attempts, attempts_interval)

    for phone_no in mobile_no_list:
        send_whatsapp_msg(target, phone_no, message_text, no_of_message, phones_error_log, connection_error_log,
                        contacted_phones, max_attempts, attempts_interval, messages_per_hour, in_between_sleep)
        
        sleep(in_between_sleep)

    input("Envios finalizados. Verifique os logs para saber o resultado.\nPressione enter para fechar.")
    target.quit()


if __name__ == "__main__":
    main()


'''
ANOTAÇÕES

Caixa de texto:
>>> element = driver.find_element(By.XPATH, '//div[@data-tab = "1"]')
>>> write message

QR core:
>>> element = driver.find_element(By.XPATH, '//*[@aria-label = "Scan me!"]')

Verificação de mensagens enviadas:
>>> element = driver.find_elements(By.XPATH, '//span[@data-testid = "msg-time"]')
>>> len(element) > 0: throw DeliveryException

Telefone desconectado fora do chat:
>>> elements = driver.find_elements(By.XPATH, '//*[contains(text(), "Trying to reach phone")]')
>>> if len(element) > 0: throw PhoneOutChatException

Telefone desconectado dentro do chat:
>>> elements = driver.find_elements(By.XPATH, '//span[@data-testid = "alert-phone"]')
>>> len(elements) > 0: throw PhoneInChatException

Número inválido: 
>>> elements = driver.find_elements(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid.")]')
>>> if len(elements) > 0: throw UrlException 

'''