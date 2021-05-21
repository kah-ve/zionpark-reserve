import discord
import subprocess
import general_utils

client = discord.Client()


@client.event
async def on_ready():
    output_text = "We have logged in as {0.user}".format(client)
    print(output_text)
    await client.get_channel(general_utils.DISCORD_CHANNEL_ID).send(output_text)


@client.event
async def on_message(message):
    global subprocess

    if message.author == client.user:
        return

    message_content = message.content
    print(f"Received message {message_content} from DISCORD")

    if message_content.lower() == "stop":
        with open("output.log", "w") as f:
            f.write("STOP")
    elif message_content.lower() == "start":
        with open("output.log", "w") as f:
            f.write("START")


if __name__ == "__main__":
    client.run(general_utils.DISCORD_BOT_TOKEN)
