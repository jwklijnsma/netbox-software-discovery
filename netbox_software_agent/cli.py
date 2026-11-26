import argparse, logging, time
from .config import Config
from .collectors import collect
from .client import send_report

def main():
    parser=argparse.ArgumentParser(description="NetBox Software Discovery agent")
    parser.add_argument("--once",action="store_true",help="Run discovery once and exit")
    parser.add_argument("--debug",action="store_true")
    args=parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    cfg=Config()
    while True:
        try:
            report=collect(cfg); result=send_report(cfg,report)
            logging.info("Reported %s software items for %s; matched=%s",result.get("accepted"),report["hostname"],result.get("matched_object"))
        except Exception as exc:
            logging.exception("Discovery/report failed: %s",exc)
        if args.once: break
        time.sleep(max(60,cfg.interval))

if __name__ == "__main__": main()
