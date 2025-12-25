import pandas as pd

def _safe_str(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()

def _safe_int(x, default: int | None = None) -> int | None:
    if pd.isna(x) or x == "":
        return default
    try:
        return int(x)
    except Exception:
        try:
            return int(float(x))
        except Exception:
            return default

def _limit(df: pd.DataFrame, n: int | None) -> pd.DataFrame:
    return df if (n is None or len(df) <= n) else df.head(n)
