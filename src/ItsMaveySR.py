import os

from bot import Bot


def create_env():
    spotify_client_id = input('Enter your Spotify Client ID: ')
    spotify_client_secret = input('Enter your Spotify Client Secret: ')
    twitch_token = input('Enter your Twitch OAuth Token: ')
    twitch_channel = input('Enter your Twitch Channel Name: ')

    with open('.env', 'w') as f:
        f.write(f'SPOTIFY_CLIENT_ID={spotify_client_id}\n')
        f.write(f'SPOTIFY_CLIENT_SECRET={spotify_client_secret}\n')
        f.write(f'TWITCH_TOKEN={twitch_token}\n')
        f.write(f'TWITCH_CHANNEL={twitch_channel}\n')


def main():
    if not os.path.exists('.env'):
        create_env()

    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
