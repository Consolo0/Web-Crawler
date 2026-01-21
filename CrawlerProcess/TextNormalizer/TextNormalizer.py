import re
from decimal import Decimal, InvalidOperation


class TextNormalizer:

    PRICE_REGEX = re.compile(r"[^\d,\.]")

    @staticmethod
    def normalize(text: str) -> Decimal | None:
        """
        Normalizes a price string into Decimal.

        Examples:
            "$239.990"        -> Decimal("239990")
            "CLP 1.299.990"   -> Decimal("1299990")
            "239,990"         -> Decimal("239990")

        Returns None if normalization fails.
        """
        if not text:
            return None

        # remove currency symbols and spaces
        cleaned = TextNormalizer.PRICE_REGEX.sub("", text)

        # Chile / LatAm format handling
        # thousands: dot
        # decimals: comma (rare in prices)
        if cleaned.count(",") == 1 and cleaned.count(".") >= 1:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(".", "").replace(",", "")

        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None

    @staticmethod
    def normalize_rating(text: str) -> float | None:
        """
        Normalizes rating text.

        Examples:
            "(5.0)" -> 5.0
            "4,8"   -> 4.8
        """
        if not text:
            return None

        cleaned = re.sub(r"[^\d,\.]", "", text).replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Generic text cleanup.
        """
        if not text:
            return ""

        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text
