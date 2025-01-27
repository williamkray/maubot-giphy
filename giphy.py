from typing import Type
import urllib.parse
import random
from mautrix.types import RoomID, ImageInfo
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command


# Setup config file
class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("api_key")
        helper.copy("source")
        helper.copy("response_type")


class GiphyPlugin(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    async def send_gif(self, room_id: RoomID, gif_link: str, query: str, info: dict) -> None:
        resp = await self.http.get(gif_link)
        if resp.status != 200:
            await evt.respond(f"Unexpected status fetching image {url}: {resp.status}")
            return None
        
        data = await resp.read()
        mime = info['mime'] 
        filename = f"{query}.gif" if len(query) > 0 else "giphy.gif"
        uri = await self.client.upload_media(data, mime_type=mime, filename=filename)

        await self.client.send_image(room_id, url=uri, file_name=filename,
                info=ImageInfo(
                        mimetype=info['mime'],
                        width=info['width'],
                        height=info['height'],
                        size=info['size']
                    ))

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new("giphy")
    @command.argument("search_term", pass_raw=True, required=False)
    async def handler(self, evt: MessageEvent, search_term: str) -> None:
        await evt.mark_read()
        if not search_term:
            # If user doesn't supply a search term, set to empty string
            search_term = ""
            source = self.config["source"]
        else:
            source = "search"

        api_key = self.config["api_key"]
        url_params = urllib.parse.urlencode({"q": search_term, "api_key": api_key, "limit": 5})
        response_type = self.config["response_type"]
        # Get random gif url using search term
        async with self.http.get(
            "http://api.giphy.com/v1/gifs/{}?{}".format(source, url_params)
        ) as response:
            data = await response.json()

        # Retrieve gif link from JSON response
        try:
            picked_gif = random.choice(data['data'])
            gif_link = picked_gif['images']['original']['url']
            info = {}
            info['width'] = int(picked_gif['images']['original']['width']) or 480
            info['height'] = int(picked_gif['images']['original']['height']) or 270
            info['size'] = int(picked_gif['images']['original']['size'])
            info['mime'] = 'image/gif' # this shouldn't really change
        except Exception as e:
            await evt.respond(f"Something went wrong, most likely there were no results 😢")
            return None

        if response_type == "message":
            await evt.respond(gif_link, allow_html=True)  # Respond to user
        elif response_type == "reply":
            await evt.reply(gif_link, allow_html=True)  # Reply to user
        elif response_type == "upload":
            await self.send_gif(evt.room_id, gif_link, search_term, info) # Upload the GIF to the room
        else:
            await evt.respond("something is wrong with my config, be sure to set a response_type")
