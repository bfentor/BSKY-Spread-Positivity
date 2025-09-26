import os
from time import sleep
import dotenv
from atproto import Client
from atproto import models
from atproto import client_utils
from random import choice
import json

# TO DO: Populate a json with movie quote insults

FETCH_NOTIFICATIONS_DELAY_SEC = 1

def main() -> None:
    dotenv.load_dotenv()

    client = Client()
    client.login(f"{os.getenv("BSKY_USERNAME")}", f"{os.getenv("BSKY_PASSWORD")}")

    data = json.load(open("insults.json", "r"))

    # fetch new notifications
    while True:
        last_seen_at = client.get_current_time_iso()

        response = client.app.bsky.notification.list_notifications()
        for notification in response.notifications:
            if (notification.is_read == False) and (notification.reason == "mention"):
                
                thread = client.get_post_thread(uri=notification.uri)
                post = models.base.ModelBase(uri=notification.uri, cid=notification.cid)

                if thread["thread"]["post"]["record"]["reply"] == None:
                    rootPost = post
                else:
                    rootPost = thread["thread"]["post"]["record"]["reply"]["root"]

                parentRef = models.create_strong_ref(post)
                rootRef = models.create_strong_ref(rootPost)

                client.send_post(
                    text=choice(list(data.values())),
                    reply_to=models.AppBskyFeedPost.ReplyRef(parent=parentRef, root=rootRef)
                )
                
                client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
                print(f"Replied at {last_seen_at}");

        sleep(FETCH_NOTIFICATIONS_DELAY_SEC)

if __name__ == '__main__':
    main()