import pandas as pd
import numpy as np
from typing import List, Callable, Optional, Union

def assign_state(dpd: int, bucket_grid: List[int], bucket_labels: List[str]) -> str:
    for i, bound in enumerate(bucket_grid):
        if dpd < bound:
            return bucket_labels[i]
    return bucket_labels[-1]

def assign_states(df: pd.DataFrame, bucket_grid: List[int], bucket_labels: List[str]) -> pd.DataFrame:
    df = df.copy()
    df['state'] = df['dpd'].apply(lambda x: assign_state(x, bucket_grid, bucket_labels))
    return df

def fit_transition_matrix(
    df: pd.DataFrame,
    bucket_labels: List[str],
    lookback: int = 24
) -> np.ndarray:
    df['as_of_date'] = pd.to_datetime(df['as_of_date'])
    recent_dates = sorted(df['as_of_date'].unique())[-lookback:]
    df = df[df['as_of_date'].isin(recent_dates)]
    df = df.sort_values(['account_id', 'as_of_date'])
    n = len(bucket_labels)
    transitions = np.zeros((n, n))
    for acc_id, group in df.groupby('account_id'):
        prev_state = None
        for _, row in group.iterrows():
            state = row['state']
            if prev_state is not None:
                i = bucket_labels.index(prev_state)
                j = bucket_labels.index(state)
                transitions[i, j] += 1
            prev_state = state
    # Normalize rows
    row_sums = transitions.sum(axis=1, keepdims=True)
    P = np.divide(transitions, row_sums, out=np.zeros_like(transitions), where=row_sums!=0)
    return P

def build_recovery_vector(
    df: pd.DataFrame,
    bucket_labels: List[str],
    recovery_func: Callable = np.mean
) -> np.ndarray:
    c = np.zeros(len(bucket_labels))
    for i, state in enumerate(bucket_labels):
        vals = df[df['state'] == state]['recovery_amt']
        c[i] = recovery_func(vals) if not vals.empty else 0.0
    return c

def get_B0(df: pd.DataFrame, bucket_labels: List[str]) -> np.ndarray:
    last_date = df['as_of_date'].max()
    last = df[df['as_of_date'] == last_date]
    B0 = np.zeros(len(bucket_labels))
    for i, state in enumerate(bucket_labels):
        B0[i] = last[last['state'] == state]['balance'].sum()
    return B0

def simulate_cash(
    P: np.ndarray,
    B0: np.ndarray,
    c: np.ndarray,
    H: int = 12
) -> pd.DataFrame:
    results = []
    B = B0.copy()
    for h in range(1, H+1):
        cash = float(np.dot(B, c))
        balance = float(np.sum(B))
        results.append((h, cash, balance))
        B = np.dot(B, P)
    return pd.DataFrame(results, columns=['month', 'expected_cash', 'expected_balance'])

def run_forecast(
    data: Union[str, pd.DataFrame],
    bucket_grid: Optional[List[int]] = None,
    bucket_labels: Optional[List[str]] = None,
    lookback: int = 24,
    H: int = 12,
    recovery_func: Callable = np.mean
) -> tuple:
    if bucket_grid is None:
        bucket_grid = [30, 60, 90, 120, 150, 180]
    if bucket_labels is None:
        bucket_labels = ["C0", "C1", "C2", "C3", "C4", "C5", "WO"]
    if isinstance(data, str):
        df = pd.read_csv(data)
    else:
        df = data.copy()
    df = assign_states(df, bucket_grid, bucket_labels)
    P = fit_transition_matrix(df, bucket_labels, lookback)
    c = build_recovery_vector(df, bucket_labels, recovery_func)
    B0 = get_B0(df, bucket_labels)
    forecast_df = simulate_cash(P, B0, c, H)
    return forecast_df, P, c 