import pprint
import requests

START_ID = 1
MAX_ID = 731

def convert_height_to_cm(height: str) -> int:
    """Преобразование роста из метров или сантиметров в сантиметры.

    Параметры:
        height (str): рост, указанный в формате "X cm",
        "Y meters" или другом.

    Возвращает:
        int: рост в сантиметрах.

    Исключения:
        ValueError: если рост отрицательный или если
        формат роста отличается от "X cm", "Y meters".
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
    
    Герои с некорректным ростом игнорируются.
    
    Параметры:
        gender (str): пол супергероя ("Male" или "Female").
        has_job (bool): наличие работы у супергероя (True) или нет (False).

    Возвращает:
        dict: Словарь с информацией о самом высоком супергерое или
        пустой словарь, если героев не найдено.
    """

    response = requests.get("https://akabab.github.io/superhero-api/api/all.json")
    all_heroes = response.json()

    filtered_heroes = [
        hero for hero in all_heroes
        if hero["appearance"]["gender"] == gender and
        (
            (has_job and hero.get("work", {}).get("base", "") not in ["-", ""]) or
            (not has_job and hero.get("work", {}).get("base", "") in ["", "-"])
        )
    ]

    tallest_hero = None
    for hero in filtered_heroes:
        try:
            height_in_cm = convert_height_to_cm(hero["appearance"]["height"][1])
            if tallest_hero is None or height_in_cm > convert_height_to_cm(tallest_hero["appearance"]["height"][1]):
                tallest_hero = hero
        except ValueError:
            continue

    return tallest_hero if tallest_hero else {}

def main():
    result = get_tallest_hero("Male", True)
    pprint.pprint(result)

if __name__ == "__main__":
    main()