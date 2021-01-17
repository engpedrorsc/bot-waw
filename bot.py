'''Etapas
1 - Apresentação e identificação
2 - Carregar fontes de dados (telefones e mensagem)
3 - Login
4 - Envio das mensagens

'''


# from pathlib import Path
# from selenium.webdriver.support.ui import WebDriverWait
# from time import time
# from functions import *
# from datetime import datetime
# from urllib.request import urlopen
# from urllib.error import *

from functions import *
from selenium.webdriver.support.ui import WebDriverWait


def main():
    # Files list
    files = ['mensagem.txt',
             'telefones_bloqueados.txt',
             'telefones_para_envio.txt']
    campaign_folder_root = 'Campanhas'

    presentation('BEM-VINDO  AO  BOT  WAW !')

    files_ready = input(
        'Os arquivos com a mensagem e com os telefones podem ser carregados? (s/[n]): ')
    if files_ready != 's':
        print('Preencha os arquivos de mensagem e de telefones e inicie novamente.')
        input('Pressione ENTER para fechar.')
        exit()

    campaign_folder = open_campaign(files, campaign_folder_root)
    os.chdir(campaign_folder)

    # File load and creation
    message = read_input('mensagem.txt',
                         'Mensagem carregada com sucesso.',
                         'Mensagem vazia.')
    full_phone_list = list(dict.fromkeys(read_input('telefones_para_envio.txt',
                                                    'Lista de telefones carregada com sucesso.',
                                                    'Lista de telefones vazia.')))
    phone_black_list = list(dict.fromkeys(read_input('telefones_bloqueados.txt',
                                                     'Lista de telefones bloqueados carregada com sucesso.')))
    contacted_phones = list(dict.fromkeys(read_input('telefones_contactados.txt',
                                                     'Lista de telefones contactados carregada com sucesso.')))
    invalid_phones = list(dict.fromkeys(read_input('telefones_invalidos.txt',
                                                   'Lista de telefones inválidos carregada com sucesso.')))

    excluded_phones = phone_black_list + contacted_phones + invalid_phones
    if len(excluded_phones) > 0:
        phones_list = [
            phone_number for phone_number in full_phone_list if phone_number not in excluded_phones]
    else:
        phones_list = full_phone_list

    driver = open_browser('..' + os.sep + 'geckodriver.exe')
    wdw_short = WebDriverWait(
        driver, 15, poll_frequency=0.5, ignored_exceptions=None)  # Short wait.
    wdw_long = WebDriverWait(
        driver, 30, poll_frequency=0.5, ignored_exceptions=None)  # Long wait.
    max_pace = 90  # Maximum sent messages per hour

    login(driver, 'http://web.whatsapp.com', wdw_short)
    # Counts current delivered messages in the current campaign.
    current_sent_counter = 0
    start_time = time()  # Set start running time to calculate the pace.

    for phone in phones_list:
        print(f'Enviando mensagem para {phone}.')
        url = f'https://web.whatsapp.com/send?phone={phone}&source=&data=#.'
        try:
            send_message(start_time, driver, url, message,
                         current_sent_counter, max_pace, wdw_short, wdw_long)
        except InvalidUrl:
            print('URL inválida.')
            write_file('telefones_invalidos.txt', phone)
            continue
        else:
            write_file(contacted_phones, phone)
            current_sent_counter += 1
            global_sent_counter = len(contacted_phones)
            if global_sent_counter == 1:
                print(f'{global_sent_counter} mensagem enviada nesta campanha.')
            else:
                print(f'{global_sent_counter} mensagens enviadas nesta campanha.')

    show_statistics()

    # log_sent_file = f'{campaign}_sent.txt'
    # log_invalid_file = f'{campaign}_invalid.txt'

    # phones = read_input(input_folder, 'Telefones.txt', 'Lista telefônica carregada.', 'Lista de telefones vazia.') # Phones list.
    # black_list = read_input(input_folder, 'bloqueados.txt', 'Lista telefônica carregada.') # Blacklisted phones
    # message = read_input(input_folder, 'Mensagem.txt', 'Mensagem carregada.', 'Mensagem vazia.') # Message to be sent.
    # sent_log = read_input(log_folder, log_sent_file,'Telefones já contactados carregados.')
    # invalid_log = read_input(log_folder, log_invalid_file, 'Telefones inválidos carregados.')

    # sent_log_counter = len(sent_log) # Counts previous delivered messages in the current campaign.
    # remaining_phones = difference(phones, black_list, sent_log, invalid_log, 'Telefones da campanha identificados.', 'Sem novos telefones para esta campanha.')


    # driver = open_browser('geckodriver.exe')
    # wdw_short = WebDriverWait(driver, 15, poll_frequency=0.5, ignored_exceptions=None) # Short wait.
    # wdw_long = WebDriverWait(driver, 30, poll_frequency=0.5, ignored_exceptions=None) # Long wait.
    # max_pace = 90 # Maximum sent messages per hour
    # login(driver, 'http://web.whatsapp.com', wdw_short)
    # sent_counter = 0 # Counts current delivered messages in the current campaign.
    # start_time = time() # Set start running time to calculate the pace.
    # for phone in remaining_phones:
    #     print(f'Enviando mensagem para {phone}')
    #     url = f'https://web.whatsapp.com/send?phone={phone}&source=&data=#.'
    #     try:
    #         send_message(start_time, driver, url, message, sent_counter, max_pace, wdw_short, wdw_long)
    #     except InvalidUrl:
    #         write_log(log_folder, log_invalid_file, phone)
    #         continue
    #     except WebDriverException:
    #         raise WebDriverException('Computador desconectado. Verifique a conexão do computador. (main loop)')
    #         input()
    #     else:
    #         write_log(log_folder, log_sent_file, phone)
    #         sent_counter += 1
    #         global_sent_counter = sent_counter + sent_log_counter
    #         if global_sent_counter == 1:
    #             print(f'{global_sent_counter} mensagem enviada nesta campanha.')
    #         else:
    #             print(f'{global_sent_counter} mensagens enviadas nesta campanha.')
    # show_statistics() # To be written
    # return
if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     expiration_date = '2020-09-30'
#     expiration_msg = 'Verifique a sua conexão à internet.\nSe estiver OK, contacte o desenvolvedor.'
#     close_msg = 'Pressione ENTER e feche o navegador para encerrar.'
#     try:
#         date_str = urlopen('https://just-the-time.appspot.com/').read().strip().decode('utf-8')
#         date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
#         if date <= datetime.strptime(expiration_date, '%Y-%m-%d'):
#             main()
#         else:
#             print('\n'+expiration_msg)
#             raise Exception(expiration_msg)
#     except URLError or HTTPError or ContentTooShortError:
#         print('\n'+expiration_msg)
#         input('\n'+close_msg)
#     except WebDriverException:
#         print('Ocorreu algum erro com o navegador ou com a conexão do computador.')
#         input('\n'+close_msg)
