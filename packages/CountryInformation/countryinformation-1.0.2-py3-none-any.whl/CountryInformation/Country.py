from .Language import Language


class Country:
    common_name_in_english: str
    official_name_in_english: str
    country_code: str
    languages: list[Language]

    def __init__(self, common_name_in_english: str, official_name_in_english: str, country_code: str, languages: list[Language]):
        self.common_name_in_english = common_name_in_english
        self.official_name_in_english = official_name_in_english
        self.country_code = country_code
        self.languages = languages

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Country):
            return False
        return self.common_name_in_english == other.common_name_in_english

    def __hash__(self):
        return hash(self.common_name_in_english)
