import discord


def get_channel_id():
    for server in client.guilds:
        for channel in server.channels:
            if channel.type == "Text":
                print(channel.name)
                print(channel.id)


get_channel_id()
