from time import sleep, time
from math import ceil
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import presence_of_element_located, presence_of_all_elements_located

'''Custom exceptions'''


class InvalidUrl(Exception):
    pass


'''Login functions'''


def open_browser(path):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en')
    try:
        return webdriver.Firefox(executable_path=path, firefox_profile=profile)
    except:
        print('Erro ao abrir o navegador.')


def open_page(driver, url, wdw):
    try:
        driver.get(url)
        wdw.until(presence_of_element_located((By.XPATH, '//*[@aria-label = "Scan me!"]')))
        print('Escaneie o código QR para iniciar o WhatsApp Web.')
    except TimeoutException:
        try:
            driver.refresh()
        except WebDriverException:
            print('Erro de conexão do computador. (open_page1)')
    except:
        print('Erro de conexão do computador. (open_page2)')
    else:
        print('URL carregada com sucesso.')



def check_login(driver, wdw):
    try:
        wdw.until(presence_of_element_located((By.XPATH, '//span[@data-testid = "laptop"]')))
    except TimeoutException:
        try:
            driver.refresh()
            check_login(driver, wdw)
        except:
            print('Erro de conexão do computador. (check_login1)')
    except:
        print('Erro de conexão do computador. (check_login2)')
    else:
        print('Login realizado com sucesso.')


def login(driver, url, wdw):
    open_page(driver, url, wdw) # Opens page
    check_login(driver, wdw) # Checks if login was successful
    return


'''Chat functions'''


def read_input(file_path, msg):
    f = open(file_path, 'rb')
    text = f.read().decode('UTF-8').splitlines()
    f.close()
    print(msg)
    return text


def check_pace(max_pace, start_time, sent_counter):
    try:
        current_time = time()
        pace = ceil(sent_counter/(current_time - start_time)*3600)
        if pace < max_pace:
            print(f'Passo: {pace} -> Passo OK.')
            return
        else:
            print(f'Passo: {pace} -> Mantendo o passo.')
            sleep(5)
            return check_pace(max_pace, start_time, sent_counter)
    except ZeroDivisionError:
        sleep(1)
        return check_pace(max_pace, start_time, sent_counter)


def send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB):
    try:
        driver.get(url)
        locator = (By.XPATH, '//div[@data-tab = "1"]')
        wdwB.until(presence_of_element_located(locator))
        text_box = driver.find_element(locator[0], locator[1])
        
        for line in message:
            text_box.send_keys(line)
            ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        
        check_pace(max_pace, start_time, sent_counter)
        input('Pressione ENTER para enviar a mensagem.')
        text_box.send_keys(Keys.ENTER)
        wdwB.until_not(presence_of_all_elements_located((By.XPATH, '//span[@data-testid = "msg-time"]')))
    
    except TimeoutException:
        if bool(driver.find_elements(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid.") or\
                                                    contains(text(), "O número de telefone compartilhado através de url é inválido.")]')):
            print('URL inválida.')
            raise InvalidUrl
       
        elif bool(driver.find_elements(By.XPATH, '//*[contains(text(), "Trying to reach phone") or\
                                                      contains(text(), "Tentando conectar ao celular")]')) or\
             bool(driver.find_elements(By.XPATH, '//span[@data-testid = "alert-phone"]')):
            
            print('Telefone desconectado. Verifique a conexão do telefone. (send_message)')
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB)
        
        elif bool(driver.find_elements(By.XPATH, '//*[@aria-label = "Scan me!"]')):
            print('Refaça o login. (send_message)')
            check_login(driver, wdwA)
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB)
        
        elif bool(driver.find_elements(By.XPATH, '//span[@data-testid = "alert-computer"]')):
            print('Computador desconectado. Verifique a conexão do computador. (send_message)')
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB)
        
        else:
            driver.refresh()
            sleep(5)
            return send_message(start_time, driver, url, message, sent_counter, max_pace, wdwA, wdwB)
   
    except:
        print('O computador pode estar desconectado. (send_message)')
        raise
    
    else:
        sent_counter += 1
        if sent_counter == 1:
            print(f'{sent_counter} mensagem enviada.')
        else:
            print(f'{sent_counter} mensagens enviadas.')
        return sent_counter


'''Results functions'''


def show_statistics():
    # To be written
    pass
    return
