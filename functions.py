'''NOTAS:
1 - Transformar a chamada dos arquivos em objetos
'''


import os
from datetime import datetime as dt
import shutil
from pyfiglet import Figlet
from time import sleep, time
from math import ceil
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import presence_of_element_located, presence_of_all_elements_located

'''Custom exceptions'''


class InvalidUrl(Exception):
    pass


class EmptyInputFile(Exception):
    pass


'''Functions'''


def presentation(text: str, style='doom'):
    redered_text = Figlet(font=style)
    print('\n' + redered_text.renderText(text))


def invalid_char_check(text: str, forbidden_chars: list = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']):
    forbidden_chars_found = []
    for char in text:
        if char in forbidden_chars:
            forbidden_chars_found.append(char)
    return set(forbidden_chars_found)


def backup_campaign(campaign_folder, backup_folder, files):
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    for file in files:
        date_time = str(dt.now()).replace(':', '.')
        shutil.move(src=campaign_folder + os.sep + f'{file}',
                    dst=backup_folder + os.sep + f'{date_time}_{file}')


def copy_campaign_new_files(campaign_folder, files):
    for file in files:
        shutil.copy(src=f'{file}', dst=campaign_folder)


def open_mode():
    print('\nJá existe uma campanha com este nome.')
    print('Escolha uma das opções abaixo:')
    print('1 - Criar nova campanha com novo nome.')
    print('2 - Continuar a campanha já existente com os arquivos originais.')
    print('3 - Continuar a campanha já existente com os novos arquivos.')
    choice = int(input('Digite a opção escolhida e pressione ENTER: '))
    if choice not in [1, 2, 3]:
        print('\n---> Opção inválida.')
        return open_mode()
    return choice


def open_campaign(files, campaign_folder_root):
    print('\n>>> Identifique a campanha <<<')
    print('Sugestão: Nome-Data (Ex: Semanal-2020.12.31)')
    name = input('Nome da campanha: ')

    if len(name) == 0:
        print('\nO nome da campanha é obrigatório.')
        return open_campaign(files, campaign_folder_root)

    forbidden_chars_found = invalid_char_check(name)
    if len(forbidden_chars_found) > 0:
        found = ' '.join(forbidden_chars_found)
        print(
            f'\nErro: O nome escolhido possui os seguintes caracteres inválidos: {found}')
        return open_campaign(files, campaign_folder_root)

    campaign_folder = campaign_folder_root + os.sep + name
    if not os.path.exists(campaign_folder):
        os.makedirs(campaign_folder)
        copy_campaign_new_files(campaign_folder, files)
    else:
        choice = open_mode()
        if choice == 1:
            print('Insira um nome de campanha que ainda não exista.')
            open_campaign(files, campaign_folder_root)
        elif choice == 2:
            pass
        elif choice == 3:
            backup_folder = campaign_folder + os.sep + 'Backup'
            backup_campaign(campaign_folder, backup_folder, files)
            copy_campaign_new_files(campaign_folder, files)

    return campaign_folder


def read_input(file, msg_success, msg_error=''):
    try:
        f = open(file, 'rb')
    except FileNotFoundError:
        f = open(file, 'w')
        f.close()
        return read_input(file, msg_success, msg_error)
    text = f.read().decode('UTF-8').splitlines()
    f.close()
    if len(text) <= 0 and msg_error != '':
        print(msg_error)
        print('Verifique os arquivos e tente novamente.')
        input('Pressiona ENTER para fechar.')
        exit()
    else:
        print(msg_success)
    return text


def write_file(file, text):
    f = open(file, 'a')
    f.write(f'{text}\n')
    f.close()


def open_browser(driver):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en')
    return webdriver.Firefox(executable_path=driver, firefox_profile=profile)


def login(driver, url, wdw):
    try:
        driver.get(url)
        wdw.until(presence_of_element_located(
            (By.XPATH, '//*[@aria-label = "Scan me!"]')))
        print('Escaneie o código QR para iniciar o WhatsApp Web.')
    except TimeoutException:
        # driver.refresh()
        return login(driver, url, wdw)

    try:
        wdw.until(presence_of_element_located(
            (By.XPATH, '//span[@data-testid = "laptop"]')))
    except TimeoutException:
        # driver.refresh()
        return login(driver, url, wdw)
    else:
        print('Login realizado com sucesso.')


def write_message(message, text_box, driver):
    for line in message:
        text_box.send_keys(line)
        ActionChains(driver).key_down(Keys.SHIFT).key_down(
            Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()


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
        write_message(message, text_box, driver)
        check_pace(max_pace, start_time, sent_counter)
        # input('Pressione ENTER para enviar a mensagem.')
        text_box.send_keys(Keys.ENTER)  # Sends written message
        wdw2.until_not(presence_of_all_elements_located(
            (By.XPATH, '//span[@data-testid = "msg-time"]')))

    except TimeoutException:
        if bool(driver.find_elements(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid.") or\
                                                    contains(text(), "O número de telefone compartilhado através de url é inválido.")]')):
            raise InvalidUrl
        elif bool(driver.find_elements(By.XPATH, '//*[contains(text(), "Trying to reach phone") or\
                                                          contains(text(), "Tentando conectar ao celular")]')) or\
                bool(driver.find_elements(By.XPATH, '//span[@data-testid = "alert-phone"]')):
            print(
                '\n---> Telefone desconectado. Verifique a conexão do telefone. (send_message)')
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2)
        elif bool(driver.find_elements(By.XPATH, '//*[@aria-label = "Scan me!"]')):
            print('\n---> Refaça o login.')
            login(driver, wdw1)
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdw1, wdw2)
        elif bool(driver.find_elements(By.XPATH, '//span[@data-testid = "alert-computer"]')):
            print(
                '\n---> Computador desconectado. Verifique a conexão do computador. (send_message)')
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
