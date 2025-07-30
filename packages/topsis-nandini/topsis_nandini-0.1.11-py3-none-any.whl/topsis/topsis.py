# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def validate_inputs(data, weights, impacts):
    if len(weights) != len(impacts):
        raise ValueError("The number of weights must match the number of impacts.")

    if len(weights) != data.shape[1]:
        raise ValueError("Number of weights/impacts must match the number of criteria columns.")

    if not all(impact in ['+', '-'] for impact in impacts):
        raise ValueError("Impacts must be either '+' or '-'.")

def run_topsis_from_dataframe(df, weights, impacts):
    weights = list(map(float, weights))
    validate_inputs(df, weights, impacts)

    # Step 1: Normalize the decision matrix
    norm = df / np.sqrt((df**2).sum(axis=0))

    # Step 2: Multiply by weights
    weighted = norm * weights

    # Step 3: Determine ideal best and ideal worst
    impacts = np.array(impacts)
    ideal_best = np.where(impacts == '+', np.max(weighted, axis=0), np.min(weighted, axis=0))
    ideal_worst = np.where(impacts == '+', np.min(weighted, axis=0), np.max(weighted, axis=0))

    # Step 4: Calculate distances to ideal best and worst
    dist_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    # Step 5: Calculate TOPSIS score and rank
    scores = dist_worst / (dist_best + dist_worst)
    ranks = scores.argsort()[::-1] + 1

    return scores, ranks

def topsis(input_file, weights_str, impacts_str, output_file):
    data = pd.read_csv(input_file)
    if data.shape[1] < 3:
        raise ValueError("Input file must have at least 3 columns (identifier + 2 criteria columns).")

    df = data.iloc[:, 1:]

    # ✅ FIXED dtype validation (previous version was broken)
    if not all(np.issubdtype(dtype, np.number) for dtype in df.dtypes):
        raise ValueError("All criteria columns must be numeric.")

    weights = weights_str.split(',')
    impacts = impacts_str.split(',')

    scores, ranks = run_topsis_from_dataframe(df, weights, impacts)

    data['Topsis Score'] = scores
    data['Rank'] = ranks
    data.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
