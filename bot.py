## Libraries
import discord
import os
import asyncio
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

## Load Environment Variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK')

## Bot Setup
intents = discord.Intents.all()
client = commands.Bot(command_prefix='mg!', intents=intents)
client.remove_command('help')

status_messages = [
    "🍉 | Im having fun :)",
    "🌐 | Active in {guild_count} servers!",
    "⚙️ | Type /help for commands!",
]

@client.event
async def on_ready():
    try:
        synced_commands = await client.tree.sync()
        print(f"+ [✅SYNCED✅] {len(synced_commands)} commands successfully.")
    except Exception as e:
        print(f"- [❌SYNC FAILED❌] {e}")

    print(f"+ [CONNECTED] {client.user.name} is online and ready!")
    print(f"Currently in {len(client.guilds)} guilds.")

    if not update_status_loop.is_running():
        update_status_loop.start()


@tasks.loop(seconds=10)
async def update_status_loop():
    try:
        guild_count = len(client.guilds)
        latency = round(client.latency * 1000)
        latency_message = "📡 | Ping: 999+ms" if latency > 999 else f"📡 | Ping: {latency}ms"
        all_statuses = status_messages + [latency_message]
        current = all_statuses[update_status_loop.current_loop % len(all_statuses)].format(guild_count=guild_count)
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.watching, name=current)
        )
    except Exception as e:
        await logger.send(build_embed("❌ Status Update Failed", f"`{e}`", "error"))

def send_webhook_log(embed: discord.Embed):
    """Sends an embed message to the specified webhook."""
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "embeds": [embed.to_dict()]  # Convert the embed to a dictionary format that Discord's API expects
    }

    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)

    if response.status_code != 204:
        print(f"Failed to send webhook. Status code: {response.status_code}, Response: {response.text}")
    else:
        pass

async def load_cogs():
    """Loads all cogs and sends a summary embed after all have been processed."""
    loaded = []
    failed = []

    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            name = filename[:-3]
            try:
                await client.load_extension(f'cogs.{name}')
                loaded.append(filename)
                
            except Exception as e:
                failed.append((filename, str(e)))
                

    # Build embed
    embed = discord.Embed(
        title="📦 Cog Load Summary",
        color=discord.Color.green() if not failed else discord.Color.orange()
    )
    if loaded:
        embed.add_field(
            name="✅ Successfully Loaded",
            value="\n".join(f"`{file}`" for file in loaded),
            inline=False
        )
    if failed:
        embed.color = discord.Color.red()
        embed.add_field(
            name="❌ Failed to Load",
            value="\n".join(f"`{file}` - `{error}`" for file, error in failed),
            inline=False
        )

    embed.set_footer(text="Cog Loader")
    await logger.send(embed)

async def main():
    try:
        await load_cogs()
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        await logger.send(build_embed(
            "🚨 Critical Error Loading Cogs",
            f"An unexpected error occurred while loading cogs:\n`{e}`",
            "error"
        ))

    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await logger.send(build_embed("🛑 CRITICAL ERROR", "KeyboardInterrupt: Bot manually stopped.", "warn"))
    except Exception as e:
        print(f"[FAILED TO START] {e}")
        await logger.send(build_embed("❌ Failed to Start Bot", f"`{e}`", "error"))

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
