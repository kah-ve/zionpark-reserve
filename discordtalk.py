import discord
import time
import subprocess
import general_utils

client = discord.Client()
from reserve_shuttle import run_main


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

    message_content: str = message.content
    received_msg = f"Received message {message_content} from DISCORD"
    print(received_msg)
    await message.channel.send(received_msg)

    if message_content.lower() == "stop" or message_content.lower() == "start":
        return

    split_msg = message_content.split(" ")
    intended_date = split_msg[0]
    intended_times = split_msg[1]

    try:
        await message.channel.send(f"Kicked off trying to reserve shuttles!")
        run_main(intended_date, intended_times)

    except:
        await message.channel.send(f"An exception was thrown. Code has stopped running!")


def run_again():
    while True:
        try:
            client.run(general_utils.DISCORD_BOT_TOKEN)
        except:
            print("Run failed. Trying to run again")
            time.sleep(1)
            run_again()


if __name__ == "__main__":
    run_again()
