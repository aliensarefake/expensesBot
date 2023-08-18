from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import json

async def viewMonthlyExpenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with open('users_expenses.json', 'r') as file:
        users_data = json.load(file)

    if str(user_id) not in users_data:
        await update.message.reply_text('Your current expenditure for the month: $0')

    else:
        currentMonthExpenditure = users_data[str(user_id)]['currentMonthlyExpenditure']
        reply_message = f'<b>Your Current Expenditure for the month: ${currentMonthExpenditure}</b>\n\n'
        await update.message.reply_text(reply_message, parse_mode='HTML')