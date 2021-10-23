import os
import json
import glob


TRACKER_RADER_PATH = os.getenv('TRACKER_RADER_PATH', 'tracker-rader')

NONBLOCKING_CATEGORIES = set(["CDN", "Online Payment", "SSO"])
HARDBLOCK_CATEGORIES = set(['Malware', 'Obscure Ownership', 'Unknown High Risk Behavior'])
ADS_ONLY_CATEGORIES = set(["Ad Motivated Tracking", "Advertising","Analytics","Audience Measurement", "Action Pixels", "Third-Party Analytics Marketing"])

COUNT = [0]

def add_blocks(results, data, constrained):
    domain = data['domain']
    owner = data['owner']
    resources = data['resources']

    obj = {}
    if not results.get(domain):
        obj['owner'] = {}
        obj['rules'] = []
        obj['hardblock'] = False
        results[domain] = obj

    if not results[domain]['owner'] and owner:
        results[domain]['owner'] = owner

    for r in data['resources']:
        if constrained:
            if r['fingerprinting'] >= 1 or r['cookies'] > 0:
                results[domain]['rules'].append(r['rule'])
                COUNT[0] += 1
        else:
            results[domain]['rules'].append(r['rule'])
            print('Hardblocked', data['domain'])
            COUNT[0] += 1

    if not constrained:
        results[domain]['hardblock'] = True

    if not results[domain]['rules']:
        del results[domain]


def shorten_hardblock_rules(results):
    for domain, value in results.items():
        if value['hardblock']:
            results[domain]['rules'] = ["\\.".join(domain.split("."))]


def main():
    filesnames = glob.glob(f"{TRACKER_RADER_PATH}/domains/*/*.json")

    count = 0
    # results = []
    results = dict({})
    for filename in filesnames:
        with open(filename) as file:
            data = json.load(file)

            block_conditions = [
                HARDBLOCK_CATEGORIES.intersection(data['categories']),
                data['categories'] and not set(data['categories']).difference(ADS_ONLY_CATEGORIES)
            ]
            if any(block_conditions):
                # results.append(data['domain'])
                add_blocks(results, data, False)
                continue

            skip_conditions = [
                NONBLOCKING_CATEGORIES.intersection(data['categories']),
                data['prevalence'] < 0.01,
            ]
            if any(skip_conditions):
                # print(data['domain'])
                continue

            add_blocks(results, data, True)

    shorten_hardblock_rules(results)
    with open('block.json', 'w') as f:
        result_json = json.dumps(results, indent=2, sort_keys=True)
        f.write(result_json)

    print('Stats:', len(results.keys()), COUNT[0])
    print('done.')

if __name__ == "__main__":
    main()