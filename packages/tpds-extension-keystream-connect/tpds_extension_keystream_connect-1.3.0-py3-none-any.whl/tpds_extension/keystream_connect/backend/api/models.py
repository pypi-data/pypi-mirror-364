# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.
from pydantic import BaseModel


class UsecaseResponseModel(BaseModel):
    status: bool = False
    message = "ERROR"
    log: str = ""
