"""
Test RPKs with 1 resource each of all the different resource types have been saved in a folder.
Point this script to a folder and it'll extract the type names associated with each rpk test file

(uses 'safe' base64 encoding due to filename reserved character limitations:
https://docs.python.org/3/library/base64.html#base64.urlsafe_b64encode)
"""
import glob
import sys
import os.path
import subprocess
import json

from base64 import urlsafe_b64decode

"""
Gets type name from the base64 encoding in a filename, assumes format `typenum#-<b64encoded typename>.rpk`
"""
def get_type_name(filename: str) -> str:
    type_name_start = filename.find('-')
    if type_name_start == -1:
        print('Invalid filename format: {}'.format(filename))
        sys.exit(1)

    return urlsafe_b64decode(filename[type_name_start + 1:].replace('.rpk', '')).decode('utf8')


"""
Return a list of RPK type names and file paths:
[
    (type_name1, rpk_file_path1),
    (type_name2, rpk_filepath2),
    ...
]
"""
def build_test_rpks_list(folder_path: str) -> list:
    ret = []
    # get all files starting with typenum and ending with .rpk from folder
    for f in glob.glob(os.path.join(folder_path, 'typenum*.rpk')):
        ret.append((get_type_name(f), f))  # Get type name from b64 encoded filename, pair with its path and add to results
    return ret

"""
Invoke parser process and pass it a file to grab the first resource inside's type id.
"""
def get_type_id(parser_path, file_path):
    cmd = 'python {} --json -f "{}"'.format(os.path.join(parser_path, 'main.py'), file_path)
    #print(cmd)

    try:
        subprocess_output = subprocess.run(cmd, capture_output=True)
        parsed_json = json.loads(subprocess_output.stderr)
        resources = parsed_json['resources']
        if not len(resources):
            print("The parser didn't return any resources in its JSON. Exiting.")
            return

        return resources[0]['type']

    except json.decoder.JSONDecodeError as e:
        print('Parser did not return valid JSON.')
        return
    except Exception as e:
        print(f'Unknown error running parser `{cmd}`: {e}')
        return

"""
Print which RPKs failed to parse if any at the end
"""
def print_errors(errors):
    if not len(errors):
        return
    print('Parsing issues:')
    for err in errors:
        print(err)
    print()

"""
Print success message + write json results to file
"""
def write_results_and_json(output):
    json_path = 'debug/type_ids.json'
    print(f'Writing successful results to `{json_path}` and exiting.')
    with open(json_path, 'w') as f:
        json.dump(output, f)


def main():
    if len(sys.argv) != 3:
        print(f'Usage: python3 {sys.argv[0]} <parser folder> <rpk folder>')
        sys.exit(1)

    n = 0
    output = []
    errors = []

    ret = build_test_rpks_list(sys.argv[2])

    for type_name, type_path in ret:
        n += 1
        print(f'Getting type #{n} id... `{type_name}`: ', end='')
        sys.stdout.flush()

        if type_id := get_type_id(sys.argv[1], type_path):
             print(type_id)
             output.append((type_name, type_id))
        else:
            errors.append(f'Parser could not read type id ({type_name}: {type_path}).')
            continue

    print_errors(errors)
    write_results_and_json(output)

if __name__ == '__main__':
    main()