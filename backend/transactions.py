from backend.database import load_data, save_data

from datetime import datetime

def get_transactions(username):

    transactions = load_data(
        "transactions.json"
    )

    return transactions.get(
        username,
        []
    )


def add_transaction(
    username,
    merchant,
    amount,
    category
):

    transactions = load_data(
        "transactions.json"
    )

    if username not in transactions:
        transactions[username] = []

    transactions[username].append(
        {
            "timestamp": datetime.now().isoformat(),
            "merchant": merchant,
            "amount": float(amount),
            "category": category
        }
    )

    save_data(
        "transactions.json",
        transactions
    )


def delete_transaction(
    username,
    index
):

    transactions = load_data(
        "transactions.json"
    )

    if (
        username in transactions
        and 0 <= index < len(transactions[username])
    ):

        transactions[username].pop(index)

        save_data(
            "transactions.json",
            transactions
        )


def edit_transaction(
    username,
    index,
    merchant,
    amount,
    category
):

    transactions = load_data(
        "transactions.json"
    )

    if (
        username in transactions
        and 0 <= index < len(transactions[username])
    ):

        old_timestamp = transactions[username][index]["timestamp"]

        transactions[username][index] = {

            "timestamp": old_timestamp,

            "merchant": merchant,

            "amount": float(amount),

            "category": category

        }

        save_data(
            "transactions.json",
            transactions
        )