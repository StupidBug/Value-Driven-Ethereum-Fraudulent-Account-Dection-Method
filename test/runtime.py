import argparse
from datetime import datetime


def calculate_average_time(filename):
    with open(filename, 'r') as f:
        log_data = f.read()
    # Split log data into lines
    log_lines = log_data.strip().split('\n')
    # Create a dictionary to store spider runtimes
    spider_runtimes = list()
    start_time = list()

    for line in log_lines:
        if "Spider opened" in line:
            start_time.append(datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S"))
        elif "Closing spider (finished)" in line:
            end_time = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
            runtime = (end_time - start_time.pop()).total_seconds() / 3600
            spider_runtimes.append(runtime)

    return sum(spider_runtimes) / len(spider_runtimes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = 'export cases info'
    parser.add_argument(
        '-l', '--logfile',
        help='logfile which need to calcu time',
        dest='logfile',
        type=str,
        default=None,
    )
    args = parser.parse_args()
    print(calculate_average_time(args.logfile))
