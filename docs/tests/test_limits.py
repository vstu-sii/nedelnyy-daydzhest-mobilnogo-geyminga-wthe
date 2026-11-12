import pytest

def validate_input(text):
    """Имитация функции валидации на входе пайплайна"""
    if not text or not isinstance(text, str):
        raise ValueError("Пустой или невалидный текст")
    if len(text) > 10000:
        raise ValueError("Текст слишком длинный (лимит 10 000 символов)")
    return True

def test_empty_input():
    """Тест: пустой ввод должен выбрасывать ошибку, а не ломать систему"""
    with pytest.raises(ValueError, match="Пустой или невалидный текст"):
        validate_input("")

def test_too_long_input():
    """Тест: превышение лимита символов (деградация)"""
    long_text = "A" * 10001
    with pytest.raises(ValueError, match="Текст слишком длинный"):
        validate_input(long_text)

def test_valid_input():
    """Тест: нормальный текст проходит"""
    assert validate_input("Обычная новость про мобильную игру") == True
