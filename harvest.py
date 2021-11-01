import os
import json
import glob
import time


TRACKER_RADER_PATH = os.getenv('TRACKER_RADER_PATH', 'tracker-rader')

NONBLOCKING_CATEGORIES = set(["CDN", "Online Payment", "SSO"])
HARDBLOCK_CATEGORIES = set(['Malware', 'Obscure Ownership', 'Unknown High Risk Behavior'])
ADS_ONLY_CATEGORIES = set(["Ad Motivated Tracking","Ad Fraud","Advertising","Analytics","Audience Measurement", "Action Pixels", "Third-Party Analytics Marketing", "Session Replay"])

COUNT = [0]

def add_blocks(results, data, constrained):
    domain = data['domain']
    owner = data['owner']
    resources = data['resources']

    obj = {}
    if not results.get(domain):
        obj['owner'] = {}
        obj['rules'] = set([])
        obj['hardblock'] = False
        results[domain] = obj

    if not results[domain]['owner'] and owner:
        results[domain]['owner'] = owner

    for r in data['resources']:
        if constrained:
            if r['fingerprinting'] >= 1 or r['cookies'] > 0:
                results[domain]['rules'].add(r['rule'])
                COUNT[0] += 1
        else:
            results[domain]['rules'].add(r['rule'])
            # print('Hardblocked', data['domain'])
            COUNT[0] += 1

    if not constrained:
        results[domain]['hardblock'] = True

    if not results[domain]['rules']:
        del results[domain]


def shorten_rules(results):
    '''
    Shortens hardblock rules and remove duplicates
    '''
    for domain, value in results.items():
        if not value['owner']:
            value['hardblock'] = True

        if value['hardblock']:
            results[domain]['rules'] = set(["\\.".join(domain.split("."))])

        results[domain]['rules'] = list(results[domain]['rules'])


def main():
    start = time.time()

    filesnames = glob.glob(f"{TRACKER_RADER_PATH}/domains/*/*.json")

    results = dict({})
    for filename in filesnames:
        with open(filename) as file:
            data = json.load(file)

            block_conditions = [
                HARDBLOCK_CATEGORIES.intersection(data['categories'])
            ]
            if any(block_conditions):
                # results.append(data['domain'])
                add_blocks(results, data, False)
                continue

            skip_conditions = [
                NONBLOCKING_CATEGORIES.intersection(data['categories']),
                data['prevalence'] < 0.005,
            ]
            if any(skip_conditions):
                continue

            if data['categories'] and not set(data['categories']).difference(ADS_ONLY_CATEGORIES):
                add_blocks(results, data, False)
                continue

            add_blocks(results, data, True)

    shorten_rules(results)
    with open('block.json', 'w') as f:
        result_json = json.dumps(results, indent=2, sort_keys=True)
        f.write(result_json)

    end = time.time()

    count = 0
    for _,value in results.items():
        count += len(value['rules'])
    # print('Stats:', len(results.keys()), COUNT[0], count)
    print(f"Stats:\n domains={len(results.keys())}, found={COUNT[0]} filtered={count}")
    print(f"Time Elapsed: {end - start}")
    print('done.')

if __name__ == "__main__":
    main()