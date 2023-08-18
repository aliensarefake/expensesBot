from datetime import datetime

# def check_and_transition_to_new_day(user_data):
#     # Get current date as a string
#     current_date = datetime.today().strftime('%Y-%m-%d')
#     last_recorded_date = user_data.get('lastRecordedDate')

#     if current_date == last_recorded_date or current_date not in user_data["dailyHistory"]:
#         # Update the current day's expenditure in daily history
#         user_data['dailyHistory'][current_date] = user_data['expenditureCategory']
#         user_data["lastRecordedDate"] = current_date
        
#     else:
#         # Update the day before to daily history
#         if last_recorded_date:
#             user_data['dailyHistory'][last_recorded_date] = user_data['expenditureCategory']

#         # Reset current daily expenditures
#         user_data['currentDailyExpenditure'] = 0
#         user_data['expenditureCategory'] = {
#             "food": [],
#             "transport": [],
#             "entertainment": [],
#             "misc": []
#         }
#         user_data['lastRecordedDate'] = current_date  # Update last recorded date

def check_and_transition_to_new_day(user_data):
    # Get current date as a string
    current_date = datetime.today().strftime('%Y-%m-%d')
    last_recorded_date = user_data.get('lastRecordedDate')

    # Determine if there are categories already present in the user_data
    existing_categories = user_data['expenditureCategory'].keys() if 'expenditureCategory' in user_data else []

    if current_date == last_recorded_date or current_date not in user_data["dailyHistory"]:
        # Update the current day's expenditure in daily history
        user_data['dailyHistory'][current_date] = user_data['expenditureCategory']
        user_data["lastRecordedDate"] = current_date

    else:
        # Update the day before to daily history
        if last_recorded_date:
            user_data['dailyHistory'][last_recorded_date] = user_data['expenditureCategory']

        # Reset current daily expenditures
        user_data['currentDailyExpenditure'] = 0

        # Create a new expenditureCategory with the existing categories set to empty lists
        user_data['expenditureCategory'] = {category: [] for category in existing_categories}

        user_data['lastRecordedDate'] = current_date  # Update last recorded date
