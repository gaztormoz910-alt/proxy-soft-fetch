from gui import ISO_TO_NAME, NAME_TO_ISO


def test_every_country_name_maps_back_to_a_code():
    for lang, mapping in ISO_TO_NAME.items():
        for iso, name in mapping.items():
            assert name in NAME_TO_ISO, f"{lang}/{iso}: «{name}» нет в обратном индексе"


def test_index_covers_both_languages():
    assert NAME_TO_ISO[ISO_TO_NAME["RU"]["DE"]] == "DE"
    assert NAME_TO_ISO[ISO_TO_NAME["EN"]["DE"]] == "DE"


def test_unknown_is_present():
    assert NAME_TO_ISO["Unknown"] == "Unknown"
    assert NAME_TO_ISO["Неизвестно"] == "Unknown"


def substring_lookup(name):
    for mapping in ISO_TO_NAME.values():
        for iso, candidate in mapping.items():
            if candidate in name:
                return iso
    return ""


BROKEN_BY_SUBSTRING = [
    ("RU", "GQ", "GN"),
    ("RU", "GW", "GN"),
    ("RU", "SS", "SD"),
    ("RU", "VI", "US"),
    ("RU", "VG", "GB"),
    ("EN", "BQ", "NL"),
    ("EN", "GQ", "GN"),
    ("EN", "GS", "GE"),
    ("EN", "GW", "GN"),
    ("EN", "IO", "IN"),
    ("EN", "MO", "CN"),
    ("EN", "SS", "SD"),
]


def test_substring_lookup_really_confused_nested_names():
    for lang, iso, wrong in BROKEN_BY_SUBSTRING:
        name = ISO_TO_NAME[lang][iso]
        assert substring_lookup(name) == wrong, (
            f"{lang}/{iso} «{name}»: ожидалась старая ошибка → {wrong}")


def test_exact_lookup_fixes_every_broken_name():
    for lang, iso, _wrong in BROKEN_BY_SUBSTRING:
        name = ISO_TO_NAME[lang][iso]
        assert NAME_TO_ISO[name] == iso, f"{lang}/{iso}: «{name}»"


def test_exact_lookup_is_correct_for_every_country():
    for lang, mapping in ISO_TO_NAME.items():
        for iso, name in mapping.items():
            assert NAME_TO_ISO[name] == iso, f"{lang}/{iso}: «{name}»"


def test_no_name_is_shared_between_two_different_countries():
    seen = {}
    collisions = []
    for lang, mapping in ISO_TO_NAME.items():
        for iso, name in mapping.items():
            if name in seen and seen[name] != iso:
                collisions.append((name, seen[name], iso))
            seen[name] = iso
    assert collisions == [], f"одинаковые названия у разных стран: {collisions}"


def test_translation_round_trip_is_stable():
    for iso, ru_name in ISO_TO_NAME["RU"].items():
        en_name = ISO_TO_NAME["EN"][NAME_TO_ISO[ru_name]]
        back = ISO_TO_NAME["RU"][NAME_TO_ISO[en_name]]
        assert back == ru_name, f"{iso}: {ru_name} → {en_name} → {back}"


def test_unrecognised_value_is_left_alone():
    assert NAME_TO_ISO.get("совсем не страна") is None


def test_lookup_is_a_single_dict_hit():
    assert isinstance(NAME_TO_ISO, dict)
    assert len(NAME_TO_ISO) >= len(ISO_TO_NAME["RU"])
