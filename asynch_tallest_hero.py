import os
import pprint
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

START_ID = 1
MAX_ID = 731
hero_cache = {}


async def get_hero_info(session, character_id: int) -> dict:
    """Получение информации о герое по его ID.
    
    Параметры:
        session: объект сессии для выполнения HTTP-запросов.
        character_id (int): ID героя, информацию о котором необходимо получить.

    Возвращает:
        dict: информация о герое в виде словаря.
    
    Исключения:
        RuntimeError: если возникает ошибка при получении информации о герое.
    """

    if character_id in hero_cache:
        return hero_cache[character_id]

    async with session.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id}") as response:
        if response.status == 200:
            current_hero_info = await response.json()
            hero_cache[character_id] = current_hero_info
            return current_hero_info
        else:
            raise RuntimeError(
                f"Ошибка при получении информации о герое с ID {character_id}: {response.status}"
            )
        

def convert_height_to_cm(height: str) -> int:
    """Преобразование роста из метров или сантиметров в сантиметры.

    Если рост указан в других единицах, будет вызвано исключение ValueError.

    Параметры:
        height (str): рост, указанный в формате "X cm" или "Y meters".

    Возвращает:
        int: рост в сантиметрах.

    Исключения:
        ValueError: если формат роста не распознан.
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

async def tallest_hero(gender: str, has_job: bool) -> dict:
    """Поиск самого высокого супергероя по заданным критериям.

    Если герой не имеет места работы (base) или оно указано как '-',
    то такой герой считается безработным.
    
    Параметры:
        gender (str): пол супергероя.
        has_job (bool): наличие работы у супергероя.

    Возвращает:
        dict: Словарь с информацией о самом высоком супергерое,
        соответствующем заданным критериям.
    """

    tallest_hero_id = None
    max_height = 0

    async with aiohttp.ClientSession() as session:
        tasks = [get_hero_info(session, current_id) for current_id in range(START_ID, MAX_ID + 1)]
        heroes = await asyncio.gather(*tasks)

        for current_hero in heroes:
            if current_hero is None:
                continue
            base = current_hero.get("work", {}).get("base", "")
            is_base_valid = (has_job and base not in ["-", ""]) or (not has_job and base in ["", "-"])

            if current_hero["appearance"]["gender"] == gender and is_base_valid:
                try:
                    current_height = convert_height_to_cm(current_hero["appearance"]["height"][1])
                    if current_height > max_height:
                        max_height = current_height
                        tallest_hero_id = current_hero
                except ValueError:
                    continue

    if tallest_hero_id is not None:
        return tallest_hero_id
    return {}

def main():
    result = asyncio.run(tallest_hero("Male", True))
    pprint.pprint(result)

if __name__ == "__main__":
    main()
    hero_cache.clear()