
import os
import time
import traceback
from datetime import datetime
from decimal import Decimal

from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv
from pysdk.grvt_ccxt_logging_selector import logger
from pysdk.grvt_ccxt_test_utils import validate_return_values



def show_derisk_mm_ratios(api: GrvtCcxt, keyword: str = "NOW") -> None:
    """Show the current derisking market making ratios."""
    FN = "show_derisk_mm_ratios"
    acc_summary = api.get_account_summary(type="sub-account")
    maintenance_margin = acc_summary.get("maintenance_margin")
    derisk_margin = acc_summary.get("derisk_margin")
    derisk_ratio = acc_summary.get("derisk_to_maintenance_margin_ratio")
    logger.info(f"{FN} {keyword} {maintenance_margin=}")
    logger.info(f"{FN} {keyword} {derisk_margin=}")
    logger.info(f"{FN} {keyword} {derisk_ratio=}")
    logger.info(f"sub-account summary:\n{acc_summary}")

def set_derisk_mm_ratio(api: GrvtCcxt, ratio: str = "2.0") -> None:
    """Set the derisking market making ratio."""
    FN = f"set_derisk_mm_ratio {ratio=}"
    logger.info(f"{FN} START")
    show_derisk_mm_ratios(api, "BEFORE")
    api.set_derisk_mm_ratio(ratio)
    show_derisk_mm_ratios(api, "AFTER")

def test_grvt_ccxt():
    params = {
        "api_key": os.getenv("GRVT_API_KEY"),
        "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
        "private_key": os.getenv("GRVT_PRIVATE_KEY"),
    }
    env = GrvtEnv(os.getenv("GRVT_ENV", "testnet"))
    test_api = GrvtCcxt(env, logger, parameters=params, order_book_ccxt_format=True)
    show_derisk_mm_ratios(test_api, "START")
    set_derisk_mm_ratio(test_api, ratio="2.0")


if __name__ == "__main__":
    test_grvt_ccxt()
