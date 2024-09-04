import discord
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from discord.ext import tasks, commands
from datetime import datetime
import pymysql
import pymysql.cursors
import config
import io

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure the bot can read messages

# Initialize the bot with interactions only (no command prefix needed)
bot = commands.Bot(command_prefix='/', intents=intents)

# Database configuration
db_config = config.db_config
get_db_connection = config.get_db_connection

########################
#   TICKET SYSTEM      #
########################

@bot.tree.command(name="ticketlaunch", description="Create a ticket button")
@commands.has_permissions(administrator=True)
async def ticketlaunch(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Create a Ticket",
        description="Click a button below to open a ticket for the corresponding request type.\n\n **⚙️ General Questions** for all general questions.\n **🤝 Partnership Request** If you want to request a partnership with this server.\n**📝 Apply for Staff** If you want to apply for staff.",
        color=discord.Color.purple()  # Using predefined purple color
    )
    view = discord.ui.View()

    buttons = [
        discord.ui.Button(label="⚙️ General Questions", style=discord.ButtonStyle.primary, custom_id="ticket_general"),
        discord.ui.Button(label="🤝 Partnership Request", style=discord.ButtonStyle.success, custom_id="ticket_partnership"),
        discord.ui.Button(label="📝 Apply for Staff", style=discord.ButtonStyle.secondary, custom_id="ticket_apply_staff")
    ]

    for button in buttons:
        view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="setticketrole", description="Set a role to manage tickets")
@commands.has_permissions(administrator=True)
async def setticketrole(interaction: discord.Interaction, role: discord.Role):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO roles (role_id) VALUES (%s)", (str(role.id),))
    connection.commit()
    cursor.close()
    connection.close()
    embed = discord.Embed(
        title="Role Set",
        description=f"Role {role.name} has been set to manage tickets.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removerole", description="Remove a role from managing tickets")
@commands.has_permissions(administrator=True)
async def removeticketrole(interaction: discord.Interaction, role: discord.Role):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM roles WHERE role_id = %s", (str(role.id),))
    connection.commit()
    cursor.close()
    connection.close()
    embed = discord.Embed(
        title="Role Removed",
        description=f"Role {role.name} has been removed from managing tickets.",
        color=discord.Color.red()  # Using predefined red color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="adduser", description="Add a user to the ticket")
async def adduser(interaction: discord.Interaction, member: discord.Member):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.response.send_message(embed=embed)
        return

    await interaction.channel.set_permissions(member, read_messages=True, send_messages=True)
    embed = discord.Embed(
        title="User Added",
        description=f"Added {member.mention} to the ticket.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removeuser", description="Remove a user from the ticket")
async def removeuser(interaction: discord.Interaction, member: discord.Member):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.response.send_message(embed=embed)
        return

    await interaction.channel.set_permissions(member, read_messages=False, send_messages=False)
    embed = discord.Embed(
        title="User Removed",
        description=f"Removed {member.mention} from the ticket.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticketsetcategory", description="Set a category for tickets")
@commands.has_permissions(administrator=True)
async def setticketcategory(interaction: discord.Interaction, category: discord.CategoryChannel):
    guild_id = interaction.guild.id  # Get the guild ID from the interaction
    
    connection = get_db_connection()  # Assuming get_db_connection() returns a database connection
    cursor = connection.cursor()
    
    # Clear the existing category setting for the specific guild
    cursor.execute("DELETE FROM ticket_category WHERE guild_id = %s", (str(guild_id),))
    
    # Insert the new category ID for the specific guild
    cursor.execute("INSERT INTO ticket_category (guild_id, category_id) VALUES (%s, %s)", (str(guild_id), str(category.id)))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    embed = discord.Embed(
        title="Category Set",
        description=f"Tickets will now be created under the category: {category.name}.",
        color=discord.Color.green()  # Using predefined green color
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setupticketdatabase", description="Set up the database tables for the ticket system")
@commands.has_permissions(administrator=True)
async def setupticketdatabase(interaction: discord.Interaction):
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # SQL statements to create necessary tables
    create_roles_table = """
    CREATE TABLE IF NOT EXISTS roles (
        role_id VARCHAR(255) PRIMARY KEY
    );
    """

    create_ticket_category_table = """
    CREATE TABLE IF NOT EXISTS ticket_category (
        guild_id VARCHAR(255) PRIMARY KEY,
        category_id VARCHAR(255) NOT NULL
    );
    """

    create_tickets_table = """
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        channel_id VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL,
        type VARCHAR(100) NOT NULL,
        guild_id VARCHAR(255) NOT NULL
    );
    """

    # Execute the SQL statements
    try:
        cursor.execute(create_roles_table)
        cursor.execute(create_ticket_category_table)
        cursor.execute(create_tickets_table)
        connection.commit()

        embed = discord.Embed(
            title="✅ Database Setup Complete",
            description="All necessary database tables have been created successfully.\n Or they where already there.",
            color=discord.Color.green()  # Using predefined green color
        )
    except Exception as e:
        embed = discord.Embed(
            title="❌ Database Setup Failed",
            description=f"An error occurred while setting up the database: {e}",
            color=discord.Color.red()  # Using predefined red color
        )
    finally:
        cursor.close()
        connection.close()

    await interaction.response.send_message(embed=embed, ephemeral=True)

def get_allowed_roles():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT role_id FROM roles")
    roles = cursor.fetchall()
    cursor.close()
    connection.close()
    return [int(role[0]) for role in roles]

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        if custom_id == "ticket_general":
            await handle_open_ticket(interaction, "General Questions")
        elif custom_id == "ticket_partnership":
            await handle_open_ticket(interaction, "Partnership Request")
        elif custom_id == "ticket_apply_staff":
            await handle_open_ticket(interaction, "Apply for Staff")
        elif custom_id == "close_ticket":
            await handle_close_ticket(interaction)
        elif custom_id == "confirm_close":
            await confirm_close_ticket(interaction)
        elif custom_id == "cancel_close":
            await cancel_close_ticket(interaction)

async def handle_open_ticket(interaction: discord.Interaction, ticket_type: str):
    await interaction.response.defer()  # Acknowledge the interaction

    guild_id = interaction.guild.id
    connection = config.get_db_connection_tickets()  # Use the config function to get the connection
    
    try:
        with connection.cursor() as cursor:
            # Fetch the category ID associated with the guild
            cursor.execute("SELECT category_id FROM ticket_category WHERE guild_id = %s", (str(guild_id),))
            result = cursor.fetchone()

            category = None
            if result:
                category_id = int(result['category_id'])
                print(f"Retrieved category ID: {category_id} for guild ID: {guild_id}")
                category = interaction.guild.get_channel(category_id)
            else:
                print(f"No category found for guild ID: {guild_id}")

            # Create a new ticket channel under the specified category
            channel_name = f'ticket-{interaction.user.name}'
            if category:
                channel = await category.create_text_channel(channel_name)
            else:
                channel = await interaction.guild.create_text_channel(channel_name)

            # Insert the new ticket into the database
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO tickets (user_id, channel_id, status, type, guild_id) VALUES (%s, %s, %s, %s, %s)",
                               (str(interaction.user.id), str(channel.id), 'open', ticket_type, str(guild_id)))
                connection.commit()
                print(f"Inserted ticket for user ID {interaction.user.id} into database.")

            # Close the connection after the insert operation
            connection.close()

            # Directly set permissions for the ticket creator
            try:
                # Set permissions for the ticket creator to view and send messages in the ticket channel
                await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
                print(f"Successfully added {interaction.user.name} to the channel '{channel_name}'.")
            except Exception as e:
                print(f"Failed to add {interaction.user.name} to the channel '{channel_name}'. Error: {e}")
                await channel.send("There was an error adding you to the channel.")

            # Set up the embed and buttons
            embed = discord.Embed(
                title="Ticket Created",
                description=f'{interaction.user.mention}, your ticket for **{ticket_type}** has been created {channel.mention}.',
                color=discord.Color.purple()
            )

            view = discord.ui.View()
            close_button = discord.ui.Button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
            view.add_item(close_button)

            await channel.send(embed=embed, view=view)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the connection is closed in case of an exception
        if connection.open:
            connection.close()

    await interaction.followup.send(embed=embed, ephemeral=True)

async def handle_close_ticket(interaction: discord.Interaction):
    # Ensure that interaction is acknowledged
    await interaction.response.defer()  # This sends an acknowledgment response
    
    # Check if the ticket exists
    connection = config.get_db_connection_tickets()  # Update to use your specific connection function
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()

    if not ticket:
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.followup.send(embed=embed)  # Use followup.send for follow-up responses
        return

    # Check if the user has the required role
    allowed_roles = get_allowed_roles()
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to close this ticket.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.followup.send(embed=embed)
        return

    # Confirm closure
    confirmation_embed = discord.Embed(
        title="Close Ticket",
        description="Are you sure you want to close this ticket?",
        color=discord.Color.red()  # Using predefined red color
    )
    view = discord.ui.View()
    yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.success, custom_id="confirm_close")
    no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.danger, custom_id="cancel_close")
    view.add_item(yes_button)
    view.add_item(no_button)
    
    # Send the confirmation embed
    await interaction.followup.send(embed=confirmation_embed, view=view)

async def confirm_close_ticket(interaction: discord.Interaction):
    # Check if the ticket exists in the database
    connection = config.get_db_connection_tickets()  # Update to use your specific connection function
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    ticket = cursor.fetchone()

    if not ticket:
        cursor.close()
        connection.close()
        embed = discord.Embed(
            title="Error",
            description="No ticket found.",
            color=discord.Color.red()  # Using predefined red color
        )
        await interaction.response.send_message(embed=embed)
        return

    # Retrieve user_id from the ticket record
    user_id = int(ticket['user_id'])

    # Create and send the transcript
    transcript = io.StringIO()
    async for message in interaction.channel.history(limit=200):  # Adjust the limit as needed
        transcript.write(f"{message.author}: {message.content}\n")
    transcript.seek(0)  # Reset file pointer to the beginning

    # Attempt to fetch the user
    try:
        user = await interaction.client.fetch_user(user_id)
        try:
            # Send the transcript to the user via DM
            await user.send("Here is the transcript of your ticket:", file=discord.File(fp=transcript, filename="transcript.txt"))
            print(f"Sent ticket transcript to user ID {user_id}.")
        except discord.Forbidden:
            print(f"Failed to send DM to user ID {user_id}.")
        except Exception as e:
            print(f"An error occurred while sending the transcript: {e}")
    except discord.NotFound:
        print(f"User with ID {user_id} not found.")
    except Exception as e:
        print(f"An error occurred while fetching the user: {e}")

    # Delete the ticket entry from the database
    cursor.execute("DELETE FROM tickets WHERE channel_id = %s", (str(interaction.channel.id),))
    connection.commit()
    cursor.close()
    connection.close()

    # Delete the ticket channel
    await interaction.channel.delete()

    # Optionally, send a confirmation message in the log channel or another medium
    # await interaction.guild.system_channel.send(f"Ticket {interaction.channel.name} closed by {interaction.user.name}.")

async def cancel_close_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Cancelled",
        description="Ticket closing has been cancelled.",
        color=discord.Color.purple()  # Using predefined purple color
    )
    await interaction.response.send_message(embed=embed)

#########################
#   YOUTUBE ANNOUNCE    #
#########################

# Connect to the database and create tables if they don't exist
def setup_database():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                discord_channel_id BIGINT NOT NULL,
                youtube_channel_id VARCHAR(100) NOT NULL,
                last_announced_video_id VARCHAR(100) DEFAULT NULL
            );
            """)
        connection.commit()
    finally:
        connection.close()

setup_database()

# Fetch settings from the database
def get_channel_settings():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT discord_channel_id, youtube_channel_id, last_announced_video_id FROM channel_settings LIMIT 1;")
            result = cursor.fetchone()
    finally:
        connection.close()
    return result

# Static Configurations
announcement_channel_id = None
target_channel = None
last_check_date = datetime.utcnow().date()  # Track the last check date

@bot.event
async def on_ready():
    # Set custom status to "Watching Koenfred19"
    activity = discord.Activity(type=discord.ActivityType.watching, name="Koenfred19")
    await bot.change_presence(activity=activity)

    global announcement_channel_id, target_channel
    settings = get_channel_settings()
    if settings:
        announcement_channel_id, target_channel, last_announced_video_id = settings
        print(f'[INFO] Channel settings loaded: Announcement Channel ID = {announcement_channel_id}, Target Channel ID = {target_channel}')
        print(f'[INFO] Last announced video ID = {last_announced_video_id}')
    else:
        print('[ERROR] No channel settings found in the database.')
    
    print(f'[INFO] Logged in as {bot.user.name}')
    print('[INFO] Bot is ready and starting the check_for_new_video loop...')
    check_for_new_video.start()
    # Register slash commands
    await bot.tree.sync()
    print("[INFO] Commands synced.")  # Debug: Commands synced message

@tasks.loop(minutes=5)
async def check_for_new_video():
    global last_check_date

    print("[INFO] Checking for new video...")  # Debug: Start checking for new videos

    if not announcement_channel_id or not target_channel:
        print("[ERROR] No channel settings configured. Please set up the channel settings.")
        return

    channel = bot.get_channel(announcement_channel_id)
    if channel is None:
        print(f"[ERROR] Channel with ID {announcement_channel_id} not found or bot has no access.")
        return

    # Fetch latest video data
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={target_channel}"
    print(f"[INFO] Fetching RSS feed from URL: {feed_url}")  # Debug: Fetching RSS feed

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(feed_url) as response:
                if response.status == 200:
                    print("[INFO] RSS feed fetched successfully.")  # Debug: Feed fetched successfully

                    data = await response.text()

                    # Parse RSS feed
                    root = ET.fromstring(data)
                    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

                    if not entries:
                        print(" [ERROR] No video entries found in RSS feed.")
                        return

                    # Find the most recent video by comparing datetime
                    new_video_found = False
                    latest_video = None
                    latest_published_date = None

                    for entry in entries:
                        video_title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        video_url = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
                        channel_name = entry.find('{http://www.w3.org/2005/Atom}author').find('{http://www.w3.org/2005/Atom}name').text
                        video_id = video_url.split('v=')[-1]
                        published_date_str = entry.find('{http://www.w3.org/2005/Atom}published').text
                        published_date = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%S%z')

                        # Update the latest video if this one is newer
                        if latest_published_date is None or published_date > latest_published_date:
                            latest_published_date = published_date
                            latest_video = {
                                'title': video_title,
                                'url': video_url,
                                'channel_name': channel_name,
                                'video_id': video_id,
                                'published_date': published_date
                            }

                    if latest_video:
                        print(f"[INFO] Latest video found: {latest_video['title']} published on {latest_video['published_date']}")  # Debug: Print video details

                        # Fetch the last announced video ID from the database
                        connection = pymysql.connect(**db_config)
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute("SELECT last_announced_video_id FROM channel_settings LIMIT 1;")
                                last_announced_video_id = cursor.fetchone()[0]
                        finally:
                            connection.close()

                        if latest_video['video_id'] != last_announced_video_id:
                            # Build and send embed
                            embed = discord.Embed(
                                title=latest_video['title'],
                                url=latest_video['url'],
                                description=f"**Kanaal:** {latest_video['channel_name']}",
                                color=discord.Colour.blurple()
                            )
                            embed.set_image(url=f"https://i4.ytimg.com/vi/{latest_video['video_id']}/maxresdefault.jpg")
                            embed.add_field(name='Link:', value=latest_video['url'], inline=False)

                            # Message with @everyone mention
                            message_content = f"@everyone **{latest_video['channel_name']}** heeft een nieuwe video geplaatst of is live gegaan!"

                            print(f"[INFO] Sending message for new video: {latest_video['title']}")  # Debug: Sending message

                            try:
                                await channel.send(content=message_content, embed=embed)

                                # Update last announced video ID in the database
                                connection = pymysql.connect(**db_config)
                                try:
                                    with connection.cursor() as cursor:
                                        cursor.execute("""
                                        UPDATE channel_settings
                                        SET last_announced_video_id = %s
                                        WHERE discord_channel_id = %s AND youtube_channel_id = %s;
                                        """, (latest_video['video_id'], announcement_channel_id, target_channel))
                                    connection.commit()
                                finally:
                                    connection.close()
                                    
                                new_video_found = True
                            except discord.Forbidden:
                                print("[ERROR] Bot does not have permission to send messages in this channel.")
                            except discord.HTTPException as e:
                                print(f"[ERROR] HTTP Exception: {e}")

                    if not new_video_found:
                        print("[INFO] No new video of the day found or already announced.")

                else:
                    print(f"[ERROR] Failed to fetch video data. Status code: {response.status}")
        except Exception as e:
            print(f"[ERROR] Error occurred while fetching RSS feed: {e}")

    # Update last check date
    last_check_date = datetime.utcnow().date()

@bot.tree.command(name="nieuwstevideo", description="Get the latest video from the YouTube RSS feed")
async def nieuwstevideo(interaction: discord.Interaction):
    print("[INFO] Fetching latest video on slash command...")  # Debug: Slash command triggered

    if not target_channel:
        await interaction.response.send_message("No YouTube channel ID configured. Please set up the channel settings.")
        return

    # Fetch latest video data
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={target_channel}"
    print(f"[INFO] Fetching RSS feed from URL: {feed_url}")  # Debug: Fetching RSS feed

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(feed_url) as response:
                if response.status == 200:
                    print("[INFO] RSS feed fetched successfully.")  # Debug: Feed fetched successfully

                    data = await response.text()

                    # Parse RSS feed
                    root = ET.fromstring(data)
                    entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

                    if not entries:
                        print("[ERROR] No video entries found in RSS feed.")
                        await interaction.response.send_message("No video entries found.")
                        return

                    # Find the most recent video by comparing datetime
                    latest_video = None
                    latest_published_date = None

                    for entry in entries:
                        video_title = entry.find('{http://www.w3.org/2005/Atom}title').text
                        video_url = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
                        channel_name = entry.find('{http://www.w3.org/2005/Atom}author').find('{http://www.w3.org/2005/Atom}name').text
                        video_id = video_url.split('v=')[-1]
                        published_date_str = entry.find('{http://www.w3.org/2005/Atom}published').text
                        published_date = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%S%z')

                        # Update the latest video if this one is newer
                        if latest_published_date is None or published_date > latest_published_date:
                            latest_published_date = published_date
                            latest_video = {
                                'title': video_title,
                                'url': video_url,
                                'channel_name': channel_name,
                                'video_id': video_id,
                                'published_date': published_date
                            }

                    if latest_video:
                        print(f"[INFO] Latest video found: {latest_video['title']} published on {latest_video['published_date']}")  # Debug: Print video details

                        # Build and send embed
                        embed = discord.Embed(
                            title=latest_video['title'],
                            url=latest_video['url'],
                            description=f"**Kanaal:** {latest_video['channel_name']}",
                            color=discord.Colour.blurple()
                        )
                        embed.set_image(url=f"https://i4.ytimg.com/vi/{latest_video['video_id']}/maxresdefault.jpg")
                        embed.add_field(name='Link:', value=latest_video['url'], inline=False)

                        # Send message
                        await interaction.response.send_message(content=f"**{latest_video['channel_name']}** heeft een nieuwe video geplaatst of is live gegaan!", embed=embed)
                    else:
                        await interaction.response.send_message("No new video of the day found.")

                else:
                    print(f"[ERROR] Failed to fetch video data. Status code: {response.status}")
                    await interaction.response.send_message("Failed to fetch video data.")
        except Exception as e:
            print(f"[ERROR] Error occurred while fetching RSS feed: {e}")
            await interaction.response.send_message("An error occurred while fetching video data.")

    # Update last check date
    last_check_date = datetime.utcnow().date()

@bot.tree.command(name="youtubesetup", description="Set up the YouTube channel and Discord channel for announcements")
@commands.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, youtube_channel_id: str, discord_channel_id: str):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO channel_settings (discord_channel_id, youtube_channel_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE discord_channel_id = VALUES(discord_channel_id), youtube_channel_id = VALUES(youtube_channel_id);
            """, (discord_channel_id, youtube_channel_id))
        connection.commit()
        global announcement_channel_id, target_channel
        announcement_channel_id = discord_channel_id
        target_channel = youtube_channel_id
        await interaction.response.send_message(f"Channel settings updated: Announcement Channel ID = {discord_channel_id}, Target Channel ID = {youtube_channel_id}")
    finally:
        connection.close()

@bot.tree.command(name="reset", description="Clear all channel settings from the database")
@commands.has_permissions(administrator=True)
async def clearsettings(interaction: discord.Interaction):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM channel_settings;")
        connection.commit()
        await interaction.response.send_message("All channel settings have been cleared from the database.")
    except Exception as e:
        print(f"[ERROR] Error occurred while clearing settings: {e}")
        await interaction.response.send_message("An error occurred while clearing settings.")
    finally:
        connection.close()

# Run the bot with your bot token
bot.run(config.BOT_TOKEN)
