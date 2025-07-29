from django.db import models
from django.core.validators import RegexValidator

from ..utils import get_pattern_format


class CharField(models.CharField):
    description = "Extended CharField allowing pattern_format for inputs"

    def __init__(self, *args, pattern_format=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern_format = pattern_format

        pattern_format__str = get_pattern_format(pattern_format)

        if pattern_format__str:
            kwargs["max_length"] = pattern_format__str.count("#")

        super().__init__(*args, **kwargs)

        if pattern_format__str:
            self.validators.append(
                RegexValidator(
                    regex=f'^\\d{{{pattern_format__str.count("#")}}}$',  # ^\d{11}$
                    message=f'Precisa conter exatamente {pattern_format__str.count("#")} dígitos',
                )
            )
