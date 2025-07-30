from typing import Final


class ApiUrlRef:
    AWS: Final[str] = "https://958e36p8n5.execute-api.ap-northeast-1.amazonaws.com/prod/"
    LocalNodeJs: Final[str] = "http://localhost:33000/"


class ApiUrl:
    Root = ApiUrlRef.AWS
