from twitchio.ext import commands
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

import os


class Bot(commands.Bot):

    def __init__(self):
        spotify_redirect_uri = 'http://localhost:8080'

        load_dotenv()

        self.spotify = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                redirect_uri=spotify_redirect_uri,
                scope="user-read-playback-state user-modify-playback-state"
            )
        )

        super().__init__(token=os.getenv('TWITCH_TOKEN'), prefix='!', initial_channels=[os.getenv('TWITCH_CHANNEL')])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        # Check if the message or author is None
        if message.author is None:
            print("Received a message with no author.")
            return

        await self.handle_commands(message)

    @commands.command(name='sr')
    async def sr(self, ctx):
        song_title = ctx.message.content[len('!sr '):].strip()
        if song_title:
            try:
                # Search for the song on Spotify
                results = self.spotify.search(q=song_title, type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    track_uri = track['uri']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']

                    # Add the track to the queue
                    self.spotify.add_to_queue(track_uri)
                    await ctx.send(f'Added {track_name} by {track_artist} to the queue.')
                else:
                    await ctx.send('No results found on Spotify.')
            except Exception as e:
                print(e)
                await ctx.send('An error occurred while adding the song to the queue.')
        else:
            await ctx.send('Please provide a song title.')

    @commands.command(name='queue')
    async def queue(self, ctx):
        queue = self.spotify.get_queue()
        if queue:
            queue_list = '\n'.join(
                [f'{i + 1}. {track["name"]} by {track["artists"][0]["name"]}' for i, track in enumerate(queue)])
            await ctx.send(f'Current Queue:\n{queue_list}')
        else:
            await ctx.send('The queue is empty.')

    @commands.command(name='current')
    async def current(self, ctx):
        try:
            # Get the current playback state
            current_playback = self.spotify.current_playback()

            if current_playback and current_playback['is_playing']:
                track = current_playback.get('item')
                if track:
                    track_name = track.get('name', 'Unknown Track')

                    # Handle multiple artists
                    artists = track.get('artists', [])
                    artist_names = ', '.join(artist.get('name', 'Unknown Artist') for artist in artists)

                    await ctx.send(f'Currently playing: {track_name} by {artist_names}')
                else:
                    await ctx.send('No track information available.')
            else:
                await ctx.send('No song is currently playing.')
        except Exception as e:
            print(e)
            await ctx.send('An error occurred while fetching the current song.')

    # %% Mod Commands

    @commands.command(name='skip')
    async def skip(self, ctx):
        if ctx.author.is_mod or ctx.author.is_broadcaster:
            self.spotify.next_track()
            await ctx.send('Skipped the current track.')

    @commands.command(name='replay')
    async def replay(self, ctx):
        if ctx.author.is_mod or ctx.author.is_broadcaster:
            self.spotify.previous_track()
            await ctx.send('Replayed the current track.')

    @commands.command(name='pause')
    async def pause(self, ctx):
        if ctx.author.is_mod or ctx.author.is_broadcaster:
            self.spotify.pause_playback()
            await ctx.send('Paused the current track.')

    @commands.command(name='play')
    async def resume(self, ctx):
        if ctx.author.is_mod or ctx.author.is_broadcaster:
            self.spotify.start_playback()
            await ctx.send('Resumed the current track.')
