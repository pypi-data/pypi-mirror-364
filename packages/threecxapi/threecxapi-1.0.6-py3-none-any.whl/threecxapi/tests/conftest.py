import pytest


@pytest.fixture
def generic_error_response():
    return {
        "error": {
            "code": "",
            "message": "SAMPLE_FIELD:\nWARNINGS.XAPI.SAMPLE_ERROR",
            "details": [{"code": "", "message": "WARNINGS.XAPI.SAMPLE_ERROR", "target": "SAMPLE_FIELD"}],
        }
    }


@pytest.fixture
def group_error(generic_error_response):
    return generic_error_response


@pytest.fixture
def user_error(generic_error_response):
    return generic_error_response
