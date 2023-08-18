from datetime import datetime

def check_and_transition_to_new_month(user_data):
    current_month = datetime.now().month
    lastUpdatedMonth = user_data["lastUpdatedMonth"]

    if lastUpdatedMonth != None and current_month != int(lastUpdatedMonth):  
        user_data["monthlyHistory"][str(lastUpdatedMonth)] = user_data["currentMonthlyExpenditure"]

        # Reset the monthly expenditure
        user_data["currentMonthlyExpenditure"] = 0

        # Update the last updated month
        user_data["lastUpdatedMonth"] = str(current_month)

    else:
        user_data["monthlyHistory"][str(current_month)] = user_data["currentMonthlyExpenditure"]
        user_data["lastUpdatedMonth"] = str(current_month)
