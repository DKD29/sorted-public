from backend.database import load_data, save_data


def get_budgets(username):

    budgets = load_data(
        "budgets.json"
    )

    return budgets.get(
        username,
        {}
    )


def set_budget(
    username,
    category,
    amount,
    month
):

    budgets = load_data(
        "budgets.json"
    )

    if username not in budgets:

        budgets[username] = {}

    if month not in budgets[username]:

        budgets[username][month] = {}

    budgets[username][month][category] = {
        "amount": float(amount)
    }

    save_data(
        "budgets.json",
        budgets
    )


def delete_budget(
    username,
    category,
    month
):

    budgets = load_data(
        "budgets.json"
    )

    if username not in budgets:
        return

    if month not in budgets[username]:
        return

    if category not in budgets[username][month]:
        return

    del budgets[username][month][category]

    if len(budgets[username][month]) == 0:

        del budgets[username][month]

    if len(budgets[username]) == 0:

        del budgets[username]

    save_data(
        "budgets.json",
        budgets
    )

def calculate_budget_status(
    username,
    transactions,
    month
):

    budgets = get_budgets(
        username
    )

    if month not in budgets:

        return {}

    monthly_budgets = budgets[month]

    results = {}

    for category, budget_data in monthly_budgets.items():

        budget_amount = float(
            budget_data["amount"]
        )

        spent = 0.0

        for transaction in transactions:

            transaction_date = transaction["timestamp"][:7]

            if (
                transaction_date == month
                and transaction["category"] == category
            ):

                spent += float(
                    transaction["amount"]
                )

        remaining = (
            budget_amount - spent
        )

        if spent > budget_amount:

            status = "Over budget"

            over_amount = (
                spent - budget_amount
            )

        else:

            status = "Within budget"

            over_amount = 0.0

        results[category] = {

            "budget": budget_amount,

            "spent": spent,

            "remaining": remaining,

            "status": status,

            "over_amount": over_amount

        }

    return results