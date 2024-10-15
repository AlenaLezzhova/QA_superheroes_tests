import pytest
from unittest.mock import patch
from tallest_hero_all import convert_height_to_cm, get_tallest_hero


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


@pytest.fixture
def mock_api_response():
    return [
        {
            "appearance": {
                "gender": "Male",
                "height": ["5'10", "178 cm"]
            },
            "work": {
                "base": "Gotham"
            }
        },
        {
            "appearance": {
                "gender": "Male",
                "height": ["6'3", "191 cm"]
            },
            "work": {
                "base": "Metropolis"
            }
        },
        {
            "appearance": {
                "gender": "Male",
                "height": ["5'8", "173 cm"]
            },
            "work": {
                "base": "-"
            }
        },
        {
            "appearance": {
                "gender": "Female",
                "height": ["5'7", "170 cm"],
            },
            "work": {
                "base": "-"
            }
        },
        {
            "appearance": {
                "gender": "Female",
                "height": ["-", "175 cm"],
            },
            "work": {
                "base": "Earth"
            }
        },
        {
            "appearance": {
                "gender": "Female",
                "height": ["5'7", "179 cm"]
            },
            "work": {
                "base": "-"
            }
        }
    ]

def test_get_tallest_hero_male_with_job(mock_api_response):
    """
    Тестирование функции get_tallest_hero для героев
    мужского пола с заполненным местом работы.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        result = get_tallest_hero("Male", True)
        assert result["appearance"]["height"][1] == "191 cm"
        assert result["appearance"]["gender"] == "Male"
        assert result["work"]["base"] == "Metropolis"

def test_get_tallest_hero_male_without_job(mock_api_response):
    """
    Тестирование функции get_tallest_hero для героев
    мужского пола без работы.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        result = get_tallest_hero("Male", False)
        assert result["appearance"]["height"][1] == "173 cm"
        assert result["appearance"]["gender"] == "Male"
        assert result["work"]["base"] == "-"

def test_get_tallest_hero_female_with_job(mock_api_response):
    """
    Тестирование функции get_tallest_hero для героев
    женского пола с заполненным местом работы.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        result = get_tallest_hero("Female", True)
        assert result["appearance"]["height"][1] == "175 cm"
        assert result["appearance"]["gender"] == "Female"
        assert result["work"]["base"] == "Earth"

def test_get_tallest_hero_female_without_job(mock_api_response):
    """
    Тестирование функции get_tallest_hero для героев
    женского пола без работы.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        result = get_tallest_hero("Female", False)
        assert result["appearance"]["height"][1] == "179 cm"
        assert result["appearance"]["gender"] == "Female"
        assert result["work"]["base"] == "-"

def test_no_heroes_found():
    """
    Тестирование функции get_tallest_hero
    при отсутствии героев.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = []
        result = get_tallest_hero("Male", True)
        assert result == {}

def test_invalid_height_format():
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