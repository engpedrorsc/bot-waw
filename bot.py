#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium.webdriver.support.ui import WebDriverWait
from time import time
from auxiliaries.functions import *


def main():
    driver = open_browser('./drivers/geckodriver.exe')
    wdwA = WebDriverWait(driver, 15, poll_frequency=0.5, ignored_exceptions=None) # Short wait.
    wdwB = WebDriverWait(driver, 30, poll_frequency=0.5, ignored_exceptions=None) # Long wait.
    phones = read_input('./inputs/00Telefones.txt', 'Lista telefônica carregada.') # Phones list.
    message = read_input('./inputs/10Mensagem.txt', 'Mensagem carregada.') # Message to be sent.
    max_pace = 90 # Maximum sent messages per hour

    login(driver, 'http://web.whatsapp.com', wdwA)
    sent_counter = 0 # Counts delivered messages. Always starts at zero.
    start_time = time() # Set start running time to calculate the pace.
    for phone in phones:
        print(f'Enviando mensagem para {phone}')
        url = f'https://web.whatsapp.com/send?phone={phone}&source=&data=#.'
        try:
            sent_counter = send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB)
        except InvalidUrl:
            continue
    show_statistics() # To be written
    return


if __name__ == "__main__":
    main()
