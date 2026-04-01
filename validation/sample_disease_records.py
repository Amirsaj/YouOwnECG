"""
Sample PTB-XL records for specific cardiac conditions based on SCP codes.
Outputs a CSV with 10 randomly sampled records per condition for validation.
"""

import ast
import pandas as pd

DB_PATH = "/Users/amirsadjadtaleban/Documents/PTBXL/ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1/ptbxl_database.csv"
OUT_PATH = "/Users/amirsadjadtaleban/Documents/YouOwnECG/validation/disease_test_samples.csv"
SEED = 42

CONDITION_CODES = {
    "lbbb":           ["CLBBB"],
    "rbbb":           ["CRBBB"],
    "first_degree_avb": ["1AVB"],
    "lafb":           ["LAFB"],
    "wpw_pattern":    ["WPW"],
    "afib":           ["AFIB"],
    "lvh":            ["LVH"],
    "anterior_stemi": ["AMI", "ASMI"],
    "inferior_stemi": ["IMI", "ILMI", "IPLMI", "IPMI"],
    "lateral_stemi":  ["ALMI", "LMI"],
    "long_qt":        ["LNGQT"],
    "pericarditis":   ["PRC(S)"],
    "low_voltage":    ["LVOLT"],
}


def parse_scp(value):
    try:
        return ast.literal_eval(value)
    except Exception:
        return {}


def matches_condition(scp_dict, codes, threshold=50.0):
    return any(scp_dict.get(code, 0.0) >= threshold for code in codes)


def main():
    df = pd.read_csv(DB_PATH)
    df["scp_parsed"] = df["scp_codes"].apply(parse_scp)

    rows = []
    for condition, codes in CONDITION_CODES.items():
        mask = df["scp_parsed"].apply(lambda d: matches_condition(d, codes))
        matched = df[mask]
        total = len(matched)
        sample = matched.sample(n=min(10, total), random_state=SEED) if total > 0 else matched
        print(f"{condition:25s}: {total:5d} records found, sampled {len(sample)}")
        for _, row in sample.iterrows():
            rows.append({
                "ecg_id":    row["ecg_id"],
                "condition": condition,
                "scp_codes": row["scp_codes"],
                "filename_hr": row["filename_hr"],
            })

    out_df = pd.DataFrame(rows, columns=["ecg_id", "condition", "scp_codes", "filename_hr"])
    out_df.to_csv(OUT_PATH, index=False)
    print(f"\nSaved {len(out_df)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
