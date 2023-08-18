from telegram import Update
from telegram.ext import ContextTypes
import json

# async def viewDailyExpenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     with open('users_expenses.json', 'r') as file:
#         users_data = json.load(file)

#     if str(user_id) not in users_data:
#         await update.message.reply_text('Your current expenditure for the day: $0')
#     else:

#         category_totals = {"food": 0, "transport": 0, "entertainment": 0, "misc": 0}
#         currentExpenditure = users_data[str(user_id)]["currentDailyExpenditure"]

#         for cat in category_totals.keys():
#             for item in users_data[str(user_id)]["expenditureCategory"][cat]:
#                 category_totals[cat] += item[1]

#         # Create the reply message
#         reply_message = f'*Your Current Expenditure for the day: ${currentExpenditure}*\n\n'
#         reply_message += '\n'.join([f'_*{cat.capitalize()}:*_ ${total}' for cat, total in category_totals.items()])

#         await update.message.reply_text(reply_message, parse_mode='Markdown')

async def viewDailyExpenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if str(user_id) not in users_data:
        await update.message.reply_text('Your current expenditure for the day: $0')
    else:
        # Retrieve the user's expenditure categories
        user_categories = users_data[str(user_id)]["expenditureCategory"]

        # Calculate the total for each category
        category_totals = {cat: sum(item[1] for item in items) for cat, items in user_categories.items()}

        currentExpenditure = users_data[str(user_id)]["currentDailyExpenditure"]

        # Create the reply message
        reply_message = f'*Your Current Expenditure for the day: ${currentExpenditure}*\n\n'
        reply_message += '\n'.join([f'_*{cat.capitalize()}:*_ ${total}' for cat, total in category_totals.items()])

        await update.message.reply_text(reply_message, parse_mode='Markdown')
