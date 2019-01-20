
import CONSTANTS
import CONFIG
import playground
import probe_get_latest_trains

def run_sncf_parser():
    probe_get_latest_trains.main()
    playground.main()


run_sncf_parser()
