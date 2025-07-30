from aenum import IntEnum
from volworld_common.api.enum.common_error_code import CommonErrorCode


class ErrorCode(IntEnum):

    NoError = CommonErrorCode.NoError.value

    UserNameExisting = 1001

