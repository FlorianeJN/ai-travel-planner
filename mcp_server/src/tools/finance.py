import httpx


async def convert_currency(amount: float, from_curr: str, to_curr: str) -> dict:
    """Converts an amount between currencies via the Frankfurter API."""
    from_c = from_curr.upper()
    to_c = to_curr.upper()

    if from_c == to_c:
        return {"original_amount": amount, "converted_amount": amount, "currency": to_c}

    url = f"https://api.frankfurter.dev/v1/latest?amount={amount}&base={from_c}&symbols={to_c}"

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, timeout=10.0)
            if res.status_code != 200:
                return {"error": f"Failed to convert from {from_c} to {to_c}"}

            rates = res.json().get("rates", {})
            converted = rates.get(to_c)
            return {
                "original_amount": amount,
                "from": from_c,
                "to": to_c,
                "converted_amount": converted,
            }
        except Exception as e:
            return {"error": f"Network error: {str(e)}"}
