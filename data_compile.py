import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--minified', action='store_true')

def main():
    args = parser.parse_args()

    exceptions = {}
    block_list = {}
    with open("exceptions.json") as file:
        exceptions = json.load(file)
    with open("block.json") as file:
        block_list = json.load(file)

    for domain, rulelist in exceptions.items():
        if not rulelist:
            del block_list[domain]
            continue
        
        for exception_rule in rulelist:
            matches = []
            for rule in block_list[domain]["rules"]:
                if exception_rule in rule:
                    matches.append(rule)
        
            for match in matches:
                block_list[domain]["rules"].remove(match)
            
            block_list[domain]["rules"].append(exception_rule)

    domain_regex = "|".join(block_list.keys())
    domain_regex = "\\.".join(domain_regex.split("."))

    compiled = {}
    compiled["domainRegex"] = domain_regex

    compiled_domains = {}
    for domain, value in block_list.items():
        compiled_domains[domain] = {}
        compiled_domains[domain]['hardblock'] = value['hardblock']

        compiled_domains[domain]["owner"] = ""
        if value["owner"]:
            compiled_domains[domain]["owner"] = value["owner"]["displayName"]

        compiled_domains[domain]["rules"] = "|".join(value["rules"])

    compiled["domains"] = compiled_domains

    with open('block.compiled.json', 'w') as f:
        result_json = json.dumps(compiled, indent=2, sort_keys=True)
        f.write(result_json)

    if args.minified:
        print("producing minified json...")
        with open('block.compiled.minified.json', "w") as f:
            result_json = json.dumps(compiled, sort_keys=True, separators=(',', ':'))
            f.write(result_json)

    print("done.")

if __name__ == "__main__":
    main()


