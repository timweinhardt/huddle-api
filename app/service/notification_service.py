from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    DeviceNotRegisteredError,
)


class NotificationService:
    def __init__(self, token_repo):
        self.push_client = PushClient()  # optional access token config
        self.token_repo = token_repo

    def notify(
        self,
        recipient_tokens: list[str],
        title: str,
        body,
        data: dict,
        sound: str = "default",
    ):
        messages = [
            PushMessage(
                to=token,
                title=title,
                body=body,
                data=data,
                sound=sound,
            )
            for token in recipient_tokens
        ]

        for chunk in self.push_client.publish_multiple(messages):
            for response in chunk:
                try:
                    response.validate_response()
                except DeviceNotRegisteredError:
                    self.token_repo.deactivate_token(response.push_message.to)
                except PushServerError:
                    # log and retry strategy (or send to DLQ/SQS)
                    pass
                except Exception:
                    pass
