from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import json

ASKING, REGISTERING = range(2)

async def ask_for_categories(update: Update, context: ContextTypes):
    user_id = update.effective_user.id
    context.user_data['user_id'] = user_id

    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if str(user_id) in users_data:
        await update.message.reply_text(f'Hello <b>{update.effective_user.username}</b>! You have already been registered.', parse_mode='HTML')
        return ConversationHandler.END

    custom_categories_message = (
        "Please enter your custom expenditure categories to better tailor the tracking to your personal spending habits. Separate each category with a comma. Here are some ideas for categories you might consider:\n\n"
        "<b>- Groceries</b>\n"
        "<b>- Entertainment</b>\n"
        "<b>- Dining Out</b>\n"
        "<b>- Transportation</b>\n"
        "<b>- Utilities</b>\n"
        "<b>- Health Care</b>\n"
        "<b>- Clothing</b>\n"
        "<b>- Savings/Investments</b>\n\n"
        "You can follow this format: [Groceries, Entertainment, Dining Out, ...]\n"
        "Feel free to include any other categories that are relevant to your spending!"
    )

    await update.message.reply_text(custom_categories_message, parse_mode='HTML')
    return ASKING

async def register_categories(update: Update, context: ContextTypes):
    categories_text = update.message.text

    # Validate the input format: check if it starts with '[' and ends with ']'
    if not (categories_text.startswith('[') and categories_text.endswith(']')):
        await update.message.reply_text('Invalid format! Please enter your custom expenditure categories in this format: [cat 1, cat 2, cat 3, ...]')
        return ASKING

    categories = categories_text[1:-1].split(', ')
    
    # Additional check for empty categories
    if not all(categories):
        await update.message.reply_text('Invalid format or empty category detected! Please enter your custom expenditure categories in this format: [cat 1, cat 2, cat 3, ...]')
        return ASKING

    user_id = context.user_data['user_id']

    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    users_data[str(user_id)] = {
        "lastRecordedDate": None,
        "lastUpdatedMonth": None,
        "currentDailyExpenditure": 0,
        "currentWeeklyExpenditure": 0,
        "currentMonthlyExpenditure": 0,
        "expenditureCategory": {cat.strip(): [] for cat in categories}, 
        "dailyLimit": None,
        "weeklyLimit": None,
        "monthlyLimit": None,
        "dailyHistory": {},
        "monthlyHistory": {}
    }

    with open('users_expenses.json', 'w') as file:
        json.dump(users_data, file, indent=4)

    await update.message.reply_text(f'Successfully registered for <b>{update.effective_user.username}</b>...', parse_mode='HTML')

    return ConversationHandler.END



conv_handler_register = ConversationHandler(
    entry_points=[CommandHandler('register', ask_for_categories)],
    states={
        ASKING: [MessageHandler(filters.TEXT, register_categories)],
    },
    fallbacks=[]
)