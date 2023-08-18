from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
import json

SELECT_LIMIT_TYPE, ENTER_LIMIT_VALUE = range(2)

async def start_set_limit(update: Update, context):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)
    
    if str(user_id) in users_data: return await show_limit_options(update, context)
    else:
        await update.message.reply_text('You have not been registered in our database yet. \n Please register by pressing /register')
        return ConversationHandler.END

async def show_limit_options(update, context):
    inline_keyboard = [
        [InlineKeyboardButton('Daily Limit', callback_data='dailyLimit')],
        [InlineKeyboardButton('Weekly Limit', callback_data='weeklyLimit')],
        [InlineKeyboardButton('Monthly Limit', callback_data='monthlyLimit')],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text('Please choose the type of limit you want to set:', reply_markup=markup)
    return SELECT_LIMIT_TYPE

async def handle_limit_type_callback(update: Update, context):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    query = update.callback_query
    await query.answer()

    chosen_limit_type = query.data

    #check if limit has alr been set
    if users_data[str(user_id)][chosen_limit_type] != None:
        limit_value = users_data[str(user_id)][f"{chosen_limit_type}"]
        await query.message.reply_text(f'You have already set the {chosen_limit_type.capitalize()} Limit to ${limit_value}.') # Here
        return ConversationHandler.END

    else:
        context.user_data['chosen_limit_type'] = chosen_limit_type
        await query.edit_message_text(f'You selected {chosen_limit_type.capitalize()} Limit. Now, please enter the value for this limit:')
        return ENTER_LIMIT_VALUE

async def enter_limit_value(update: Update, context):
    user_id = update.effective_user.id
    chosen_limit_type = context.user_data['chosen_limit_type']
    limit_value = update.message.text
    print(limit_value)
    if limit_value[0] == "$": limit_value = limit_value[1:]

    if limit_value.isdigit() and int(limit_value) >= 0:
        with open('users_expenses.json', 'r') as file:
            users_data = json.load(file)

        users_data[str(user_id)][f"{chosen_limit_type}"] = int(limit_value)

        with open('users_expenses.json', 'w') as file:
            json.dump(users_data, file, indent=4)

        await update.message.reply_text(f'Successfully set the {chosen_limit_type.capitalize()} Limit to ${limit_value}.')
        return ConversationHandler.END
    
    else:
        await update.message.reply_text('Invalid value. Please enter again!')
        return ENTER_LIMIT_VALUE

conv_handler_set_limit = ConversationHandler(
    entry_points=[CommandHandler('setLimits', start_set_limit)],
    states={
        SELECT_LIMIT_TYPE: [CallbackQueryHandler(handle_limit_type_callback)],
        ENTER_LIMIT_VALUE: [MessageHandler(filters.TEXT, enter_limit_value)],
    },
    fallbacks=[CommandHandler("setLimits", start_set_limit)]  
)
