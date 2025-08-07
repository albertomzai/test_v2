#!/usr/bin/env python3
"""
Flask backend for a mortgage simulator.
Provides:
- GET /   : Serves the static `index.html` from the ``static`` folder.
- POST /calcular : Receives loan data in JSON and returns an amortization table.

All logic is self‑contained, uses only Flask, and follows the Colmena style guide.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Dict

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class AmortizationEntry:
    month: int
    payment: float
    principal: float
    interest: float
    balance: float

    def to_dict(self) -> Dict[str, float | int]:
        """Convert the entry into a serialisable dictionary.

        Returns:
            A mapping with keys ``month``, ``payment``, ``principal``, ``interest`` and
            ``balance``.
        """
        return {
            "month": self.month,
            "payment": round(self.payment, 2),
            "principal": round(self.principal, 2),
            "interest": round(self.interest, 2),
            "balance": round(self.balance, 2),
        }

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def calculate_amortization(principal: float, annual_rate: float, years: int) -> List[AmortizationEntry]:
    """Calculate a fixed‑payment amortization schedule.

    Args:
        principal: Loan amount in the same currency as ``annual_rate``.
        annual_rate: Annual interest rate expressed as a percentage (e.g., 5.0 for 5%).
        years: Term of the loan in years.

    Returns:
        A list of :class:`AmortizationEntry` objects, one per month.
    """
    monthly_rate = annual_rate / 100 / 12
    total_months = years * 12
    if monthly_rate == 0:  # Edge case: zero interest loan
        payment = principal / total_months
    else:
        payment = principal * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)

    balance = principal
    schedule: List[AmortizationEntry] = []
    for month in range(1, total_months + 1):
        interest_payment = balance * monthly_rate
        principal_payment = payment - interest_payment
        balance -= principal_payment
        if balance < 0:
            balance = 0.0
        schedule.append(
            AmortizationEntry(
                month=month,
                payment=payment,
                principal=principal_payment,
                interest=interest_payment,
                balance=balance,
            )
        if balance == 0.0:
            break
    return schedule

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main page.

    Returns:
        The ``index.html`` file from the static folder.
    """
    return send_from_directory(app.static_folder, "index.html")

@app.route("/calcular", methods=["POST"])
def calcular():
    """Return an amortization table for the supplied loan data.

    Expects JSON payload with keys ``principal``, ``annual_rate`` and ``years``.
    Returns:
        JSON object containing a list of monthly entries.
    """
    try:
        data = request.get_json(force=True)
    except Exception as exc:  # pragma: no cover
        return jsonify(error=f"Invalid JSON payload: {exc}"), 400

    try:
        principal = float(data["principal"])
        annual_rate = float(data["annual_rate"])
        years = int(data["years"])
    except (KeyError, ValueError) as exc:  # pragma: no cover
        return jsonify(error=f"Missing or invalid fields: {exc}"), 400

    try:
        schedule = calculate_amortization(principal, annual_rate, years)
    except Exception as exc:  # pragma: no cover
        return jsonify(error=f"Calculation error: {exc}"), 500

    return jsonify(table=[entry.to_dict() for entry in schedule])

# ---------------------------------------------------------------------------
# Main block (no external API, so no .env creation needed)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # No external secrets required; run the development server.
    app.run(host="0.0.0.0", port=5000, debug=True)
