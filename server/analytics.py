# @index-begin
# @symbol variable/parameter: database L31
# @symbol variable/parameter: forecasting L31
# @symbol function/class: report L31
# @symbol variable/parameter: user L31
# @symbol variable/parameter: parameters L33
# @symbol variable/parameter: predicate L34
# @symbol variable/parameter: rows L38
# @symbol variable/parameter: row L44
# @symbol variable/parameter: series L44
# @symbol variable/parameter: result L45
# @symbol variable/parameter: values L54
# @symbol variable/parameter: count L55
# @symbol variable/parameter: average_x L56
# @symbol variable/parameter: average_y L57
# @symbol variable/parameter: sxx L58
# @symbol variable/parameter: slope L59
# @symbol variable/parameter: value L60
# @symbol variable/parameter: intercept L63
# @symbol variable/parameter: residual_sd L64
# @symbol variable/parameter: index L68
# @symbol variable/parameter: predicted L69
# @symbol variable/parameter: width L70
# @index-end
"""Explainable monthly summaries and bounded baseline forecasts. Index: docs/code-index.md."""

import math
import sqlite3


def report(database: sqlite3.Connection, user: dict, forecasting: bool) -> dict:
    """Aggregate exact cents, scope customer rows, and label projections as noncausal baselines."""
    parameters = [user["workspace"]]
    predicate = "workspace=?"
    if user["role"] == "customer":
        predicate += " AND customer=?"
        parameters.append(user["customer"])
    rows = database.execute(
        "SELECT month,SUM(quantity) quantity,SUM(revenue_cents) revenue_cents FROM sales WHERE "
        + predicate
        + " GROUP BY month ORDER BY month",
        parameters,
    ).fetchall()
    series = [dict(row) for row in rows]
    result = {
        "currency": "USD",
        "series": series,
        "revenue_cents": sum(row["revenue_cents"] for row in series),
        "quantity": sum(row["quantity"] for row in series),
        "forecast": [],
        "method": "Ordinary least squares monthly revenue baseline. No seasonality or causal assumptions; indicative only.",
    }
    if forecasting and len(series) >= 3:
        values = [row["revenue_cents"] for row in series]
        count = len(values)
        average_x = (count - 1) / 2
        average_y = sum(values) / count
        sxx = sum((index - average_x) ** 2 for index in range(count))
        slope = (
            sum((index - average_x) * (value - average_y) for index, value in enumerate(values))
            / sxx
        )
        intercept = average_y - slope * average_x
        residual_sd = math.sqrt(
            sum((value - intercept - slope * index) ** 2 for index, value in enumerate(values))
            / (count - 2)
        )
        for index in range(count, count + 3):
            predicted = max(0, round(intercept + slope * index))
            width = round(
                1.96 * residual_sd * math.sqrt(1 + 1 / count + (index - average_x) ** 2 / sxx)
            )
            result["forecast"].append(
                {
                    "month_offset": index - count + 1,
                    "revenue_cents": predicted,
                    "low_cents": max(0, predicted - width),
                    "high_cents": predicted + width,
                }
            )
        result["method"] += " Approximate 95% normal prediction band (not a guaranteed interval)."
    return result
