import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from pathlib import Path
from time import sleep, time
from math import ceil
import csv
import io
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import presence_of_element_located, presence_of_all_elements_located

'''Custom exceptions'''


class InvalidUrl(Exception):
    pass

class EmptyInputFile(Exception):
    pass


'''Start and login functions'''


def ask_campaign_name():
    name = input('\n>>>Identifique a campanha<<<\nSugestão: Nome-Data (Ex: Semanal-2020.12.31)\nNome da campanha: ')
    forbidden = ['<','>',':','"','/','\\','|','?','*']
    if len(name) == 0:
        print('\nO nome da campanha é obrigatório.')
        return ask_campaign_name()
    for c in name:
        if c in forbidden:
            print(f'\nErro: O caractere "{c}" é inválido. Digite um nome com caracteres válidos.')
            return ask_campaign_name()
    return name


def open_browser(driver):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en')
    return webdriver.Firefox(executable_path=driver, firefox_profile=profile)


def open_page(driver, url, wdw):
    try:
        driver.get(url)
        wdw.until(presence_of_element_located((By.XPATH, '//*[@aria-label = "Scan me!"]')))
        print('Escaneie o código QR para iniciar o WhatsApp Web.')
    except TimeoutException:
        driver.refresh()
        return open_page(driver, url, wdw)
    else:
        print('URL carregada com sucesso.')


def check_login(driver, wdw):
    try:
        wdw.until(presence_of_element_located((By.XPATH, '//span[@data-testid = "laptop"]')))
    except TimeoutException:
        driver.refresh()
        return check_login(driver, wdw)
    else:
        print('Login realizado com sucesso.')


def login(driver, url, wdw):
    open_page(driver, url, wdw) # Opens page
    check_login(driver, wdw) # Checks if login was successful


'''Chat functions'''


def read_input(path, file, msg):
    path.mkdir(parents = True, exist_ok = True)
    try:
        f = open(path/file, 'rb')
    except FileNotFoundError:
        f = open(path/file, 'w')
        f.close()
        return read_input(path, file, msg)
    text = f.read().decode('UTF-8').splitlines()
    f.close()
    print(msg)
    return text


def check_input(input, msg):
    if len(input) == 0:
        print(msg)
        exit()


def write_log(path, file, text):
    f = open(path/file, 'a')
    f.write(f'{text}\n')
    f.close()


def difference(full_list, list1, list2, list3, msg): # To be improved
    filtered = set(full_list) - set(list1) - set(list2) - set(list3)
    print(msg)
    return list(filtered)


def check_pace(max_pace, start_time, counter):
    try:
        current_time = time()
        pace = ceil(counter/(current_time - start_time)*3600)
        if pace < max_pace:
            print(f'Passo: {pace} -> Passo OK.')
            return
        else:
            msg = f'Passo: {pace} -> Mantendo o passo.'
            print(msg, end='\r')
            sleep(1)
            print(' ' * len(msg), end='\r')
            return check_pace(max_pace, start_time, counter)
    except ZeroDivisionError:
        sleep(1)
        return check_pace(max_pace, start_time, counter)


def send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2):
    try:
        driver.get(url)
        locator = (By.XPATH, '//div[@data-tab = "1"]')
        wdw2.until(presence_of_element_located(locator))
        text_box = driver.find_element(locator[0], locator[1])
        
        for line in message:
            text_box.send_keys(line)
            ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        
        check_pace(max_pace, start_time, sent_counter)
        # input('Pressione ENTER para enviar a mensagem.')
        text_box.send_keys(Keys.ENTER)
        wdw2.until_not(presence_of_all_elements_located((By.XPATH, '//span[@data-testid = "msg-time"]')))
    
    except TimeoutException:
        if bool(driver.find_elements(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid.") or\
                                                    contains(text(), "O número de telefone compartilhado através de url é inválido.")]')):
            print('URL inválida.')
            raise InvalidUrl
       
        elif bool(driver.find_elements(By.XPATH, '//*[contains(text(), "Trying to reach phone") or\
                                                      contains(text(), "Tentando conectar ao celular")]')) or\
             bool(driver.find_elements(By.XPATH, '//span[@data-testid = "alert-phone"]')):
            
            print('Telefone desconectado. Verifique a conexão do telefone. (send_message)')
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2)
        
        elif bool(driver.find_elements(By.XPATH, '//*[@aria-label = "Scan me!"]')):
            print('Refaça o login. (send_message)')
            check_login(driver, wdw1)
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2)
        
        elif bool(driver.find_elements(By.XPATH, '//span[@data-testid = "alert-computer"]')):
            print('Computador desconectado. Verifique a conexão do computador. (send_message)')
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2)

        else:
            driver.refresh()
            sleep(5)
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2)

    return


'''Results functions'''


def show_statistics():
    # To be written
    pass
    return
