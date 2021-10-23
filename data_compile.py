import json


def main():
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

    with open('block-compiled.json', 'w') as f:
        result_json = json.dumps(block_list, indent=2, sort_keys=True)
        f.write(result_json)

    print("done.")

if __name__ == "__main__":
    main()


