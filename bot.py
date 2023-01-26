import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import asyncio
import json

#Para mayor seguridad, cargamos el fichero .env y asignamos el valor del token a una variable.
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

# Iniciar el bot con el prefijo de comando '$'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

# Cargar user_points desde archivo
try:
    with open("user_points.json", "r") as f:
        user_points = json.load(f)
except:
    user_points = {}

# Iniciar evento
event_active = False

# Crear una lista ordenada interna para almacenar las películas
try:
    with open("peliculas_cola.json", "r") as f:
        peliculas_cola = json.load(f)
except:
    peliculas_cola = []

# ID del canal de voz específico
channel_id = 1050768293901893764

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_voice_state_update(member, before, after):
    if event_active:
        # Comprueba si el miembro se une a un canal de voz específico
        if after.channel == bot.get_channel(channel_id) and before.channel != after.channel:
            # Asignar puntos al usuario si no está en el diccionario
            user_id = str(member.id)
            if user_id not in user_points:
                user_points[user_id] = 0
            while event_active:
                await asyncio.sleep(60)
                user_points[user_id] += 1
                print(f'{member} has {user_points[user_id]} points.')
                with open("user_points.json", "w") as f:
                    json.dump(user_points, f)

@bot.command()
async def start_event(ctx):
    if ctx.author.guild_permissions.administrator:
        global event_active
        event_active = True
        await ctx.send('Evento iniciado.')
    else:
        await ctx.send('Solo un administrador puede iniciar el evento.')

@bot.command()
async def stop_event(ctx):
    if ctx.author.guild_permissions.administrator:
        global event_active
        event_active = False
        await ctx.send('Evento detenido.')
    else:
        await ctx.send('Solo un administrador puede detener el evento.')

@bot.command()
async def add_movie(ctx, *movie_name: str):
    if not movie_name:
        await ctx.send("Necesitas propocionar el nombre de alguna pelicula.")
        return
    member = ctx.author
    user_id = str(member.id)
    cost = 300
    if user_id in user_points and user_points[user_id] >= cost:
        user_points[user_id] -= cost
        movie_name = " ".join(movie_name)
        peliculas_cola.append(movie_name)
        peliculas_cola.sort()
        with open("user_points.json", "w") as f:
            json.dump(user_points, f)
        with open("peliculas_cola.json", "w") as f:
            json.dump(peliculas_cola, f)
        await ctx.send(f'{movie_name} ha sido agregada a la cola de películas.')
        await ctx.send(f'{member} ha gastado {cost} puntos y tiene {user_points[user_id]} puntos restantes.')
    else:
        await ctx.send(f'{member} no tiene suficientes puntos para agregar una pelicula. Necesitas {cost} puntos.')

@bot.command()
async def movie_queue(ctx):
    try:
        with open("peliculas_cola.json", "r") as f:
            peliculas_cola = json.load(f)
    except:
        peliculas_cola = []
    if len(peliculas_cola) > 0:
        peliculas_cola_string = "\n".join(peliculas_cola)
        await ctx.send(f'La cola de películas es: \n{peliculas_cola_string}')
    else:
        await ctx.send(f'La cola de películas está vacía.')

@bot.command()
async def points(ctx,user:discord.Member=None):
    if user is None:
        user = ctx.author
    user_id = str(user.id)
    if user_id in user_points:
        await ctx.send(f'{user} tiene {user_points[user_id]} puntos.')
    else:
        await ctx.send(f'{user} no tiene puntos registrados.')


# Iniciar el bot con la token de Discord
bot.run(TOKEN)