import requests

from datetime import datetime

from backend.budget import (
    calculate_budget_status
)

def analyze_transactions(transactions):

    total_spending = 0.0
    total_income = 0.0

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

        transaction_type = transaction.get(
            "type",
            "expense"
        )

        if transaction_type == "income":

            total_income += amount

            continue

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

    net_balance = (
        total_income - total_spending
    )

    return {
        "total_spending": total_spending,
        "total_income": total_income,
        "net_balance": net_balance,
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
- Profession / occupation: {profile.get("profession")}
- User type: {profile.get("user_type")}
- Income source: {profile.get("income_source")}
- Preferred detail level: {profile.get("detail_level")}

Financial information:
- Total income: ₹{analysis["total_income"]:.2f}
- Total spending: ₹{analysis["total_spending"]:.2f}
- Net balance: ₹{analysis["net_balance"]:.2f}
- Category breakdown: {analysis["category_breakdown"]}
- Category percentages: {analysis["category_percentages"]}
- Highest spending category: {analysis["highest_category"]}
- Largest expense: {analysis["largest_expense"]}

Budget information:
- Current month budget status: {budget_status}


Your task:

1. Summarize the user's finances.
2. Identify important spending patterns.
3. Explain the relationship between income, spending, and net balance when enough information is available.
4. Give practical suggestions based on the user's goals, age, profession, income situation, spending patterns, and budgets.
5. Provide investment guidance ONLY when the available financial information supports it.
6. When discussing investments, consider all of the following:
   - The user's age.
   - The user's profession or occupation.
   - The user's income source and whether income is actually provided.
   - The user's total income and net balance.
   - The user's spending patterns.
   - Their available budget and remaining budget when provided.
   - Whether the user appears to have money left after recorded spending.
7. Do not recommend investing money that is needed for essential expenses or existing budget commitments.
8. If the user's net balance is negative or zero, prioritize controlling spending, maintaining liquidity, and building financial stability rather than recommending investments.
9. If income is unknown, do not invent an income amount or assume the user has regular income.
10. If the user's financial situation suggests they have surplus money, explain what type of investment approach may be appropriate rather than promising returns.
11. Consider age-appropriate financial guidance. If the user is a minor, do not present investment actions as something they should independently execute. Explain that investments may require a parent/guardian and should be considered with appropriate adult supervision.
12. Do not recommend risky, speculative, leveraged, or guaranteed-return investments.
13. Do not recommend specific investments merely because they are popular.
14. Do not claim that any investment will definitely make money.
15. Clearly distinguish between financial education and personalized professional financial advice.
16. Use ONLY information explicitly provided in the user information, financial information, and budget information.
17. Never invent dates, time periods, income amounts, budgets, savings amounts, investment amounts, or financial events.
18. If a fact is unknown, do not guess it.
19. You may explain or interpret the provided calculations, but do not create new financial facts.
20. Follow the user's requested detail level.

Investment guidance rules:

- If net balance is negative:
  Focus on reducing unnecessary spending and improving cash flow. Do not recommend investing.

- If net balance is zero:
  Focus on financial stability and maintaining available cash. Do not recommend investing unless there is clear evidence of available surplus money.

- If net balance is positive:
  Explain that the positive balance represents money left after the recorded transactions, NOT necessarily money available to invest.
  Only discuss investment possibilities if the user's goals and financial situation support doing so.

- If the user has a budget:
  Do not suggest investments that would interfere with staying within the budget.

- If the user's goals involve short-term needs:
  Prioritize liquidity and capital preservation over volatile investments.

- If the user's goals are long-term and there is clear surplus money:
  Educationally explain suitable long-term investment categories at a high level, while avoiding guarantees and risky speculation.

- If the user's age indicates they are a minor:
  Keep investment guidance educational and state that actual investing should involve a parent/guardian where legally required.

- If profession or income source suggests irregular income:
  Place greater emphasis on maintaining accessible funds and financial stability before discussing investments.

Important:
The spending information represents only transactions recorded in SO₹TED.
No spending period has been provided.
The user's actual income amount may not be provided.
No budget may have been provided.
A positive net balance does NOT automatically mean the user has investable money.
Do not assume any of these values.

Return the response using these sections:

## Financial Summary

## Spending Analysis

## Investment Considerations

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
