from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from Expenses.addExpenseLogic import conv_handler_addExpense
from Expenses.viewDailyExpenseLogic import viewDailyExpenses
from Expenses.viewMonthlyExpenseLogic import viewMonthlyExpenses
from Expenses.removeExpenseLogic import conv_handler_removeExpense
from Limits.setLimitLogic import conv_handler_set_limit
from Limits.resetLimitLogic import conv_handler_reset_limit
from Reset.resetDailyExpenses import check_and_transition_to_new_day
from Reset.resetMonthlyExpenses import check_and_transition_to_new_month
from Expenses.editExpenseLogic import conv_handler_editExpense
from register import conv_handler_register
from addCategoryLogic import conv_handler_addCategory
from config import BOT_TOKEN
import json

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user.username)
    user_id = update.effective_user.id
    user_exists = False

    # Check if the user exists in the database
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)
        if str(user_id) in users_data:
            user_exists = True

    register_command = ""
    if not user_exists:
        register_command = "<b>🔟 /register - Register your account in order to start tracking your finances.</b>\n\n"

    intro_message = (
        f"Hello <b>{update.effective_user.username}</b>! I'm your personal finance assistant, here to guide you towards mindful spending. 🧠💵\n\n"
        "Here's what I can do for you:\n"
        "1️⃣ /addExpense - Record an expense in any of the available categories. Categories are not limited and can be customized to fit your personal tracking needs.\n"
        "2️⃣ /removeExpense - Remove a previously added expense.\n"
        "3️⃣ /editExpense - Edit a previously added expense.\n\n"  
        "4️⃣ /viewDailyExpenses - View a detailed summary of your current daily expenses.\n"
        "5️⃣ /viewMonthlyExpenses - View a detailed summary of your current monthly expenses.\n\n"
        "6️⃣ /setLimits - Define your daily, weekly, or monthly spending limits.\n"
        "7️⃣ /resetLimits - Reset your spending limits.\n\n"
        "8️⃣ /addCategory - Add a new spending category for your expenses.\n\n"  
        "9️⃣ /refresh - Update your expenses for a new day, moving current day's expenses to historical records.\n\n"
        + register_command + 
        "Feel free to ask me anything about your expenses, and I'll do my best to assist you!"
    )

    await update.message.reply_text(intro_message, parse_mode='HTML')


async def refresh_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    # Get user data
    if user_id in users_data:
        user_data = users_data[user_id]

        # Check and transition to a new day
        check_and_transition_to_new_day(user_data)

        # Check and transition to a new month
        check_and_transition_to_new_month(user_data)

        with open('users_expenses.json', 'w') as file:
            json.dump(users_data, file, indent=4)

        await update.message.reply_text('Expenses refreshed. Historical expenses have been updated.')

    else:
        await update.message.reply_text('You have not been registered in our database yet. \nPlease register by pressing /register')

     
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    
    #creating the handlers
    start_handler = CommandHandler('start', start)
    viewDailyExpenses_handler = CommandHandler('viewDailyExpenses', viewDailyExpenses)
    viewMonthlyExpenses_handler = CommandHandler('viewMonthlyExpenses', viewMonthlyExpenses)
    refreshExpenses_handler = CommandHandler('refresh', refresh_expenses)

    #adding the handlers
    application.add_handler(start_handler)
    application.add_handler(conv_handler_addExpense)
    application.add_handler(viewDailyExpenses_handler)
    application.add_handler(conv_handler_set_limit)
    application.add_handler(conv_handler_reset_limit)
    application.add_handler(conv_handler_removeExpense)
    application.add_handler(refreshExpenses_handler)
    application.add_handler(viewMonthlyExpenses_handler)
    application.add_handler(conv_handler_register)
    application.add_handler(conv_handler_editExpense)
    application.add_handler(conv_handler_addCategory)
#
    
    application.run_polling(poll_interval=1) #how often to check for new update -- in this case is every 5 sec

if __name__ == '__main__':
    main()


