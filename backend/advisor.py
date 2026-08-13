import requests

from datetime import datetime

from backend.budget import (
    calculate_budget_status
)

def analyze_transactions(transactions):

    total_spending = 0

    category_breakdown = {}

    largest_expense = {
        "merchant": None,
        "amount": 0,
        "category": None
    }


    for transaction in transactions:

        amount = float(
            transaction["amount"]
        )

        total_spending += amount


        category = transaction["category"]


        if category not in category_breakdown:

            category_breakdown[category] = 0


        category_breakdown[category] += amount


        if amount > largest_expense["amount"]:

            largest_expense = {
                "merchant": transaction["merchant"],
                "amount": amount,
                "category": category
            }


    if category_breakdown:

        highest_category = max(
            category_breakdown,
            key=category_breakdown.get
        )

    else:

        highest_category = None


    category_percentages = {}

    for category, amount in category_breakdown.items():

        if total_spending > 0:

            category_percentages[category] = (
                amount / total_spending
            ) * 100

        else:

            category_percentages[category] = 0


    return {
        "total_spending": total_spending,
        "category_breakdown": category_breakdown,
        "category_percentages": category_percentages,
        "largest_expense": largest_expense,
        "highest_category": highest_category
    }

def build_prompt(
    profile,
    analysis,
    budget_status
):

    prompt = f"""
You are the financial advisor inside SO₹TED.

User information:
- Age: {profile.get("age")}
- User type: {profile.get("user_type")}
- Income source: {profile.get("income_source")}
- Financial goals: {profile.get("goals")}
- Preferred detail level: {profile.get("detail_level")}

Spending information:
- Total spending: ₹{analysis["total_spending"]:.2f}
- Category breakdown: {analysis["category_breakdown"]}
- Category percentages: {analysis["category_percentages"]}
- Highest spending category: {analysis["highest_category"]}
- Largest expense: {analysis["largest_expense"]}

Budget information:

- Current month budget status: {budget_status}


Your task:

1. Summarize the user's spending.
2. Identify important spending patterns.
3. Give practical suggestions based on the user's goals.
4. Keep the advice appropriate for the user's age and situation.
5. Use ONLY information explicitly provided in the user information and spending information.
6. Never invent dates, time periods, income amounts, budgets, savings amounts, or financial events.
7. If a fact is unknown, do not guess it.
8. You may explain or interpret the provided calculations, but do not create new financial facts.
9. Do not recommend risky investments.
10. Do not claim to be a professional financial advisor.
11. Follow the user's requested detail level.

Important:
The spending information represents only transactions recorded in SO₹TED.
No spending period has been provided.
The user's actual income amount has not been provided.
No budget has been provided.
Do not assume any of these values.

Return the response using these sections:

## Financial Summary

## Spending Analysis

## Suggestions
"""

    return prompt

def generate_advice(
    username,
    profile,
    transactions
):

    analysis = analyze_transactions(
        transactions
    )

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    budget_status = calculate_budget_status(
        username,
        transactions,
        current_month
    )

    prompt = build_prompt(
        profile,
        analysis,
        budget_status
    )

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

    except requests.exceptions.ConnectionError:

        return (
            "SO₹TED AI is currently unavailable. "
            "Please make sure Ollama is running and try again."
        )

    except requests.exceptions.Timeout:

        return (
            "SO₹TED AI took too long to respond. "
            "Please try again."
        )

    if response.status_code != 200:

        return (
            "SO₹TED AI could not generate advice right now. "
            "Please try again."
        )

    data = response.json()

    return data["response"]