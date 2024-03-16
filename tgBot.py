# This Python file uses the following encoding: utf-8
import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
TOKEN = "7048836769:AAEv_2XDOETUksLXAQWzOCnmDjp9YsEexw8"
rpc_user = 'kzcashrpc'
rpc_password = 'xjEAlFEbABPgSuZq54hFHfoe'

rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@127.0.0.1:8276')


bot_token = TOKEN
bot = telebot.TeleBot(bot_token)

def addressBalance(args):
    inputs = rpc_connection.listunspent(0, 9999, args)
    balance = 0
    if len(inputs) == 0:
        balance += 0
    elif len(inputs) == 1:
        balance += inputs[0].get("amount")
    else:
        for i in inputs:
            balance += i.get("amount")
    return balance

@bot.message_handler(commands=['getnewaddress'])
def get_new_address(message):
    new_address = rpc_connection.getnewaddress()
    bot.reply_to(message, f"Новый адрес: {new_address}")

@bot.message_handler(commands=['getbalance'])
def get_balance(message):
    balance = rpc_connection.getbalance()
    bot.reply_to(message, f"Общий баланс кошелька: {balance}")


@bot.message_handler(commands=['send'])
def send_coins(message):
    global temp
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, "Шаблон: /send <адрес отправителя> <адрес получателя> <сумма>")
        return
    sender_address, receiver_address, amount = args
 # vhody
    try:
        inputs = rpc_connection.listunspent(0, 9999, [sender_address])
    except JSONRPCException:
        bot.reply_to(message, f"Неправильный адрес кошелька отправителя")
        return

    for i in inputs:
        temp = i
        if float(float(temp.get("amount"))) > (float(amount)+0.001):
            break
    if float(float(temp.get("amount"))) < (float(amount)+0.001):
        bot.reply_to(message, "Недостаточно средств")
        return
    fee = float(temp.get("amount")) - float(amount) - 0.001
    inputForTransaction = {"txid":temp.get("txid"), "vout": temp.get("vout")}
    try:
        createTransaction = rpc_connection.createrawtransaction([inputForTransaction], {receiver_address:amount, sender_address:fee})
    except JSONRPCException:
        bot.reply_to(message, f"Неправильный адрес кошелька получателя")
        return
    signTransaction = rpc_connection.signrawtransaction(createTransaction)
    receivedHex = signTransaction.get("hex")
    txid = rpc_connection.sendrawtransaction(receivedHex)
    bot.reply_to(message, f"Монеты отправлены получателю! ID транзакции: {txid}")

@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Шаблон: /getaddressbalance <адрес кошелька>")
        return
    try:
        balance = addressBalance(args)
    except JSONRPCException:
        bot.reply_to(message, f"Неправильный адрес кошелька ")
        return
    bot.reply_to(message, f"Баланс адреса: {balance} KZC")


@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.infinity_polling()
