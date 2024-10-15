import os

import pytest
import aiohttp
from aioresponses import aioresponses
from dotenv import load_dotenv
from unittest.mock import patch

from asynch_tallest_hero import get_hero_info, convert_height_to_cm, tallest_hero, hero_cache

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

@pytest.mark.parametrize("input_height, expected_output", [
    ("179 cm", 179),
    ("0 cm", 0),
    ("2.5 meters", 250)
])
def test_convert_height_to_cm_valid(input_height, expected_output):
    """
    Тестирование функции convert_height_to_cm
    на работу с валидными значениями.
    """
    assert convert_height_to_cm(input_height) == expected_output

@pytest.mark.parametrize("invalid_input", [
    "invalid height",
    "5 feet",
    "555"
])
def test_convert_height_to_cm_invalid(invalid_input):
    """
    Тестирование функции convert_height_to_cm
    на работу с невалидными значениями.
    """
    with pytest.raises(ValueError, match="Неизвестный формат роста"):
        convert_height_to_cm(invalid_input)

@pytest.mark.parametrize("invalid_input", [
    "-10 cm",
    "-2 meters"
])
def test_convert_height_to_cm_negative(invalid_input):
    """
    Тестирование функции convert_height_to_cm
    на работу с отрицательными значениями.
    """
    with pytest.raises(ValueError, match="Отрицательный рост"):
        convert_height_to_cm(invalid_input)

mock_hero_response = [
    {
        "id": 1,
        "name": "Batman",
        "appearance": {
            "gender": "Male",
            "height": ["6'2", "188 cm"]
        },
        "work": {
            "occupation": "CEO of Wayne Enterprises",
            "base": "Gotham City"
        }
    },
    {
        "id": 2,
        "name": "Robin",
        "appearance": {
            "gender": "Male",
            "height": ["-", "185 cm"]
        },
        "work": {
            "occupation": "Secretary of Wayne Enterprises",
            "base": "Gotham City"
        }
    }
]

@pytest.mark.asyncio
async def test_get_hero_info_cache():
    """Тестирование кэширования информации о герое."""
    character_id = 1
    expected_response = {
        "id": character_id,
        "name": "Batman",
        "appearance": {
            "gender": "Male",
            "height": ["6'2", "188 cm"]
        },
        "work": {
            "occupation": "CEO of Wayne Enterprises",
            "base": "Gotham City"
        }
    }
    hero_cache.clear()
    with aioresponses() as m:
        m.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id}", payload=expected_response)
        async with aiohttp.ClientSession() as session:
            result = await get_hero_info(session, character_id)
    assert result == expected_response
    assert hero_cache[character_id] == expected_response

    async with aiohttp.ClientSession() as session:
        cached_result = await get_hero_info(session, character_id)
    assert cached_result == expected_response
    assert hero_cache[character_id] == expected_response


@pytest.mark.asyncio
async def test_get_hero_info_success():
    """Тестирование успешного получения информации о герое."""
    character_id = 1
    expected_response = {
        "id": character_id,
        "name": "Batman",
        "appearance": {
            "gender": "Male",
            "height": ["6'2", "188 cm"]
        },
        "work": {
            "occupation": "CEO of Wayne Enterprises",
            "base": "Gotham City"
        }
    }
    hero_cache.clear()
    with aioresponses() as m:
        m.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id}", payload=expected_response)
        async with aiohttp.ClientSession() as session:
            result = await get_hero_info(session, character_id)
    assert result == expected_response

@pytest.mark.asyncio
async def test_get_hero_info_success():
    """Тестирование ошибки при получении информации о герое."""
    character_id = 1
    hero_cache.clear()
    with aioresponses() as m:
        m.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/{character_id}", status=404)
        async with aiohttp.ClientSession() as session:
            with pytest.raises(RuntimeError) as exc_info:
                await get_hero_info(session, character_id)
            assert "Ошибка при получении информации о герое с ID 1: 404" in str(exc_info.value)

@pytest.fixture
def mock_hero_cache():
    mock_hero_cache = {}
    MAX_ID = 6
    mock_hero_cache[1] = {
        "id": 1,
        "appearance": {
            "gender": "Male",
            "height": ["5'10", "178 cm"]
        },
        "work": {
            "base": "Gotham City"
        }
    }
    mock_hero_cache[2] = {
        "id": 2,
        "appearance": {
            "gender": "Male",
            "height": ["6'3", "191 cm"]
        },
        "work": {
            "base": "Metropolis"
        }
    }
    mock_hero_cache[3] = {
        "id": 3,
        "appearance": {
            "gender": "Male",
            "height": ["5'8", "173 cm"]
        },
        "work": {
            "base": "-"
        }
    }
    mock_hero_cache[4] = {
        "id": 4,
        "appearance": {
            "gender": "Female",
            "height": ["5'7", "170 cm"],
        },
        "work": {
            "base": "-"
        }
    }
    mock_hero_cache[5] = {
        "id": 5,
        "appearance": {
            "gender": "Female",
            "height": ["5", "175 cm"],
        },
        "work": {
            "base": "Earth"
        }
    }
    mock_hero_cache[6] = {
        "id": 6,   
        "appearance": {
            "gender": "Female",
            "height": ["5'7", "179 cm"]
        },
        "work": {
            "base": "-"
        }
    }
    return mock_hero_cache

@pytest.mark.asyncio
@patch('asynch_tallest_hero.get_hero_info')
@patch('asynch_tallest_hero.MAX_ID', new=6)
async def test_get_tallest_hero_male_with_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции tallest_hero для героев
    мужского пола с заполненным местом работы.
    """
    mock_get_hero_info.side_effect = lambda session, hero_id: mock_hero_cache[hero_id]
    result = await tallest_hero("Male", True)
    assert result["appearance"]["height"][1] == "191 cm"
    assert result["appearance"]["gender"] == "Male"
    assert result["work"]["base"] == "Metropolis"

@pytest.mark.asyncio
@patch('asynch_tallest_hero.get_hero_info')
@patch('asynch_tallest_hero.MAX_ID', new=6)
async def test_get_tallest_hero_male_without_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции tallest_hero для героев
    мужского пола без работы.
    """
    mock_get_hero_info.side_effect = lambda session, hero_id: mock_hero_cache[hero_id]
    result = await tallest_hero("Male", False)
    assert result["appearance"]["height"][1] == "173 cm"
    assert result["appearance"]["gender"] == "Male"
    assert result["work"]["base"] == "-"

@pytest.mark.asyncio
@patch('asynch_tallest_hero.get_hero_info')
@patch('asynch_tallest_hero.MAX_ID', new=6)
async def test_get_tallest_hero_female_with_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции tallest_hero для героев
    женского пола с заполненным местом работы.
    """
    mock_get_hero_info.side_effect = lambda session, hero_id: mock_hero_cache[hero_id]
    result = await tallest_hero("Female", True)
    assert result["appearance"]["height"][1] == "175 cm"
    assert result["appearance"]["gender"] == "Female"
    assert result["work"]["base"] == "Earth"

@pytest.mark.asyncio
@patch('asynch_tallest_hero.get_hero_info')
@patch('asynch_tallest_hero.MAX_ID', new=6)
async def test_get_tallest_hero_female_without_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции tallest_hero для героев
    женского пола без работы.
    """
    mock_get_hero_info.side_effect = lambda session, hero_id: mock_hero_cache[hero_id]
    result = await tallest_hero("Female", False)
    assert result["appearance"]["height"][1] == "179 cm"
    assert result["appearance"]["gender"] == "Female"
    assert result["work"]["base"] == "-"

@pytest.mark.asyncio
@patch('asynch_tallest_hero.get_hero_info')
async def test_no_heroes_found(mock_hero_cache):
    """
    Тестирование функции tallest_hero
    при отсутствии героев.
    """
    mock_hero_cache.clear()
    mock_hero_cache.return_value = None
    result = await tallest_hero("Male", True)
    assert result == {}