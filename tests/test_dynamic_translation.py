"""Ленивая подпись прогресс-бара и совместимость с настоящим tqdm.

_dynamic_t() отдаёт объект, который переводится в момент отрисовки — так
подпись прогресс-бара меняется вместе с языком прямо во время прогона.

Но настоящий tqdm работает с desc как со строкой (`prefix[-2:]`, `prefix + ": "`),
а у объекта был только __str__. В результате `python fetch_proxy.py` падал с
TypeError при создании самого первого прогресс-бара. В GUI баг не проявлялся:
там patch_tqdm() подменяет tqdm заглушкой, которая desc только хранит.
"""
import io

import pytest
from tqdm import tqdm

from fetch_proxy import ProxyHunter


@pytest.fixture
def hunter():
    return ProxyHunter(threads=1, lang="RU")


def test_str_returns_the_translation(hunter):
    assert str(hunter._dynamic_t("tqdm_dl")) == "Загрузка"


def test_translation_follows_a_language_switch(hunter):
    text = hunter._dynamic_t("tqdm_dl")
    assert str(text) == "Загрузка"
    hunter.lang = "EN"
    assert str(text) == "Downloading", "подпись обязана меняться на лету"


def test_unknown_key_falls_back_to_the_key_itself(hunter):
    assert str(hunter._dynamic_t("нет-такого-ключа")) == "нет-такого-ключа"


# ------------------------------------- операции, которые выполняет сам tqdm

def test_slicing_works(hunter):
    """tqdm: prefix[-2:] == ": " """
    assert hunter._dynamic_t("tqdm_dl")[-2:] == "ка"


def test_concatenation_works(hunter):
    """tqdm: prefix + ": " """
    assert hunter._dynamic_t("tqdm_dl") + ": " == "Загрузка: "
    assert "» " + hunter._dynamic_t("tqdm_dl") == "» Загрузка"


def test_len_and_bool_work(hunter):
    text = hunter._dynamic_t("tqdm_dl")
    assert len(text) == len("Загрузка")
    assert bool(text) is True


def test_format_works(hunter):
    assert f"{hunter._dynamic_t('tqdm_dl')}" == "Загрузка"
    assert format(hunter._dynamic_t("tqdm_dl"), ">10") == "  Загрузка"


# ------------------------------------------------ настоящий tqdm, а не мок

def test_real_tqdm_accepts_the_dynamic_description(hunter):
    """Регрессия на падение CLI: раньше здесь был TypeError."""
    # disable=False + собственный поток: нужен реально отрисованный бар,
    # иначе tqdm выключается вне TTY и до подписи дело не доходит
    bar = tqdm(total=3, desc=hunter._dynamic_t("tqdm_dl"),
               disable=False, leave=False, file=io.StringIO())
    try:
        bar.update(1)
        assert "Загрузка" in str(bar)
    finally:
        bar.close()


@pytest.mark.parametrize("key", ["tqdm_dl", "tqdm_check", "tqdm_filter"])
def test_every_progress_bar_description_used_in_the_code_works(hunter, key):
    bar = tqdm(total=1, desc=hunter._dynamic_t(key),
               disable=False, leave=False, file=io.StringIO())
    try:
        bar.update(1)
        assert str(hunter._dynamic_t(key)) in str(bar)
    finally:
        bar.close()
