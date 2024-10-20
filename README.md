# Функция для поиска супергероя по заданным значениям и тестирование при помощи фреймворма pytest

 Данная функция принимает на вход пол и наличие работы (булевое значение) и возврящает по этим критериям всю информацию о самом высоком герое.

 При анализе исходного кода проекта было замечено:
 
1. В информации о каждом герое присутствует два поля, отвечающих за работу:
 'base' (место работы) и 'occupation' (род деятальности).
 Так как критерий "наличие работы (булевое значение)" не является однозначным, то в реализованных мной функциях используется следующая логика проверки наличия или отсутствия работы: если герой не имеет места работы (base) или оно указано как '-', то такой герой считается безработным.

2. В поле 'height' для героев предусмотрено указание высоты в двух единицах измерения: неметрическая (дюймы) и метрическая. Во всех реализациях функции поиска самого высокого героя сравнивает героев в метрической системе. Для этого была написана функция для перевода см и м в см.
ыЕсли у героя указано некорректное значение метрики роста (не 'cm' или 'meters') - такой герой игнорируется.

## Описание реализаций
### tallest_hero_all.py
 Данная реализация построена на обращении к файлу all.json, расположенного в исходном коде проекта по адресу: "https://akabab.github.io/superhero-api/api/all.json".
 
 Плюсы:
 - поиск производится по уже собранному перечню всех супергероев со всеи информацией о них.
 - быстрое время работы.
 
 Минусы:
 - нельзя использовать функцию без доступа к репозиторию проекта
 - стоит постоянно следить за актуальностью файла all.json


### synch_tallest_hero_api.py
 Синхронная реализация, обращение происходит методом GET к эндпоинту https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id} для каждого героя.
 
 #### Установка и запуск
 1. Установить виртуальное окружение: python3 -m venv myenv
 2. Активировать виртуальное окружение: source myenv/bin/activate
 3. Установить зависимости: pip install -r requirements.txt
 4. В корне проекта создать файл .env
 5. Получить токен для работы с API на сайте: https://superheroapi.com/
 6. Сохранить полученный токен в файле .env в переменную ACCESS_TOKEN = 'токен доступа'

 #### Плюсы и минусы
 
 Плюсы:
 - простой алгоритм
 - всегда используется актуальная версия списка героев, взятая из API
 - не нужен доступ к исходному коду проекта
 
 Минус:
 - долгое время работы: для прохода по каждому json для всех героев (731) время работы около 12 минут


### asynch_tallest_hero.py
Асинхронная реализация, обращение происходит методом GET к эндпоинту https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id} для каждого героя, аналогичсно способу synch_tallest_hero_api.py, но добавлено кэширование и применены асинхронные функции для обращения к API, что позволило существенно сократить время работы.

 #### Установка и запуск
 1. Установить виртуальное окружение: python3 -m venv myenv
 2. Активировать виртуальное окружение: source myenv/bin/activate
 3. Установить зависимости: pip install -r requirements.txt
 4. В корне проекта создать файл .env
 5. Получить токен для работы с API на сайте: https://superheroapi.com/
 6. Сохранить полученный токен в файле .env в переменную ACCESS_TOKEN = 'токен доступа'


## Список тестовых файлов 
1. Все тесты лежат внутри каталога tests
2. test_tallest_hero_all.py - содержит тесты для test_tallest_hero_all.py
3. test_synch_tallest_hero_api.py - содержит тесты для synch_tallest_hero_api.py
4. test_asynch_tallest_hero.py - содержит тесты для asynch_tallest_hero.py

 ## Запуск тестов
 Для запуска необходимо вызвать команду **pytest** из корневого каталога проекта
 - всегда используется актуальная версия списка героев, взятая из API
 - не нужен доступ к исходному коду проекта
 - быстрое время работы
