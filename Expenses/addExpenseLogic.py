from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import json

class ExpenseState:
    SELECT_CATEGORY = 0
    ENTER_EXPENDITURE = 1

async def addExpense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if str(user_id) not in users_data:
        await update.message.reply_text('You have not been registered in our database yet. \nPlease register by pressing /register')
        return ConversationHandler.END

    # Retrieve the user's categories
    user_categories = users_data[str(user_id)]["expenditureCategory"].keys()

    # Create the inline keyboard based on the user's categories
    inline_keyboard = [[InlineKeyboardButton(category, callback_data=category)] for category in user_categories]
    markup = InlineKeyboardMarkup(inline_keyboard)

    await update.message.reply_text('Please select an expenditure category:', reply_markup=markup)
    return ExpenseState.SELECT_CATEGORY


async def handle_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query: CallbackQuery = update.callback_query
    await query.answer() 
    chosen_category = query.data 

    context.user_data['selected_category'] = chosen_category

    # You can edit the original message if you want
    await query.edit_message_text(f'You selected {chosen_category}. Now, please enter the name and cost of the expenditure in this format: Durian $10')

    return ExpenseState.ENTER_EXPENDITURE 


async def enter_expenditure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chosen_category = context.user_data['selected_category']

    user_input = update.message.text
    print(user_input)

    if ' ' not in user_input:
        await update.message.reply_text('Invalid input format. Please enter the name and cost of the expenditure in this format: Durian $10')
        return ExpenseState.ENTER_EXPENDITURE  

    arr = user_input.split(' ')
    item_cost = arr[-1]
    item_name = " ".join(arr[:-1])

    # Check if item_cost starts with '$' and is a valid float
    if not item_cost.startswith('$') or not item_cost[1:].replace('.', '', 1).isdigit():
        await update.message.reply_text('Invalid cost format. Please enter the cost with a dollar sign, like $10.')
        return ExpenseState.ENTER_EXPENDITURE  

    item_cost = float(item_cost[1:])
    print(chosen_category, item_name, item_cost)

    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    users_data[str(user_id)]["expenditureCategory"][chosen_category].append([item_name, item_cost])
    users_data[str(user_id)]["currentDailyExpenditure"] += item_cost
    users_data[str(user_id)]["currentMonthlyExpenditure"] += item_cost
    currentExpenditure = users_data[str(user_id)]["currentDailyExpenditure"]
    currentMonthExpenses = users_data[str(user_id)]["currentMonthlyExpenditure"]

    with open('users_expenses.json', 'w') as file:
        json.dump(users_data, file, indent=4)

    txt = f"Successfully updated {item_name} under the category of {chosen_category}! \nYour daily expenditure stands at {currentExpenditure}\nYour monthly expenditure stands at {currentMonthExpenses}\n\nClick on /viewDailyExpenses to see the breakdown of today's expenditure!"

    if users_data[str(user_id)]["dailyLimit"] != None and currentExpenditure > users_data[str(user_id)]["dailyLimit"]:
        txt += '\n\n<b>WARNING: YOU HAVE EXCEEDED YOUR DAILY LIMIT!</b>'

    elif users_data[str(user_id)]["dailyLimit"] != None and currentExpenditure == users_data[str(user_id)]["dailyLimit"]:
        txt += '\n\n<b>NOTICE: YOU HAVE JUST HIT YOUR DAILY LIMIT!</b>'

    await update.message.reply_text(txt, parse_mode="HTML")
    return ConversationHandler.END

        
conv_handler_addExpense = ConversationHandler(
    entry_points=[CommandHandler('addExpense', addExpense)],
    states={
        ExpenseState.SELECT_CATEGORY: [CallbackQueryHandler(handle_category_callback)],
        ExpenseState.ENTER_EXPENDITURE: [MessageHandler(filters.TEXT, enter_expenditure)],
    },
    fallbacks=[CommandHandler("addExpense", addExpense)]
) 