# simple.py
import pandas as pd
import numpy as np
from .bucket import assign_state
from collections import defaultdict

STATES = ["C0", "C1", "C2", "C3", "C4", "C5", "WO"]

# Step 1: Read CSV
def read_csv(path):
    df = pd.read_csv(path)
    cols = ['account_id', 'as_of_date', 'dpd', 'balance', 'recovery_amt']
    df = df[cols]
    return df

# Step 2: Assign state
def assign_states(df):
    df = df.copy()
    df['state'] = df['dpd'].apply(assign_state)
    return df

# Step 3: Fit transition matrix
def fit_simple(df, lookback=24):
    # Only use the most recent 24 months
    df['as_of_date'] = pd.to_datetime(df['as_of_date'])
    recent_dates = sorted(df['as_of_date'].unique())[-lookback:]
    df = df[df['as_of_date'].isin(recent_dates)]
    df = assign_states(df)
    # Sort for transition detection
    df = df.sort_values(['account_id', 'as_of_date'])
    # Build transitions
    transitions = defaultdict(lambda: defaultdict(int))
    for acc_id, group in df.groupby('account_id'):
        prev_state = None
        for _, row in group.iterrows():
            state = row['state']
            if prev_state is not None:
                transitions[prev_state][state] += 1
            prev_state = state
    # Build matrix
    P = np.zeros((7,7))
    for i, s_from in enumerate(STATES):
        total = sum(transitions[s_from][s_to] for s_to in STATES)
        if total == 0:
            P[i] = np.zeros(7)
        else:
            for j, s_to in enumerate(STATES):
                P[i, j] = transitions[s_from][s_to] / total
    return P

# Step 4: Build c vector
def build_c_vector(df):
    df = assign_states(df)
    c = np.zeros(7)
    for i, state in enumerate(STATES):
        mean_recovery = df[df['state'] == state]['recovery_amt'].mean()
        c[i] = 0.0 if np.isnan(mean_recovery) else mean_recovery
    return c

# Step 5: Simulate cash
def simulate_cash(P, B0, c, H=12):
    """
    P: 7x7 transition matrix
    B0: initial state vector (length 7)
    c: mean recovery per state (length 7)
    H: forecast horizon (months)
    Returns: list of (month, expected_cash, expected_balance)
    """
    results = []
    B = B0.copy()
    for h in range(1, H+1):
        cash = float(np.dot(B, c))
        balance = float(np.sum(B))
        results.append((h, cash, balance))
        B = np.dot(B, P)
    return results

# Step 6: Write matrix
def write_matrix(P, path):
    import csv
    header = ["state"] + STATES
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i, s_from in enumerate(STATES):
            row = [s_from] + [f"{P[i, j]:.6f}" for j in range(7)]
            writer.writerow(row)

# Step 7: Write forecast
def write_forecast(curve, path):
    import csv
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["month", "expected_cash", "expected_balance"])
        for month, cash, balance in curve:
            writer.writerow([month, f"{cash:.2f}", f"{balance:.2f}"])

# Helper: Get initial state vector
def get_B0(df):
    # Use the most recent as_of_date
    df = assign_states(df)
    last_date = df['as_of_date'].max()
    last = df[df['as_of_date'] == last_date]
    B0 = np.zeros(7)
    for i, state in enumerate(STATES):
        B0[i] = last[last['state'] == state]['balance'].sum()
    return B0

# Step 8: Validate (stub)
def validate_simple(df, P, c):
    pass

def run_simple_mode(input_path, forecast_path, matrix_path, validation_path):
    df = read_csv(input_path)
    P = fit_simple(df)
    c = build_c_vector(df)
    B0 = get_B0(df)
    curve = simulate_cash(P, B0, c)
    write_matrix(P, matrix_path)
    write_forecast(curve, forecast_path)
    print(f"Wrote transition matrix to {matrix_path}")
    print(f"Wrote forecast to {forecast_path}")
    # TODO: validate and write validation.json 