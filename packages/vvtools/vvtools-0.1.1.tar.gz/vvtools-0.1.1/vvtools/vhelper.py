import math
import subprocess
import time
from pathlib import Path

def ceil_to_decimal_place(value, decimals):
    factor = 10**decimals
    return math.ceil(value * factor) / factor

def members_to_string(prefix, members_dict, use_linefeed=False):
    lst = []
    for key, value in members_dict.items():
        if hasattr(value, "to_string") and callable(value.to_string):
            lst.append(f"{key} = {value.to_string()}")
        else:
            lst.append(f"{key} = {value}")

    if use_linefeed:
        return prefix + f"\n{prefix}".join(lst)
    else:
        return prefix + f", ".join(lst)

def get_git_info():
    """
    Retrieves the current Git commit hash, message, and branch name.

    Returns:
        dict: A dictionary containing the branch name, commit hash, and commit message.
    """
    try:
        # Get the current branch name
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()

        # Get the current commit hash
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

        # Get the commit message
        commit_message = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], text=True).strip()

        return {
            "branch_name": branch_name,
            "commit_hash": commit_hash,
            "commit_message": commit_message,
        }
    except subprocess.CalledProcessError as e:
        print(f"Error while fetching Git info: {e}")
        return {
            "branch_name": "",
            "commit_hash": "",
            "commit_message": "",
        }

def start_measure():
    return time.perf_counter_ns()

def get_elapsed_ms(start_counter) -> float:
    _t_end = time.perf_counter_ns()
    _t_elap_ms = (_t_end - start_counter) * 1e-6
    return _t_elap_ms

def get_cumulative_mean(mean, val, n, round_at=2) -> float:
    if n == 0:
        return 0
    mean = ((n - 1) * mean + val) / n
    return round(mean, round_at)

def to_absolute_path(path: str) -> str:
    return str(Path(path).expanduser().resolve())