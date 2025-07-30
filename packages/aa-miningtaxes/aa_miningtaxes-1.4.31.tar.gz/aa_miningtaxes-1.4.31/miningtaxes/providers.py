from pathlib import Path

from esi.clients import EsiClientProvider

from . import __version__

spec_file = Path(__file__).parent / "swagger.json"
esi = EsiClientProvider(app_info_text=f"aa-miningtaxes v{__version__}")
