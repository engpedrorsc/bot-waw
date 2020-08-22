#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from time import time
from functions import *


def main():
    seller = 'Pedro'
    campaign = 'Teste_2020-08-20'

    input_folder = Path(f'./inputs')
    log_folder = Path(f'./logs')
    log_sent_file = f'{campaign}_sent.txt'
    log_invalid_file = f'{campaign}_invalid.txt'
    
    phones = read_input(input_folder, '00Telefones.txt', 'Lista telefônica carregada.') # Phones list.
    check_input(phones, 'Lista de telefones vazia.')    
    message = read_input(input_folder, '10Mensagem.txt', 'Mensagem carregada.') # Message to be sent.
    check_input(message, 'Mensagem vazia.')
    sent_log = read_input(log_folder, log_sent_file,'Telefones já contactados carregados.')
    sent_log_counter = len(sent_log) # Counts previous delivered messages in the current campaign.
    invalid_log = read_input(log_folder, log_invalid_file, 'Telefones inválidos carregados.')

    remaining_phones = difference(phones, sent_log, invalid_log)
    check_input(remaining_phones, 'Sem novos telefones para esta campanha.')

    driver = open_browser('geckodriver.exe')
    wdwA = WebDriverWait(driver, 15, poll_frequency=0.5, ignored_exceptions=None) # Short wait.
    wdwB = WebDriverWait(driver, 30, poll_frequency=0.5, ignored_exceptions=None) # Long wait.
    max_pace = 90 # Maximum sent messages per hour

    login(driver, 'http://web.whatsapp.com', wdwA)
    sent_counter = 0 # Counts current delivered messages in the current campaign.
    start_time = time() # Set start running time to calculate the pace.
    for phone in remaining_phones:
        print(f'Enviando mensagem para {phone}')
        url = f'https://web.whatsapp.com/send?phone={phone}&source=&data=#.'
        try:
            send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB)
        
        except InvalidUrl:
            write_log(log_folder, log_invalid_file, phone)
            continue

        except WebDriverException:
            raise WebDriverException('Computador desconectado. Verifique a conexão do computador. (main loop)')
        
        else:
            write_log(log_folder, log_sent_file, phone)
            sent_counter += 1
            sent_total = sent_counter + sent_log_counter
            if sent_total == 1:
                print(f'{sent_total} mensagem enviada.')
            else:
                print(f'{sent_total} mensagens enviadas.')
    
    show_statistics() # To be written
    return


if __name__ == "__main__":
    main()
