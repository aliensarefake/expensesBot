from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import json

class RemoveExpenseState:
    SELECT_CATEGORY = 0
    SELECT_EXPENSE = 1

# async def removeExpense(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     with open('users_expenses.json', 'r') as file:
#         users_data = json.load(file)

#     if str(user_id) not in users_data:
#         await update.message.reply_text('You have not been registered in our database yet. \n Please register by pressing /register')
#         return ConversationHandler.END

#     inline_keyboard = [
#         [InlineKeyboardButton('food', callback_data='food')],
#         [InlineKeyboardButton('transport', callback_data='transport')],
#         [InlineKeyboardButton('entertainment', callback_data='entertainment')],
#         [InlineKeyboardButton('misc', callback_data='misc')],
#     ]
#     markup = InlineKeyboardMarkup(inline_keyboard)

#     await update.message.reply_text('Please select the category of expenditure to remove:', reply_markup=markup)
#     return RemoveExpenseState.SELECT_CATEGORY

async def removeExpense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if str(user_id) not in users_data:
        await update.message.reply_text('You have not been registered in our database yet. \n Please register by pressing /register')
        return ConversationHandler.END

    user_categories = users_data[str(user_id)]["expenditureCategory"]
    inline_keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in user_categories.keys()]
    markup = InlineKeyboardMarkup(inline_keyboard)

    await update.message.reply_text('Please select the category of expenditure to remove:', reply_markup=markup)
    return RemoveExpenseState.SELECT_CATEGORY

async def handle_remove_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query: CallbackQuery = update.callback_query
    query.answer()
    chosen_category = query.data

    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    items = users_data[str(user_id)]["expenditureCategory"][chosen_category]

    if not items:
        await query.edit_message_text(f'No items found under {chosen_category} category.')
        return ConversationHandler.END

    inline_keyboard = [[InlineKeyboardButton(item[0], callback_data=item[0])] for item in items]
    markup = InlineKeyboardMarkup(inline_keyboard)

    context.user_data['selected_category'] = chosen_category

    await query.edit_message_text(f'Select the item to remove from {chosen_category}:', reply_markup=markup)
    return RemoveExpenseState.SELECT_EXPENSE

async def handle_remove_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query: CallbackQuery = update.callback_query
    await query.answer()
    chosen_item = query.data
    chosen_category = context.user_data['selected_category']

    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    expenses = users_data[str(user_id)]["expenditureCategory"][chosen_category]
    for expense in expenses:
        if expense[0] == chosen_item:
            users_data[str(user_id)]["currentDailyExpenditure"] -= expense[1]
            users_data[str(user_id)]["currentMonthlyExpenditure"] -= expense[1]
            expenses.remove(expense)
            break

    with open('users_expenses.json', 'w') as file:
        json.dump(users_data, file, indent=4)

    await query.edit_message_text(f"Successfully removed {chosen_item} from {chosen_category}! \nYour current expenditure now stands at {users_data[str(user_id)]['currentDailyExpenditure']} \n\nClick on /viewDailyExpenses to see the breakdown of today's expenditure!")
    return ConversationHandler.END

conv_handler_removeExpense = ConversationHandler(
    entry_points=[CommandHandler('removeExpense', removeExpense)],
    states={
        RemoveExpenseState.SELECT_CATEGORY: [CallbackQueryHandler(handle_remove_category_callback)],
        RemoveExpenseState.SELECT_EXPENSE: [CallbackQueryHandler(handle_remove_expense)],
    },
    fallbacks=[CommandHandler("removeExpense", removeExpense)]
)
