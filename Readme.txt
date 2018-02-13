Ситема для прослушивания событий протокол VOEvent от GCN
https://gcn.gsfc.nasa.gov/voevent.html
https://gcn.gsfc.nasa.gov/tech_describe.html

Состав проекта: 

notice_filter.py - содержит основную функцию прослушивания сообщений и вызов их обработчиков
test_notice_filter.py - тестовый скрипт для функций из notice_filter.py
clock.py - функции для работы со временем разных КА
gbm_tte.py - функции для работы с TTE данными Fermi-GBM
get_fermi.py - функции для скачивания TTE данных Fermi-GBM
get_integral.py - функции для скачивания данных INTEGRAL-SPI-ACS
tle.py - функции для скачивания TLE 

/tmp содержит учебные примеры, использовавшиеся при написании кода

Обработчик сообщений GCN (notice_filter.py) запускается в screen.

screen -ls вывод доступных скринов 
screen -r [имя скрина] развернуть свернутый скрин, если их несколько нужно указать имя
Выход из screen
Есть 2 (два) способа выхода из экрана. 
Первый - "Ctrl-А" и "d", чтобы отключить его (процедура обратная screen -r). 
Второй - набираем команду exit внутри скрина. Также можно использовать "Ctrl-А" и "К" чтобы прибить скрин.

Ссылки по screen 
http://help.ubuntu.ru/wiki/screen
https://www.tecmint.com/screen-command-examples-to-manage-linux-terminals/
https://admins.su/kak-polzovatsya-utilitoj-screen-v-linux/