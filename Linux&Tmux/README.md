## Скрипт для запуска в tmux N jupyter-ноутбуков в изолированных директориях.

* Для запуска N jupyter-ноутбуков в изолированных директориях в корневой директории DIR:
```bash
./script.py start --num_users <N> --base_dir <DIR>
```

* Для того, чтобы остановить окружение NUM по номеру в сессии SESSION_NAME:
```bash
./script.py stop --num_to_stop <NUM> --session_name <SESSION_NAME>
```

* Для того, что бы остановить сессию SESSION_NAME полностью:
```bash
./script.py stop_all --session_name <SESSION_NAME>
```
