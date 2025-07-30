# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from fastapi.routing import APIRouter
from ..usecases import fota_router

# Create a new router for the keystream usecase
usecase = APIRouter(prefix="/keystream", tags=["KeyStream_APIs"])
usecase.include_router(fota_router)
