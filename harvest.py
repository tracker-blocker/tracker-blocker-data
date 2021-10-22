import os
import json
import glob


TRACKER_RADER_PATH = os.getenv('TRACKER_RADER_PATH', 'tracker-rader')

NONBLOCKING_CATEGORIES = set(["CDN", "Online Payment", "SSO"])
HARDBLOCK_CATEGORIES = set(['Malware', 'Obscure Ownership', 'Unknown High Risk Behavior'])

def parse_content(content):
    data = json.loads(base64.b64decode(content))
    print(data['domain'])


def filter_data(data):
    pass


def main():
    filesnames = glob.glob(f"{TRACKER_RADER_PATH}/domains/*/*.json")

    count = 0
    results = []
    for filename in filesnames:
        with open(filename) as file:
            data = json.load(file)

            block_conditions = [
                HARDBLOCK_CATEGORIES.intersection(data['categories'])
            ]
            if any(block_conditions):
                results.append(data['domain'])
                count += 1
                continue

            skip_conditions = [
                NONBLOCKING_CATEGORIES.intersection(data['categories']),
                data['prevalence'] < 0.01,
            ]
            if any(skip_conditions):
                # print(data['domain'])
                continue

            for r in data['resources']:
                if r['fingerprinting'] >= 1:
                    results.append(data['domain'])
                    break

            count += 1
            # results.append(data['domain'])

    with open('block.txt', 'w') as f:
        for domain in results:
            f.write(domain+'\n')

    print('Stats:', len(filesnames), count)
    print('done.')

if __name__ == "__main__":
    main()