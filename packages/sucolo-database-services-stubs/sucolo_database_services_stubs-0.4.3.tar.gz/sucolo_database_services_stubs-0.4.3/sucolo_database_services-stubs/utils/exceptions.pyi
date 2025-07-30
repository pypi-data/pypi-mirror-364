class SucoloError(Exception):
    ...


class ConfigurationError(SucoloError):
    ...


class DatabaseError(SucoloError):
    ...


class ElasticsearchError(DatabaseError):
    ...


class RedisError(DatabaseError):
    ...


class CityNotFoundError(SucoloError):
    ...


class AmenityNotFoundError(SucoloError):
    ...
