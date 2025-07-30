"""WizTrader SDK for connecting to the Wizzer."""

from .quotes import QuotesClient
from .apis import WizzerClient

__version__ = "0.37.0"

__all__ = ["QuotesClient", "WizzerClient"]
