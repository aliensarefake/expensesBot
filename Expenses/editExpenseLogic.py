from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import json

class EditExpenseState:
    SELECT_CATEGORY = 0
    SELECT_EXPENSE = 1
    ENTER_NEW_VALUE = 2
    CONFIRM = 3


async def editExpense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if str(user_id) not in users_data:
        await update.message.reply_text('You have not been registered in our database yet. \nPlease register by pressing /register')
        return ConversationHandler.END

    user_categories = users_data[str(user_id)]["expenditureCategory"].keys()
    inline_keyboard = [[InlineKeyboardButton(category, callback_data=category)] for category in user_categories]
    markup = InlineKeyboardMarkup(inline_keyboard)

    await update.message.reply_text('Please select the category of the expense you wish to edit:', reply_markup=markup)
    return EditExpenseState.SELECT_CATEGORY

async def handle_edit_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query: CallbackQuery = update.callback_query
    await query.answer()
    chosen_category = query.data

    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    items = users_data[str(user_id)]["expenditureCategory"][chosen_category]
    inline_keyboard = [[InlineKeyboardButton(item[0], callback_data=item[0])] for item in items]
    markup = InlineKeyboardMarkup(inline_keyboard)

    context.user_data['selected_category'] = chosen_category

    await query.edit_message_text(f'Select the item to edit from {chosen_category}:', reply_markup=markup)
    return EditExpenseState.SELECT_EXPENSE

async def handle_edit_expense_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query: CallbackQuery = update.callback_query
    await query.answer()
    chosen_item = query.data
    chosen_category = context.user_data['selected_category']

    context.user_data['selected_item'] = chosen_item

    await query.edit_message_text(f'You selected {chosen_item} from {chosen_category}. Please enter the new value in the format: $10')
    return EditExpenseState.ENTER_NEW_VALUE

async def enter_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chosen_category = context.user_data['selected_category']
    chosen_item = context.user_data['selected_item']

    user_input = update.message.text

    if not user_input.startswith('$') or not user_input[1:].replace('.', '', 1).isdigit():
        await update.message.reply_text('Invalid cost format. Please enter the cost with a dollar sign, like $10.')
        return EditExpenseState.ENTER_NEW_VALUE

    new_value = float(user_input[1:])

    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    for expense in users_data[str(user_id)]["expenditureCategory"][chosen_category]:
        if expense[0] == chosen_item:
            old_value = expense[1]
            context.user_data['old_value'] = old_value
            if old_value == new_value:
                await update.message.reply_text(f'You entered the same value as before.\n Please enter a different value')
                return EditExpenseState.ENTER_NEW_VALUE

            context.user_data['new_value'] = new_value
            await update.message.reply_text(f'You entered a new value of {new_value} for {chosen_item}. Do you want to confirm? (Yes/No)')
            return EditExpenseState.CONFIRM

    return ConversationHandler.END

async def confirm_or_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower()

    if user_input not in ["yes", "no"]:
        await update.message.reply_text('Invalid response. Please type "Yes" or "No".')
        return EditExpenseState.CONFIRM

    if user_input == "no":
        await update.message.reply_text('Editing canceled.')
        return ConversationHandler.END

    # If "yes", apply the changes
    user_id = update.effective_user.id
    chosen_category = context.user_data['selected_category']
    chosen_item = context.user_data['selected_item']
    new_value = context.user_data['new_value']
    change_in_expense = new_value - context.user_data['old_value']

    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    # Update both daily & monthly expenditure
    users_data[str(user_id)]["currentDailyExpenditure"] += change_in_expense
    users_data[str(user_id)]["currentMonthlyExpenditure"] += change_in_expense

    for expense in users_data[str(user_id)]["expenditureCategory"][chosen_category]:
        if expense[0] == chosen_item:
            # Update the value
            expense[1] = new_value
            # Handle other updates like daily and monthly expenditures, etc.

    with open('users_expenses.json', 'w') as file:
        json.dump(users_data, file, indent=4)

    await update.message.reply_text(f'Successfully updated the value for {chosen_item} in {chosen_category} to {new_value}!')
    return ConversationHandler.END

def exit_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text("You've exited the conversation.")
    return ConversationHandler.END


conv_handler_editExpense = ConversationHandler(
    entry_points=[CommandHandler('editExpense', editExpense)],
    states={
        EditExpenseState.SELECT_CATEGORY: [CallbackQueryHandler(handle_edit_category_callback)],
        EditExpenseState.SELECT_EXPENSE: [CallbackQueryHandler(handle_edit_expense_callback)],
        EditExpenseState.ENTER_NEW_VALUE: [MessageHandler(filters.TEXT, enter_new_value)],
        EditExpenseState.CONFIRM: [MessageHandler(filters.TEXT, confirm_or_exit)],
    },
    fallbacks=[CommandHandler("exit", exit_conversation)]
)
