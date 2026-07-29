import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Replace the logging setup and custom print with the new logger and discord alerter
old_logging_setup = """import logging
import sys

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/daily_execution.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def print(*args, **kwargs):
    msg = " ".join(str(a) for a in args)
    logging.info(msg)"""

new_logging_setup = """from utils.logger import logger
from utils.discord_alert import discord_alerter"""

content = content.replace(old_logging_setup, new_logging_setup)

# 2. Replace all remaining print( with logger.info(
content = re.sub(r'\bprint\(', 'logger.info(', content)

# 3. Fix exception handling to use logger.exception and discord alerts for failures
# Redis failure
content = content.replace(
    """        except Exception as e:
            logger.info(f"Redis initialization failed: {e}")""",
    """        except Exception as e:
            logger.exception(f"Redis initialization failed: {e}")
            discord_alerter.send_alert(f"🚨 **URGENT:** Redis initialization failed!\nError: `{e}`")"""
)

# Inference failure
content = content.replace(
    """                except Exception as e:
                    logger.info(f"Failed inference for {asset}: {e}")""",
    """                except Exception as e:
                    logger.exception(f"Failed inference for {asset}: {e}")
                    discord_alerter.send_alert(f"🚨 **WARNING:** Failed inference for {asset}!\nError: `{e}`")"""
)

# REDUCE order fill polling silent failure
content = content.replace(
    """                            except Exception:
                                pass""",
    """                            except Exception as e:
                                logger.warning(f"Error while polling for {asset} REDUCE order fill: {e}")"""
)

# Timeout market order cancel silent failure
content = content.replace(
    """                    except Exception:
                        pass""",
    """                    except Exception as e:
                        logger.warning(f"Failed to cancel un-filled portion of order {order_id}: {e}")"""
)

# Market close liquidation failure
content = content.replace(
    """            except Exception as e:
                logger.info(f"Failed to process market-close liquidation for {symbol}: {e}")""",
    """            except Exception as e:
                logger.exception(f"Failed to process market-close liquidation for {symbol}: {e}")
                discord_alerter.send_alert(f"🚨 **URGENT:** Failed to process market-close liquidation for {symbol}!\nError: `{e}`")"""
)

# Add Daily Summary at the end of execute_daily_loop
daily_loop_end_old = """        logger.info("Loop execution complete.")"""
daily_loop_end_new = """        logger.info("Loop execution complete.")
        
        summary_lines = ["📈 **Daily Execution Summary**"]
        if final_positions:
            for pos in final_positions:
                summary_lines.append(f"- {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price}")
        else:
            summary_lines.append("No open positions.")
            
        discord_alerter.send_alert("\\n".join(summary_lines))"""

content = content.replace(daily_loop_end_old, daily_loop_end_new)

with open("main.py", "w") as f:
    f.write(content)
