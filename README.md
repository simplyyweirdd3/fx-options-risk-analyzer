# FX Options Risk Analyzer

A Python-based tool for pricing European FX options and simulating worst-case portfolio scenarios using the Garman-Kohlhagen model.

Built as the final capstone project for **OMSBA 5061: Programming I for Business** at Seattle University (Spring 2025).

---

## What It Does

This tool takes a portfolio of foreign exchange positions (spot holdings and options) and stress-tests them across a range of market scenarios to identify the worst possible overnight loss. It answers the question every risk desk cares about: *"How bad could tomorrow morning be?"*

**Core functionality:**
- Prices European FX call and put options using the **Garman-Kohlhagen model** (the FX extension of Black-Scholes)
- Loads portfolio data from CSV (spot positions, option positions, exchange rates, volatilities, interest rates)
- Simulates profit/loss across all combinations of -3, 0, and +3 standard deviation moves per currency
- Ranks scenarios by total loss and extremeness
- Visualizes the worst-case scenario with a detailed bar chart showing per-currency impact

---

## How It Works

The Garman-Kohlhagen model extends Black-Scholes to account for two interest rates (domestic and foreign), making it suitable for pricing currency options. The scenario engine then:

1. Loads the portfolio and market data from a CSV file
2. Generates every possible combination of standard deviation moves across all currencies
3. Reprices the entire portfolio under each scenario
4. Identifies the worst-case loss and visualizes the breakdown

---

## Project Structure

```
fx-options-risk-analyzer/
├── README.md
├── datatranslator_finalproject.py    # Main script with all classes and functions
└── pf_test1_currency_data.csv        # Sample portfolio data (required for demo)
```

---

## Key Classes

| Class | Purpose |
|-------|---------|
| `FxPosition` | Represents a spot FX holding in a given currency |
| `FxOption` | Represents a European-style FX option (call or put) |
| `Scenario` | Runs profit/loss simulations across all market move combinations |

---

## Tech Stack

- **Python** (core logic, OOP)
- **pandas** (data loading and manipulation)
- **matplotlib** (visualization)
- **scipy.stats** (normal distribution for option pricing)

---

## How to Run

```bash
python datatranslator_finalproject.py
```

Make sure `pf_test1_currency_data.csv` is in the same directory.

---

## Sample Output

The tool identifies the worst overnight scenario and produces a bar chart showing the loss per currency, including the standard deviation move that caused it.

---

## Author

**Ruman Sidhu**  
MS in Data Science, Seattle University  
[GitHub](https://github.com/simplyyweirdd3) · [Email](mailto:rsidhu2@seattleu.edu)
