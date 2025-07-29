import logging

logging.basicConfig(
    filename="whole.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(action: str, detail: str = "", level: str = "info"):
    if level == "debug":
        logging.debug(f"{action} - {detail}")
    else:
        logging.info(f"{action} - {detail}")