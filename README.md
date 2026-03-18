Установка
```bash
curl -sSL https://raw.githubusercontent.com/prelubodey/buhgalter_kds/main/setup.sh | bash
```

Перейдите в папку: 
```bash
cd /root/projects/buhgalter_kds
```
Остановить бота:
```bash
docker compose stop
```
(Контейнер сохранится, но перестанет работать).

Запустить остановленного бота:
```bash
docker compose start
```
Полностью удалить контейнер и остановить его:
```bash
docker compose down
```
Запустить с нуля (со сборкой):
```bash
docker compose up -d --build
```
Посмотреть, кто запущен	
```bash
docker ps
```
Посмотреть все контейнеры (даже выключенные)	
```bash
docker ps -a
```
Посмотреть логи в реальном времени	
```bash
docker logs -f accountant-ai-monitor
```
