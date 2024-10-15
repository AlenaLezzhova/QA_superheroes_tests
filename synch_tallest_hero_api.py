import os
import pprint
import requests
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

START_ID = 1
MAX_ID = 731
hero_cache = {}

def get_hero_info(character_id: int) -> dict:
    """Получение информации о герое по его ID.
    
    Параметры:
        character_id (int): ID героя, информацию о котором необходимо получить.

    Возвращает:
        dict: информация о герое в виде словаря.
    
    Исключения:
        RuntimeError: если возникает ошибка при получении информации о герое.
    """
        
    if character_id in hero_cache:
        return hero_cache[character_id]
    else:
        response = requests.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id}")
        if response.status_code == 200:
            hero_info = response.json()
            hero_cache[character_id] = hero_info
            return hero_info
        else:
            raise RuntimeError(f"Ошибка при получении информации о герое с ID {character_id}: {response.status_code}")

def convert_height_to_cm(height: str) -> int:
    """Преобразование роста из метров или сантиметров в сантиметры.

    Параметры:
        height (str): рост, указанный в формате "X cm", "Y meters" или другом.

    Возвращает:
        int: рост в сантиметрах.

    Исключения:
        ValueError: если рост отрицательный или формат роста не распознан.
    """
    
    if height.startswith("-"):
        raise ValueError("Отрицательный рост")
    else:
        if height.endswith(" cm"):
            return int(height[:-3])
        elif height.endswith(" meters"):
            return int(float(height[:-7].strip()) * 100)
        else:
            raise ValueError("Неизвестный формат роста")

def get_tallest_hero(gender: str, has_job: bool) -> dict:
    """Поиск самого высокого супергероя по полу и наличию работы.

    Если герой не имеет места работы (base) или оно указано как '-',
    то такой герой считается безработным. 
    
    Герои с некоккектным ростом игнорируются.
    
    Параметры:
        gender (str): пол супергероя ("Male" или "Female").
        has_job (bool): наличие работы у супергероя (True) или нет (False).

    Возвращает:
        dict: Словарь с информацией о самом высоком супергерое или
        пустой словарь, если героев не найдено.
    """
    
    tallest_hero_id = None
    max_height = 0

    for current_id in range(START_ID, MAX_ID+1):
        current_hero = get_hero_info(current_id)
        base = current_hero.get("work", {}).get("base", "")
        if has_job:
            is_base_valid = base not in ["-", ""]
        else:
            is_base_valid = base in ["", "-"]
        if current_hero["appearance"]["gender"] == gender and is_base_valid:
            try:
                current_height = convert_height_to_cm(current_hero["appearance"]["height"][1])
                if current_height > max_height:
                    max_height = current_height
                    tallest_hero_id = current_id
            except ValueError:
                continue

    if tallest_hero_id is not None:
        return get_hero_info(tallest_hero_id)
    return {}

def main():
    result = get_tallest_hero("Male", True)
    print('итог')
    pprint.pprint(result)

if __name__ == "__main__":
    main()
