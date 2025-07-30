from typing import Final


class FrontEndUrlRef:
    AWS: Final[str] = "https://958e36p8n5.execute-api.ap-northeast-1.amazonaws.com/prod/"


class FrontEndUrl:
    Root = FrontEndUrlRef.AWS
