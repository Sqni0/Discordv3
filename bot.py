import disnake
from disnake.ui import Button, View
import disnake as discord
from disnake.ext import commands
import random
import string
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw, ImageFont
import datetime
#import mysql
#import mysql.connector

# Für den token
load_dotenv()


YELLOW = '\033[93m'
GREEN = '\033[92m'
ENDC = '\033[0m'


client = commands.Bot(command_prefix=None, intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f"{GREEN}Erfolg: Der bot ist Online!{ENDC}")
    log_to_file_and_discord("Bot ist online!")
    await client.change_presence(activity=discord.Activity(name="ITAU", type=discord.ActivityType.playing), status=discord.Status.do_not_disturb)


def log_to_file_and_discord(action):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # falls logs nicht gefunden -> erstelle logs
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    # log datei pfad
    log_file_path = os.path.join(log_directory, "bot_logs.txt")
    
    # log in die datei schreiben ("a" fürs text anhängen zur datei)
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{timestamp} - {action}\n")
        print(f"{GREEN}Log geschrieben: {action}{ENDC}")  # Ausgabe in der Konsole
    
    
    log_channel_id = 1339174861821706240  # Kanal-ID anpassen
    channel = client.get_channel(log_channel_id)

    # erstelle embed für log
    embed = discord.Embed(title="Bot Log", description=f"**{action}**", color=discord.Color.blue())
    embed.set_footer(text=f"Logged at {timestamp}")
    
    # sende das smbed an den kanal
    if channel:
        client.loop.create_task(channel.send(embed=embed)) #"client.loop.create_task" hält code nicht an läuft im hintergrund weiter
    else:
        print("Log Kanal nicht gefunden!")


@client.slash_command(name="info", description="Das ist ein Test")
async def info(interaction):
    log_to_file_and_discord(f"Info Befehl ausgeführt von {interaction.user.name} ({interaction.user.id})")
    await interaction.response.send_message("Das ist ein Test", ephemeral=True)

@client.slash_command(name="info2", description="Das ist ein Test")
async def info2(interaction):
    log_to_file_and_discord(f"Info2 Befehl ausgeführt von {interaction.user.name} ({interaction.user.id})")
    embed = discord.Embed(title="test2", description="test")
    await interaction.response.send_message("Ich bin der ITAU test Bot", embed=embed, ephemeral=True)

@client.event
async def on_member_join(member):
    guild = client.get_guild(786953229492813876)
    role = guild.get_role(788065582200651816)
    await member.add_roles(role)

    # pfade für bild und font
    image_path = r"H:\Software_Meilenstein_1\Willkommen.png"
    font_path = r"H:\Software_Meilenstein_1\Font.otf"
    new_image_path = r"H:\Software_Meilenstein_1\WillkommenNeu.png"

   
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, 60)
    color_username = (0, 255, 0) # grün
    color_count = (0, 0, 0) # schwarz

    
    username =  f"Hallo,  {member.display_name}"
    member_count = f"TOTAL MEMBERS: #{len(guild.members)}"

   
    img_width, img_height = image.size
    text_width, text_height = draw.textbbox((0, 0), username, font=font)[2:]
    count_width, count_height = draw.textbbox((0, 0), member_count, font=font)[2:]

    # dadurch immer zentriert
    username_x = (img_width - text_width) // 2
    username_y = img_height // 2 - 100
    count_x = (img_width - count_width) // 2
    count_y = img_height // 2 + 50

   
    draw.text((username_x, username_y), username, fill=color_username, font=font)
    draw.text((count_x, count_y), member_count, fill=color_count, font=font)

    # neues bild speichern
    image.save(new_image_path)

    # neues bild in channel posten
    embed = discord.Embed(title="Willkommen!", description=f"Hallo, {member.mention}!", color=discord.Color.brand_red())
    discordfile = discord.File(new_image_path, filename="welcome.png")
    embed.set_image(url="attachment://welcome.png")

    # willkommens nachricht
    channel = guild.get_channel(1350943682785710150)
    await channel.send(embed=embed, file=discordfile)

    log_to_file_and_discord(f"Neues Mitglied {member.name} ({member.id}) hat den Server betreten.")


SAVED_ROLE_ID = 1351658575604486176  #support rolle 

def random_ticket_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Ticket Erstellen", style=disnake.ButtonStyle.green)
    async def create_ticket(self, button: Button, interaction: disnake.Interaction):
        # Kanal erstellen
        ticket_name = f"ticket-{random_ticket_name()}"
        guild = interaction.guild
        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),  # Alle Mitglieder können den Kanal nicht sehen
            interaction.user: disnake.PermissionOverwrite(read_messages=True),    # Der User hat Zugriff
        }

        # Erstelle den Kanal
        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites)

        # Willkommensnachricht
        embed_welcome = disnake.Embed(
            title="Willkommen im Ticket",
            description=f"Hallo {interaction.user.mention}, dies ist dein Ticket. Das Support-Team wird sich in Kürze bei dir melden.",
            color=disnake.Color.blue()
        )
        embed_welcome.set_footer(text="Support-System")
        log_to_file_and_discord(f"Ticket - Willkommn {interaction.user.name} ({interaction.user.id})")
        await ticket_channel.send(embed=embed_welcome)

        # Button zum Schließen des Tickets
        close_button = Button(label="Ticket Schließen", style=disnake.ButtonStyle.red)

        # Funktion, um das Ticket zu schließen
        async def close_ticket(interaction: disnake.Interaction):
            embed_close = disnake.Embed(
                title="Ticket geschlossen",
                description="Das Ticket wurde geschlossen.",
                color=disnake.Color.green()
            )
            embed_close.set_footer(text="Support-System")

            await interaction.response.send_message(embed=embed_close, ephemeral=True)
            log_to_file_and_discord(f"Ticket - Geloescht {interaction.user.name} ({interaction.user.id})")
            await ticket_channel.delete()

        # Button zum Speichern des Tickets
        save_button = Button(label="Ticket Speichern", style=disnake.ButtonStyle.blurple)

        # Funktion, um das Ticket zu speichern
        async def save_ticket(interaction: disnake.Interaction):
            # Berechtigungen für den Kanal ändern, sodass nur die bestimmte Rolle den Kanal sehen kann
            saved_role = guild.get_role(SAVED_ROLE_ID)
            if saved_role:
                # Kanal überschreiben und nur die Rolle zulassen
                await ticket_channel.set_permissions(saved_role, read_messages=True)
                await ticket_channel.set_permissions(interaction.user, read_messages=False)

                embed_save = disnake.Embed(
                    title="Ticket gespeichert",
                    description="Das Ticket wurde gespeichert und nur das Support-Team kann es jetzt sehen.",
                    color=disnake.Color.green()
                )
                embed_save.set_footer(text="Support-System")
                
                log_to_file_and_discord(f"Ticket - Gespeichert {interaction.user.name} ({interaction.user.id})")
                await interaction.response.send_message(embed=embed_save, ephemeral=True)
            else:
                embed_error = disnake.Embed(
                    title="Fehler",
                    description="Die spezifizierte Rolle wurde nicht gefunden. Bitte überprüfe die Roll-ID.",
                    color=disnake.Color.red()
                )
                log_to_file_and_discord(f"Ticket - Rollen Fehler {interaction.user.name} ({interaction.user.id})")
                await interaction.response.send_message(embed=embed_error, ephemeral=True)

        # Buttons zu View hinzufügen
        close_button.callback = close_ticket
        save_button.callback = save_ticket
        view = View()
        view.add_item(close_button)
        view.add_item(save_button)

        # Nachricht mit den Buttons
        embed_close_ticket = disnake.Embed(
            title="Ticket Optionen",
            description="Klicke auf den Button, um das Ticket zu schließen oder zu speichern.",
            color=disnake.Color.red()
        ) 
        embed_close_ticket.set_footer(text="Support-System")

        await ticket_channel.send(embed=embed_close_ticket, view=view)

        # Nachricht, dass das Ticket erstellt wurde
        embed_ticket_created = disnake.Embed(
            title="Ticket Erstellungsbestätigung",
            description=f"Dein Ticket wurde unter {ticket_channel.mention} erstellt. Ein Support-Team-Mitglied wird sich bald bei dir melden.",
            color=disnake.Color.green()
        )
        embed_ticket_created.set_footer(text="Support-System")

        await interaction.response.send_message(embed=embed_ticket_created, ephemeral=True)

# command für ticket erstellung 
@client.slash_command(name="ticket", description="Erstelle ein Ticket, um mit dem Support-Team zu sprechen.")
async def ticket(ctx: disnake.CommandInteraction):
    
    embed = disnake.Embed(
        title="Ticket-System",
        description="Klicke auf den Button, um ein Ticket zu erstellen.",
        color=disnake.Color.blue()
    )
    embed.set_footer(text="Support System")

    # Button zum Erstellen eines Tickets
    view = TicketButton()

    await ctx.send(embed=embed, view=view, ephemeral=True)

client.run('')