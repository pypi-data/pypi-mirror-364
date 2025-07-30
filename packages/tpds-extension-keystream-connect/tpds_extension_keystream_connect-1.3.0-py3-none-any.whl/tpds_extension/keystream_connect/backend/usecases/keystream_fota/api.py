# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from fastapi import Body
from fastapi.routing import APIRouter
from ...api.models import UsecaseResponseModel
from .FoTA import FoTA

fota_router = APIRouter(prefix="/fota")
uc_object = None


@fota_router.post("/setup")
def fota_setup() -> UsecaseResponseModel:
    """
    Sets up the FoTA Usecase.

    Returns:
        UsecaseResponseModel: A model containing the status, message, and log of the FoTA Usecaser setup process.
    """
    global uc_object
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        uc_object = FoTA()
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@fota_router.post("/generate_resources")
def fota_generate_resources(user_inputs=Body()) -> UsecaseResponseModel:
    """
    Generates Fota resources based on the provided user inputs.

    Args:
        user_inputs (Body): The input data required to generate Fota resources.

    Returns:
        UsecaseResponseModel: The response model containing the result for generated FoTA resources.
    """
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert uc_object is not None, "FoTA usecase object is not initialized. Please restart usecase!"
        response = uc_object.generate_resources(user_inputs)
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@fota_router.post("/proto_provision")
def fota_proto_provision(user_inputs=Body()) -> UsecaseResponseModel:
    """
    Provisions the FoTA Resources using the provided user inputs.

    Args:
        user_inputs (Body, optional): The user inputs required for provisioning.

    Returns:
        UsecaseResponseModel: The response model containing the result of the provisioning process.
    """
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert uc_object is not None, "FoTA usecase object is not initialized. Please restart usecase!"
        response = uc_object.proto_provision(user_inputs)
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@fota_router.post("/teardown")
def fota_teardown() -> UsecaseResponseModel:
    """
    Perform the teardown process for FoTA.

    This function handles the necessary steps to properly teardown the FoTA Usecase.
    It returns a UsecaseResponseModel indicating the status of the operation.

    Returns:
        UsecaseResponseModel: An object containing the status, message, and log of the teardown process.
    """
    global uc_object
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert uc_object is not None, "FoTA usecase object is not initialized. Teardown failed!"
        uc_object.logger.close()
        uc_object = None
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response
