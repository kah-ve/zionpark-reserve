# zionpark-reserve
Campsite and Shuttle reservation helper (only adds to cart)

Can run the scripts to reserve a campsite or shuttle and then be notified about the results through discord. This can be very useful since there are many cancellations of campsites 

Will update code and give a better GUI later.

### Environment Variables
In the general utils file you can see several environment variables being loaded with load_dotenv().

You need to have the environment variables in a .env file in the same directory where the reserve scripts are.

Within this file you need to have each of these environment variables modified for your purpose. Also you need to have the geckodriver downloaded and have a path to it through the WEDDRIVER_PATH variable below. The discord webhook url is where notifications about the success/failure of your script will be sent.
```
WEBDRIVER_PATH="./driver/geckodriver" (download mozilla's geckodriver and change this path to point to it)
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/[your-unique-ids-here]"
ZION_USERNAME=myemail@email.com (this is the recreation.gov username)
ZION_PASSWORD=mypassword (recreation.gov account password)
DISCORD_CHANNEL_ID=the channel id I want to be able to send commands to the bot with (for the shuttle reservation)
DISCORD_BOT_TOKEN=the bot token that will be used to send a message to discord for notification
```

### Reserve Camp
For now, can run reserve_camp with either the W or S argument

    python reserve_camp.py W
    
The W stands for watching the watchman campground while S stands for the south campground.

To watch a certain date for reserving a camp, need to modify the desired_date_global variable at the top to your desired date. For May 26, 2021, you'd write 05/26/2021. The script will then navigate to that date and check for any empty spots.

### Reserve Shuttle

You can run reserve_shuttle through the command line with 
    
    python reserve_shuttle.py 29 6,7,8,9
    
Or by using the discord channel you hooked your bot to, where you can simply type

    29 6,7,8,9
    
which will kick off the reserve_shuttle script to try to reserve a shuttle for that month's 29th day.

You can stop the discord bot by typing in 

    STOP
    
and begin again by typing

    START
    
then again kicking off a search for shuttles with

    26 6,7,8,9
    
The 6,7,8,9 means we are searching for any shuttle tickets in the times 6-7,7-8,8-9,9-10.
   
Note. You need to be writing these commands in the channel that you have given your DISCORD CHANNEL ID for, not the webhook url for the channel that the bot will be posting notifications to.





