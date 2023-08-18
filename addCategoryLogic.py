from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import json


class AddCategoryState:
    ENTER_CATEGORY_NAME = 0

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please enter the name of the new category you wish to add:')
    return AddCategoryState.ENTER_CATEGORY_NAME

async def enter_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().capitalize()

    if not user_input:
        await update.message.reply_text('Category name cannot be empty. Please enter a valid name or type /exit to cancel:')
        return AddCategoryState.ENTER_CATEGORY_NAME

    user_id = update.effective_user.id

    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if user_input in users_data[str(user_id)]["expenditureCategory"]:
        await update.message.reply_text(f'Category "{user_input}" already exists. Please enter a different name!')
        return AddCategoryState.ENTER_CATEGORY_NAME

    users_data[str(user_id)]["expenditureCategory"][user_input] = []

    with open('users_expenses.json', 'w') as file:
        json.dump(users_data, file, indent=4)

    await update.message.reply_text(f'Successfully added the new category "{user_input}"!')
    return ConversationHandler.END


conv_handler_addCategory = ConversationHandler(
    entry_points=[CommandHandler('addCategory', add_category)],
    states={
        AddCategoryState.ENTER_CATEGORY_NAME: [MessageHandler(filters.TEXT, enter_category_name)],
    },
    fallbacks=[] 
)
