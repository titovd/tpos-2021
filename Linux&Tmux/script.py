#!/usr/bin/env python3

import argparse
import libtmux
import logging
import os
import secrets
import socket

from tqdm.auto import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm


logging.basicConfig(level=logging.INFO)  # логгер для вывода информации 


def get_available_port():
    '''
    Функция для получения свободного порта для запуска ноутбука.
    '''

    with socket.socket() as s:
        s.bind(('',0))
        port = s.getsockname()[1]
        s.close()
        return port


def start(num_users, base_dir='./'):
    '''
    Запустить $num_users ноутбуков. У каждого рабочая директория виде $base_dir+$folder_num

    :param num_users: количество ноутбуков для запуска
    :param base_dir: домашняя директория для рабочих директорий
    '''

    tmux_server = libtmux.Server()
    current_session_name  = secrets.token_urlsafe()
    current_session = tmux_server.new_session(
        current_session_name
    )
    logging.info(f'Запущена сессия tmux, session_name: {current_session_name}')

    with logging_redirect_tqdm():
        for currrent_user_num in tqdm(range(1, num_users + 1)):
            user_folder_name = f'user-{currrent_user_num}'
            working_dir = os.path.join(base_dir, current_session_name, user_folder_name)
            os.makedirs(working_dir)
            logging.info(f'Создана рабочая директория для пользователя: {working_dir}')

            current_window = current_session.new_window(
                window_name=user_folder_name, start_directory=working_dir
            )
            logging.info(f'Создано новое окно tmux, window_name: {user_folder_name}')
            current_pane = current_window.attached_pane

            port = get_available_port()
            token = secrets.token_urlsafe()
            notebook_dir = os.path.join(os.getcwd(), working_dir)

            cmd = f'jupyter notebook --ip 0.0.0.0 --port {port} --no-browser --NotebookApp.token=\'{token}\' --NotebookApp.notebook_dir=\'{notebook_dir}\''
            current_pane.send_keys(cmd)
            logging.info(f'Запущен jupyter-notebook, port: {port} token: {token}')


def stop(session_name, num):
    '''
    Функция остановки окружения по его номеру.

    :param session_name: Названия tmux-сессии, в которой запущены окружения
    :param num: номер окружения, которое можно убить
    '''
    tmux_server = libtmux.Server()
    session = tmux_server.find_where(
       {"session_name" : session_name}
    )
    user_window = f'user-{num}'
    session.kill_window(user_window)
    logging.info(f'Окно window_name: {user_window} для tmux-сессии {session_name} остановлено')


def stop_all(session_name):
    '''
    Функция остановки всех окружений в tmux-сессии

    :param session_name: Названия tmux-сессии, в которой запущены окружения
    '''
    
    tmux_server = libtmux.Server()
    session = tmux_server.find_where(
        {"session_name" : session_name}
    )  
    session.kill_session()
    logging.info(f'Сессия tmux {session_name} остановлена')



def get_parser():
    '''
    Функция создания парсера для аргументов скрипта.
    '''

    parser = argparse.ArgumentParser(
        description='Запуск и работа с нескольими изолированными jupyter ноутбуками'
    )
    parser.add_argument(
        'cmd', type=str, choices=['start', 'stop', 'stop_all']
    )
    parser.add_argument(
        '-n', '--num_users', type=int, default=1, 
        help='Количество пользователей, для которых надо запустить изолированный jupyter-ноутбук'
    )
    parser.add_argument(
        '-d', '--base_dir', type=str, default='./',
        help='Корневая директория для создания изолированных директорий'
    )
    parser.add_argument(
        '-ns', '--num_to_stop', type=int,
        help='Номер окружения для остановки'
    )
    parser.add_argument(
        '-sn', '--session_name', type=str,
        help='Название tmux сессии для остановки'
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.cmd == 'start':
        start(args.num_users, args.base_dir)
    elif args.cmd == 'stop':
        stop(args.session_name, args.num_to_stop)
    elif args.cmd == 'stop_all':
        stop_all(args.session_name)

    
if __name__ == '__main__':
    main()
