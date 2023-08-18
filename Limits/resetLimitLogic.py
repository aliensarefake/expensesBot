from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import json

CHECK_USER, SELECT_CATEGORY, ENTER_NEW_LIMIT = range(3)

async def start_reset_limit(update: Update, context):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)
    
    if str(user_id) in users_data:
        return await show_categories(update, context)
    else:
        await update.message.reply_text('You have not been registered in our database yet. \n Please register by pressing /register')
        return ConversationHandler.END

async def show_categories(update, context):
    inline_keyboard = [
        [InlineKeyboardButton('Daily Limit', callback_data='dailyLimit')],
        [InlineKeyboardButton('Weekly Limit', callback_data='weeklyLimit')],
        [InlineKeyboardButton('Monthly Limit', callback_data='monthlyLimit')],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text('Please choose the category you want to reset:', reply_markup=markup)
    return SELECT_CATEGORY

async def handle_category_callback(update: Update, context):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    query = update.callback_query
    await query.answer()

    chosen_category = query.data

    if users_data[str(user_id)][chosen_category] != None:
        context.user_data['chosen_category'] = chosen_category
        await query.edit_message_text(f'You selected {chosen_category.capitalize()}. Please enter the new limit:')
        return ENTER_NEW_LIMIT
    else:
        await query.edit_message_text(f'The {chosen_category.capitalize()} has not been set yet.')
        return ConversationHandler.END

async def enter_new_limit(update: Update, context):
    user_id = update.effective_user.id
    chosen_category = context.user_data['chosen_category']
    new_limit = update.message.text
    if new_limit[0] == "$": new_limit = new_limit[1:]

    if new_limit.isdigit() and int(new_limit) >= 0:
        with open('users_expenses.json', 'r') as file:
            users_data = json.load(file)

        users_data[str(user_id)][f"{chosen_category}"] = int(new_limit)

        with open('users_expenses.json', 'w') as file:
            json.dump(users_data, file, indent=4)

        await update.message.reply_text(f'Successfully updated the {chosen_category.capitalize()} to ${new_limit}.')
        return ConversationHandler.END
    else:
        await update.message.reply_text('Invalid value. Please enter again!')
        return ENTER_NEW_LIMIT

conv_handler_reset_limit = ConversationHandler(
    entry_points=[CommandHandler('resetLimits', start_reset_limit)],
    states={
        CHECK_USER: [CommandHandler('resetLimits', start_reset_limit)],
        SELECT_CATEGORY: [CallbackQueryHandler(handle_category_callback)],
        ENTER_NEW_LIMIT: [MessageHandler(filters.TEXT, enter_new_limit)],
    },
    fallbacks=[CommandHandler("resetLimits", start_reset_limit)]  
)
