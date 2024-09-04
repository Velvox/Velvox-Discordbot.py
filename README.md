# Velvox-Discordbot.py | THIS BOT IS STILL IN BETA!
#### Basic functions:
Moderation, ticketing, games, social notifications & more
#### Advanced functions:
Automated Anti-Raid & Anti-scam functions

## Currently implemented 
#### Features:
- Ticket system
- Youtube notification (using YouTubes RSS feed)

## Bot setup

### Using Velvox Gamehosting

1. **Download the Bot Package**

   Download the `.tar` package of the bot from the [releases page](https://github.com/Velvox/Velvox-Discordbot.py/releases) or import it in to the server.

2. **Upload the Package to Velvox Gamehosting**

    - Buy your [bot (Discord bot.py)](https://billing.velvox.net/index.php/store/discord-bot) and use "Python Generic"
    - Then go to the [gamepanel](https://game.velvox.net) and go to "your server" > files and drop the .tar file in to the `/home/container/` directory, and extract it.
    - Create a database in the "Database" tab and write the login information down.

3. **Configure the Bot**

   - Open the `bot.py` and edit the the `def get_mysql_connection` and put the correct login data in to the file.
     ```python
        # MySQL Database Configuration
        MYSQL_HOST = "yourdatabasehost" # MySQL database host IP
        MYSQL_USER = "yourdatabaseuser" # MySQL user
        MYSQL_PASSWORD = "yourdatabasepassword" # MySQL password
        MYSQL_DATABASE = "yourdatabasename" # MySQL database name
     ```
    - Then scroll down to the last line of code to the `bot.run()` statement. and add your bot token you can get this at the [Discord Developer Portal](https://discord.com/developers).
        ```python
        # Run the bot with your token
        bot.run()
        ```
    - Make sure that the MySQL database has the necessary tabels, by default the bot generates them automaticly but it could error.
        ```sql
        CREATE TABLE IF NOT EXISTS channel_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            discord_channel_id BIGINT NOT NULL,
            youtube_channel_id VARCHAR(100) NOT NULL,
            last_announced_video_id VARCHAR(100) DEFAULT NULL
        );
        ```

4. **Install Required Packages**

   - By default the panel should install the default and neccasary packages. If you get any errors contact thier [support](https://billing.velvox.net/submitticket.php).

5. **Run the Bot**

   - If you configured your bot the right way when you click "Start" in the gamepanel it should start and you can start using your bot!
   - Ensure it has the right permissions set in the [Discord Developer Portal](https://discord.com/developers).
   - Go ahead to the [commands section](#commands). And you can setup your bot inside your discord server.

## Local installation
Any explanation for this will come in the future.

## Commands
All the commands work with [Discord Slashcommands](https://discord.com/blog/welcome-to-the-new-era-of-discord-apps)

The commands supported by this bot are now.

- Ticket commands
    - **Important!**

        `/setupticketdatabase` This writes the needed database tables in the database defined in the `config.py`.

        `/ticketsetcatogory` This sets the category the tickets will "spawn" in.

        `/setticketrole` This sets the role that will have access to the ticket's (Could error, it is better to fix this in the category permissions).

    - Standard commands

`/adduser` To add a user to a ticket.

`/removeuser` To remove the user from a ticket.

`/ticketlaunch` Puts a embed with ticket creation buttons.

- Youtube notifications
    - **Important!**

    `/youtubesetup` This will setup the channel that needs to be watched

    - Standard commands

`/newestvideo` To display the newest video of the channel configured in `/youtubesetup`

`/reset` Removes the actively watched youtube channel

More functions will be added in the future!

This project is based on the follwing bots, and used and or modified code associated with them.

#### [K03n-Fr3d19/Youtubeupload-announce-Discord.py](https://github.com/K03n-Fr3d19/Youtubeupload-announce-Discord.py) | [License GNU GPL V3.0](https://github.com/K03n-Fr3d19/Youtubeupload-announce-Discord.py/blob/main/LICENSE)
#### [Velvox/Velvox-Ticket-Discordbot.py](https://github.com/Velvox/Velvox-Ticket-Discordbot.py) | [License GNU GPL V3.0](https://github.com/Velvox/Velvox-Ticket-Discordbot.py/blob/main/LICENSE)

## License
This bot is licensed under the [GNU General Public License v3.0](https://github.com/Velvox/Velvox-Discordbot.py/blob/main/LICENSE). See the LICENSE file for more details.
