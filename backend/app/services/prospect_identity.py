import hashlib
import re
import unicodedata


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", plain.casefold().strip())


def build_prospect_dedup_key(name: str, city: str, state: str) -> str:
    """Create a stable MVP key using fields available at discovery time."""
    canonical = "|".join(
        (
            _normalize_text(name),
            _normalize_text(city),
            state.strip().upper(),
        )
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
