from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    DeviceNotRegisteredError,
)

from app.service.push_token_repository import ExponentPushTokenRepository


class NotificationService:
    def __init__(self):
        self.push_client = PushClient()
        self.token_repo = ExponentPushTokenRepository()

    def notify(
        self,
        recipient_user_ids: list[str],
        title: str,
        body,
        data: dict,
        sound: str = "default",
    ):
        recipient_tokens = [
            token
            for user_id in recipient_user_ids
            for token in self.token_repo.get_tokens_for_user(user_id)
        ]

        print(recipient_tokens)
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
