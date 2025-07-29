from django.db import models


class DecimalField(models.DecimalField):
    description = "Extended DecimalField"

    def __init__(self, *args, is_currency=True, prefix="", suffix="", **kwargs):
        super().__init__(*args, **kwargs)
        self.is_currency = is_currency and prefix == "" and suffix == ""
        self.prefix = prefix
        self.suffix = suffix


class IntegerField(models.IntegerField):
    description = "Extended IntegerField allowing pattern_format for inputs"

    def __init__(self, *args, pattern_format=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern_format = pattern_format
