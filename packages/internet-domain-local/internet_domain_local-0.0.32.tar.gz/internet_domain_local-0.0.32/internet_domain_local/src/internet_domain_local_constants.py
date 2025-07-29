from logger_local.LoggerComponentEnum import LoggerComponentEnum

INTERNET_DOMAIN_LOCAL_PYTHON_COMPONENT_ID = 5000004
INTERNET_DOMAIN_LOCAL_PYTHON_COMPONENT_NAME = 'domain local'
DEVELOPER_EMAIL = "sahar.g@circ.zone"
INTERNET_DOMAIN_PYTHON_PACKAGE_CODE_LOGGER_OBJECT = {
    'component_id': INTERNET_DOMAIN_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': INTERNET_DOMAIN_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}

INTERNET_DOMAIN_PYTHON_PACKAGE_TEST_LOGGER_OBJECT = {
    'component_id': INTERNET_DOMAIN_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': INTERNET_DOMAIN_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': DEVELOPER_EMAIL
}
