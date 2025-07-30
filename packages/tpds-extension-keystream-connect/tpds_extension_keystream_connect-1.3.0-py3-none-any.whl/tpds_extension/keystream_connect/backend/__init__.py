import os
from tpds.devices import TpdsBoards, TpdsDevices
from .api.apis import usecase  # noqa: F401


# Add the Board information
TpdsBoards().add_board_info(os.path.join(os.path.dirname(__file__), 'boards'))

# Add the Part information
TpdsDevices().add_device_info(os.path.join(os.path.dirname(__file__), 'parts'))
