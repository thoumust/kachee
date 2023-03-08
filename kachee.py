import sqlite3
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace with your own token
bot = telegram.Bot(token='6280857926:AAF9I7zUDbaEE-gv0PuuT31JrALqffQ0MqE')

# Connect to the database
conn = sqlite3.connect('items.db')
c = conn.cursor()

# Create the items table if it does not exist
c.execute('''CREATE TABLE IF NOT EXISTS items
             (name text, price real)''')

# Insert some sample items
c.execute("INSERT INTO items VALUES ('spotify 1m', 10.0)")
c.execute("INSERT INTO items VALUES ('spotify 2m', 20.0)")
c.execute("INSERT INTO items VALUES ('spotify 3m', 30.0)")

# Handler for /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to my store! Here are the items we sell:")

    # Retrieve the items from the database
    c.execute("SELECT * FROM items")
    items = c.fetchall()

    # Send the items as a list
    item_list = '\n'.join([f'{item[0]} - PHP {item[1]}' for item in items])
    context.bot.send_message(chat_id=update.effective_chat.id, text=item_list)

# Handler for text messages
def order(update, context):
    item_name = update.message.text

    # Check if the item is in the database
    c.execute("SELECT * FROM items WHERE name=?", (item_name,))
    item = c.fetchone()

    if item is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, that item is not available.")
    else:
        # Save the order to user data
        context.user_data['order'] = item_name
        context.user_data['price'] = item[1]

        # Send the GCash details
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"To order {item_name} (PHP {item[1]}), please pay through GCash to 09550388450 and send a screenshot of the payment confirmation to me.")

# Handler for payment confirmation
def payment(update, context):
    if update.message.photo:
        # Check if the payment is correct
        amount_paid = 0.0
        for photo in update.message.photo:
            file_id = photo.file_id
            file = context.bot.get_file(file_id)
            file.download()
            amount_paid += 1.0 # Assume that each photo represents 1 PHP

        if amount_paid >= context.user_data['price']:
            # Send the confirmation message and the ordered items
            context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for your payment! Your order will be shipped soon.")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Here are your ordered items: {} - PHP {}".format(context.user_data['order'], context.user_data['price']))

# Create the handlers and attach them to the dispatcher
updater = Updater(token='6280857926:AAF9I7zUDbaEE-gv0PuuT31JrALqffQ0MqE', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.regex(r'^\d+$'), order))
dispatcher.add_handler(MessageHandler(Filters.photo, payment))

# Start the bot
updater.start_polling()
updater.idle()

# Close the database connection
conn.close()
