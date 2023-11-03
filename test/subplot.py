import argparse
import csv
import json
import os

from matplotlib import pyplot as plt


def gen_linestyle():
    ls = ['-', '-.', '--', ':']
    i = 0
    while True:
        yield ls[i]
        i = (i + 1) % len(ls)


iter_linestyle = gen_linestyle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = 'plot relation between the rank and recall'
    parser.add_argument(
        '-i', '--input',
        help='input data folders(str)',
        dest='in_dirs',
        type=str,
        default=None
    )
    parser.add_argument(
        '-l', '--legend',
        help='plot legend for each folders',
        dest='legends',
        type=str,
        default=None
    )
    parser.add_argument(
        '-k', '--topk',
        help='top k',
        dest='k',
        type=int,
        default=100
    )
    parser.add_argument(
        '-o', '--output',
        help='top k',
        dest='o',
        type=str,
        default=None
    )
    args = parser.parse_args()
    assert args.in_dirs is not None
    assert args.legends is not None
    paths = args.in_dirs.split(',')
    legends = args.legends.split(',')
    assert len(paths) == len(legends)

    cases = dict()
    cases_path = './cases'
    for fn in os.listdir(cases_path):
        fn = os.path.join(cases_path, fn)
        with open(fn, 'r') as f:
            case = json.load(f)
            cases[case['source'][0]['address']] = case

    ranks = dict()
    for i, path in enumerate(paths):
        ranks[legends[i]] = dict()
        for source in cases.keys():
            rank = list()
            fn = os.path.join(path, 'importance', '%s.csv' % source)
            with open(fn, 'r') as f:
                reader = csv.reader(f)
                _ = next(reader)
                for row in reader:
                    rank.append(dict(
                        node=row[0],
                        rank=float(row[1])
                    ))
            rank.sort(key=lambda x: x['rank'], reverse=True)
            ranks[legends[i]][source] = rank

    targets = dict()
    for source, case in cases.items():
        _targets = [target['address'] for target in case['target']]
        targets[source] = set(_targets)

    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    index = -1
    for source, case in cases.items():
        if index+1 == len(axes.ravel()):
            continue
        ax = axes.ravel()[index+1]
        index += 1
        for legend, rank in ranks.items():
            recalls = [0 for _ in range(args.k)]
            recall = 0
            target_cnt = 0
            for i in range(len(recalls)):
                if len(rank[source]) <= i:
                    recalls[i] = recall
                    continue
                if rank[source][i]['node'] in targets[source]:
                    target_cnt += 1
                recall = target_cnt / len(targets[source])
                recalls[i] = recall
            ax.plot(recalls, linestyle=next(iter_linestyle), linewidth=3.0)
            ax.legend(legends, prop={'size': 8})
            ax.set_title(case['name'], fontsize=8)
            # ax.xlabel('Top N', fontsize=20)
            # ax.ylabel('Average Recall', fontsize=20)

    # plt.tick_params(labelsize=17)
    # plt.grid()
    plt.tight_layout()
    plt.show()
    plt.savefig(args.o)
