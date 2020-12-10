from typing import Type
import urllib.parse
import random
from mautrix.types import RoomID
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

    async def send_gif(self, room_id: RoomID, gif_link: str, query: str) -> None:
        resp = await self.http.get(gif_link)
        if resp.status != 200:
            self.log.warning(f"Unexpected status fetching image {url}: {resp.status}")
            return None
        
        data = await resp.read()
        mime = "image/gif" # this really shouldn't change
        uri = await self.client.upload_media(data, mime_type=mime)

        await self.client.send_image(room_id, url=uri, file_name=f"{query}.gif")

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
            source = "translate"

        api_key = self.config["api_key"]
        url_params = urllib.parse.urlencode({"s": search_term, "api_key": api_key})
        response_type = self.config["response_type"]
        # Get random gif url using search term
        async with self.http.get(
            "http://api.giphy.com/v1/gifs/{}?{}".format(source, url_params)
        ) as response:
            data = await response.json()

        # Retrieve gif link from JSON response
        try:
            gif_link = data['data']['images']['original']['url']
        except Exception as e:
            await evt.respond("sorry, i'm drawing a blank")
            return None

        if response_type == "message":
            await evt.respond(gif_link, allow_html=True)  # Respond to user
        elif response_type == "reply":
            await evt.reply(gif_link, allow_html=True)  # Reply to user
        elif response_type == "upload":
            await self.send_gif(evt.room_id, gif_link, search_term) # Upload the GIF to the room
        else:
            await evt.respond("something is wrong with my config, be sure to set a response_type")
