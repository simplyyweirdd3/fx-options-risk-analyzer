from datetime import date, timedelta
from itertools import product
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
from scipy.stats import norm

def fx_option_price(spot, strike, t, vol, r_domestic, r_foreign, call_put):
    """Calculates the price of a European FX option using the Garman-Kohlhagen model."""
    if t <= 0 or vol <= 0 or spot <= 0 or strike <= 0:
        return 0.0
    d1 = (math.log(spot / strike) + (r_domestic - r_foreign + 0.5 * vol**2) * t) / (vol * math.sqrt(t))
    d2 = d1 - vol * math.sqrt(t)
    if call_put.lower() == 'call':
        return spot * math.exp(-r_foreign * t) * norm.cdf(d1) - strike * math.exp(-r_domestic * t) * norm.cdf(d2)
    else:
        return strike * math.exp(-r_domestic * t) * norm.cdf(-d2) - spot * math.exp(-r_foreign * t) * norm.cdf(-d1)

class FxPosition:
    """Represents a spot FX position for a specific currency."""
    def __init__(self, quantity, currency):
        self.quantity = quantity
        self.currency = currency.upper()

    def price(self, spot):
        """Returns the value of the position at the given spot rate."""
        return self.quantity * spot

class FxOption:
    """Represents a European-style FX option (call or put)."""
    def __init__(self, quantity, call_put, strike, expiration, currency):
        self.quantity = quantity
        self.call_put = call_put
        self.strike = strike
        self.expiration = expiration
        self.currency = currency.upper()

    def price(self, spot, volatility, domestic_rate, foreign_rate):
        """Calculates the option value based on current market parameters."""
        t = (self.expiration - date.today()).days / 365
        if t <= 0 or self.quantity == 0:
            return 0.0
        return self.quantity * fx_option_price(spot, self.strike, t, volatility, domestic_rate, foreign_rate, self.call_put)

class Scenario:
    """Simulates profit/loss for a portfolio across currency move scenarios."""
    def __init__(self, positions, spots, vols, rates):
        self.positions = positions
        self.spots = spots
        self.vols = vols
        self.rates = rates

    def profit(self, moves):
        """Calculates the profit/loss given a move (in std dev) per currency."""
        new_spots = {ccy: self.spots[ccy] * (1 + self.vols[ccy] * moves.get(ccy, 0)) for ccy in self.spots}
        old_val = self.compute_valuation(self.spots)
        new_val = self.compute_valuation(new_spots)
        profits = {ccy: new_val.get(ccy, 0) - old_val.get(ccy, 0) for ccy in self.spots}
        profits['Total'] = sum(profits.values())
        return profits

    def compute_valuation(self, spots):
        """Computes the total value of all positions at given spot prices."""
        result = {}
        for p in self.positions:
            if isinstance(p, FxPosition):
                val = p.price(spots[p.currency])
            else:
                val = p.price(spots[p.currency], self.vols[p.currency], self.rates['USD'], self.rates[p.currency])
            result[p.currency] = result.get(p.currency, 0) + val
        return result

def load_data(filename):
    """Reads the portfolio CSV file and returns positions, spots, vols, and rates."""
    df = pd.read_csv(filename, sep='\t' if '\t' in open(filename).readline() else ',')
    df.columns = df.columns.str.strip().str.lower()

    positions = []
    spots = {}
    vols = {}
    rates = {}

    for _, row in df.iterrows():
        ccy = row['currency'].upper()
        spot = float(row['spot exchange rate'])
        vol = float(row['3-month volatility (annualized)'])
        rate = float(row['3-month interest rate (annualized)'])
        spots[ccy] = spot
        vols[ccy] = vol
        rates[ccy] = rate

        if row.get('spot position', 0):
            positions.append(FxPosition(float(row['spot position']), ccy))

        if row.get('call option position', 0):
            positions.append(FxOption(float(row['call option position']), 'call', spot, date.today() + timedelta(days=90), ccy))

        if row.get('put option position', 0):
            positions.append(FxOption(float(row['put option position']), 'put', spot, date.today() + timedelta(days=90), ccy))

    rates['USD'] = 0.03
    return positions, spots, vols, rates

def extremeness(moves):
    """Returns a score for how extreme a scenario is (sum of absolute std dev moves)."""
    return sum(abs(x) for x in moves.values())

def plot_scenario(profits, moves):
    """Generates a bar chart showing profit/loss per currency under a scenario."""
    currencies = [k for k in profits if k != 'Total']
    values = [profits[k] for k in currencies]
    bars = plt.bar(currencies, values, color=plt.cm.tab10.colors[:len(currencies)])
    plt.title(f"Worst overnight scenario: loss of ${-profits['Total']/1e9:.2f} bln")
    plt.ylabel("Profit USD")
    plt.xlabel("Currency")
    plt.xticks(rotation=45)
    for bar, ccy in zip(bars, currencies):
        val = profits[ccy]
        label = f"Loss of ${-val/1e6:.2f}mm due to {moves[ccy]} std dev move in {ccy}"
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), label,
                 ha='center', va='bottom' if val < 0 else 'top', rotation=90, fontsize=8)
    plt.tight_layout()
    plt.show()

def produce_report(file):
    """Loads portfolio data, runs all scenarios, and plots the worst-case result."""
    positions, spots, vols, rates = load_data(file)
    scenario = Scenario(positions, spots, vols, rates)
    move_choices = [-3, 0, 3]
    currencies = list(spots.keys())
    results = []

    for moves in product(move_choices, repeat=len(currencies)):
        move_dict = dict(zip(currencies, moves))
        profits = scenario.profit(move_dict)
        results.append((profits['Total'], extremeness(move_dict), move_dict, profits))

    results.sort(key=lambda x: (x[0], x[1]))
    worst_total, _, worst_moves, worst_profits = results[0]
    print(f"Worst loss: ${-worst_total / 1e9:.6f} billion with moves {worst_moves}")
    plot_scenario(worst_profits, worst_moves)

# Example usage:
if __name__ == '__main__':
    produce_report('pf_test1_currency_data.csv')