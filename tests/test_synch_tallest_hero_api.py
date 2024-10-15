import os

import pytest
import requests_mock
from dotenv import load_dotenv
from unittest.mock import patch

from synch_tallest_hero_api import get_hero_info, convert_height_to_cm, get_tallest_hero

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
    }
]

def test_get_hero_info_cache():
    """Тестирование кэширования информации о герое."""
    with requests_mock.Mocker() as m:
        m.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/1", status_code=200, json=mock_hero_response[0])
        hero_info_first_call = get_hero_info(1)
        hero_info_second_call = get_hero_info(1)
    assert hero_info_first_call == hero_info_second_call
    assert m.call_count == 1

def test_get_hero_info_success():
    """Тестирование успешного получения информации о герое."""
    with requests_mock.Mocker() as m:
        m.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/1", status_code=200, json=mock_hero_response[0])
        hero_info = get_hero_info(1)
    assert hero_info["id"] == 1
    assert hero_info["name"] == "Batman"
    assert hero_info["appearance"]["gender"] == "Male"
    assert hero_info["work"]["base"] == "Gotham City"

def test_get_hero_info_failure():
    """Тестирование ошибки при получении информации о герое."""
    with requests_mock.Mocker() as m:
        m.get(f"https://superheroapi.com/api/{ACCESS_TOKEN}/1", status_code=404)
        try:
            get_hero_info(1)
        except RuntimeError as exc:
            assert "Ошибка при получении информации о герое с ID 1: 404" in str(exc)


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

@patch('synch_tallest_hero_api.get_hero_info')
@patch('synch_tallest_hero_api.MAX_ID', new=6)
def test_get_tallest_hero_male_with_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции get_tallest_hero для героев
    мужского пола с заполненным местом работы.
    """
    mock_get_hero_info.side_effect = lambda hero_id: mock_hero_cache[hero_id]
    result = get_tallest_hero("Male", True)
    assert result["appearance"]["height"][1] == "191 cm"
    assert result["appearance"]["gender"] == "Male"
    assert result["work"]["base"] == "Metropolis"


@patch('synch_tallest_hero_api.get_hero_info')
@patch('synch_tallest_hero_api.MAX_ID', new=6)
def test_get_tallest_hero_male_without_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции get_tallest_hero для героев
    мужского пола без работы.
    """
    mock_get_hero_info.side_effect = lambda hero_id: mock_hero_cache[hero_id]
    result = get_tallest_hero("Male", False)
    assert result["appearance"]["height"][1] == "173 cm"
    assert result["appearance"]["gender"] == "Male"
    assert result["work"]["base"] == "-"

@patch('synch_tallest_hero_api.get_hero_info')
@patch('synch_tallest_hero_api.MAX_ID', new=6)
def test_get_tallest_hero_female_with_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции get_tallest_hero для героев
    женского пола с заполненным местом работы.
    """
    mock_get_hero_info.side_effect = lambda hero_id: mock_hero_cache[hero_id]
    result = get_tallest_hero("Female", True)
    assert result["appearance"]["height"][1] == "175 cm"
    assert result["appearance"]["gender"] == "Female"
    assert result["work"]["base"] == "Earth"

@patch('synch_tallest_hero_api.get_hero_info')
@patch('synch_tallest_hero_api.MAX_ID', new=6)
def test_get_tallest_hero_female_without_job(mock_get_hero_info, mock_hero_cache):
    """
    Тестирование функции get_tallest_hero для героев
    женского пола без работы.
    """
    mock_get_hero_info.side_effect = lambda hero_id: mock_hero_cache[hero_id]
    result = get_tallest_hero("Female", False)
    assert result["appearance"]["height"][1] == "179 cm"
    assert result["appearance"]["gender"] == "Female"
    assert result["work"]["base"] == "-"

@patch('synch_tallest_hero_api.get_hero_info')
@patch('synch_tallest_hero_api.MAX_ID', new=2)
def test_invalid_height_format(mock_hero_cache):
    """
    Тестирование функции get_tallest_hero
    при некорректном формате роста.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = [
            {
                "appearance": {
                    "gender": "Male",
                    "height": ["-", "-178 cm"]
                },
                "work": {
                    "base": "Gotham"
                }
            },
            {
                "appearance": {
                    "gender": "Male",
                    "height": ["", "178 kg"]
                },
                "work": {
                    "base": "Gotham2"
                }
            }
        ]
        result = get_tallest_hero("Male", True)        
        assert result == {}

@patch('synch_tallest_hero_api.get_hero_info')
def test_no_heroes_found(mock_hero_cache):
    """
    Тестирование функции get_tallest_hero
    при отсутствии героев.
    """
    mock_hero_cache.clear()
    result = get_tallest_hero("Male", True)
    assert result == {}