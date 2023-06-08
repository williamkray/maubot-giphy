# Giphy Maubot

NOTICE: this fork is no longer maintained, please use [GifMe](https://github.com/williamkray/maubot-gifme) instead.

A simple [maubot](https://github.com/maubot/maubot) that generates a random gif given a search term.
This project was forked from [TomCasavant/GiphyMaubot](https://github.com/TomCasavant/GiphyMaubot), which was a great starting point, but I wanted to see a few more changes.

## Setup
1. Get API key from [giphy](https://developers.giphy.com/docs/)
2. Fill in api_key field in base-config.yaml config file or in online maubot config editor
3. Decide what endpoint to get random gifs from (e.g. trending, random) in config file
4. Choose a response type:
  - message will send a regular message to the room
  - reply will send a quoted reply message to the room
  - upload will actually upload the GIF as an image to the room

## Usage
'!giphy word' - Bot replies with a link to a gif given the search term
'!giphy' - Bot replies with a link to a random gif

**NOTE: random gif response is currently broken.** This is for a couple reasons:

  1. The Giphy "translate" api endpoint has recently turned into hot garbage, so the code was refactored to use the
     "search" api endpoint, and pick a random gif from the top 5 results.
  2. The "search" endpoint uses a different letter for mysterious reasons to identify the query string to use (`q`
     instead of `s`)
  3. I'm too lazy to go through the trouble of writing an if/else statement to modify that letter for a feature that
     frankly nobody has ever used even once in the time I've been running my bot.
