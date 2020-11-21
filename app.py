# -*- coding: utf-8 -*-

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from os import listdir
from functools import wraps
import sys
import csv
import logging

logging.basicConfig(
    filename="app.log",
    format="%(asctime)s [%(levelname)s]- %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logging.info("Iniciou a aplicação")

TOKEN_BOT, CHAT_PERMITIDO = (
    (sys.argv[1], int(sys.argv[2]))
    if len(sys.argv) == 3
    else (input("Token: "), input("ChatID: "))
)
updater = Updater(token=TOKEN_BOT, use_context=True)
dispatcher = updater.dispatcher


def permissao(func):
    @wraps(func)
    def wrapper(update, context):
        nome = update.effective_user.full_name
        nick = update.effective_user.username
        id_user = update.effective_user.id

        if update.effective_chat.id == CHAT_PERMITIDO:
            logging.info(f"{nome} : {nick} : {id_user} - {func.__name__}")
            return func(update, context)
        else:
            texto = "Você não tem permissão!"
            context.bot.send_message(chat_id=update.effective_chat.id, text=texto)
            logging.critical(
                f"{nome} : {nick} : {id_user} - {func.__name__} Tentou acessar"
            )
            print(
                f"\n######################\nNome: {nome}\nNick: {nick}\nId: {id_user}\n######################\n"
            )
            return None

    return wrapper


# Bot faz o upload no chat de arquivo encontrado no diretório ./arquivos
@permissao
def arquivo(update, context):
    try:
        arquivos = context.args
        for arquivo in arquivos:
            context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=open(f"arquivos/{arquivo}", "rb"),
            )

    except FileNotFoundError:
        texto = "<b>Arquivo não encontrado.</b>\n---\n"
        arquivos = listdir("arquivos/")
        texto = texto + ", ".join(arquivos)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=texto, parse_mode=ParseMode.HTML
        )


# Pesquisa em um arquivo tsv e retorna a primeira e segunda coluna
@permissao
def pesquisa(update, context):
    termos = context.args
    texto = str()

    for termo in termos:
        try:
            arquivo = csv.reader(
                open("arquivos/planilha.tsv", "r", encoding="utf-8"), delimiter="\t"
            )
            for linha in arquivo:
                for coluna in linha:
                    if termo in coluna:
                        encontrado = linha
                        texto = texto + f"{encontrado[0]} - {encontrado[1]}\n"
        except IndentationError:
            pass

    if texto:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=texto,
            parse_mode=ParseMode.HTML,
        )

    else:
        texto = f"<b>Nada encontrado!</b>"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=texto,
            parse_mode=ParseMode.HTML,
        )


# Retorna os comandos disponíveis
@permissao
def comandos(update, context):
    texto = (
        "/arquivo <b>nome_do_arquivo.extensao</b> - Download arquivo<br>/pesquisa <b>termo</b> - Buscar em arquivo"
        ""
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=texto, parse_mode=ParseMode.HTML
    )


# * Precisa ser o último a ser definido, caso contrário será ativado antes de outro comando
# Caso seja requisitado um comando desconhecido, exibir mensagem
@permissao
def desconhecido(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="<b>Comando inválido</b>\n/comandos -> lista de comandos",
        parse_mode=ParseMode.HTML,
    )


dispatcher.add_handler(CommandHandler("arquivo", arquivo))
dispatcher.add_handler(CommandHandler("pesquisa", pesquisa))
dispatcher.add_handler(CommandHandler("comandos", comandos))
dispatcher.add_handler(MessageHandler(Filters.command, desconhecido))


updater.start_polling()
