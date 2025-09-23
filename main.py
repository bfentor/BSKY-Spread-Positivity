import os
from time import sleep
import dotenv
from atproto import Client
from atproto import models
from atproto import client_utils

# how often we should check for new notifications
FETCH_NOTIFICATIONS_DELAY_SEC = 3


def main() -> None:
    dotenv.load_dotenv()

    client = Client()
    client.login(f"{os.getenv("BSKY_USERNAME")}", f"{os.getenv("BSKY_PASSWORD")}")

    # fetch new notifications
    while True:
        last_seen_at = client.get_current_time_iso()

        response = client.app.bsky.notification.list_notifications()
        for notification in response.notifications:
            print(f"{notification.is_read}, {notification.reason}")
            if (notification.is_read == False) and (notification.reason == "mention"):
                post = models.base.ModelBase(uri=notification.uri, cid=notification.cid,)
                # print(post)
                root_post_ref = models.create_strong_ref(post)
                client.send_post(
                    text='Get lost',
                    reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref, root=root_post_ref)
                )
                client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
                print(":D");
            
            else:
                print("Nothing here...")
        print("================")
        sleep(FETCH_NOTIFICATIONS_DELAY_SEC)


if __name__ == '__main__':
    main()