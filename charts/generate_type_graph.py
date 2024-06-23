#!/usr/bin/env python3

import json
import argparse
import hashlib
import sys
import os
from pathlib import Path
import re

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input', nargs='+', help='')
    args = parser.parse_args()

    cookie = Cookie()

    nodes = dict()

    for input_path in args.input:
        content = read_json_file(input_path)
        handleDeclarations(content['rootDeclarations'], cookie, nodes, None)


    graph = dict()

    print("""flowchart LR
""")

    export_nodes(nodes, cookie)

    for tail_id in sorted(cookie.references):
        if tail_id not in cookie.declaration_for_usr: continue
        for head_id in sorted(cookie.references[tail_id]):
            if tail_id == head_id or head_id not in cookie.declaration_for_usr: continue
            print(f'{identifier(tail_id)} --> {identifier(head_id)}')

    print("")


def export_nodes(node, cookie):
    for canonical_usr in node:
        if canonical_usr not in cookie.declaration_for_usr:
            print("--", canonical_usr)
            continue
        declaration = cookie.declaration_for_usr[canonical_usr]
        label = nodeLabel(declaration)
        subnodes = node[canonical_usr]
        if len(subnodes) > 0:
            print(f'subgraph {identifier(canonical_usr)}[{label}]')
            export_nodes(subnodes, cookie)
            print('end')
        else:
            print(f'{identifier(canonical_usr)}[{label}]')



skipped_locations = [
]

kind_labels = {
    # "associatedtype": "associatedtype",
    "class": "class",
    "enum": "enum",
    # "enumelement": "enumelement",
    "extension": "extension",
    "extension.class": "extension",
    "extension.enum": "extension",
    "extension.protocol": "extension",
    "extension.struct": "extension",
    # "function.accessor.address": "function.accessor.address",
    # "function.accessor.didset": "function.accessor.didset",
    # "function.accessor.getter": "function.accessor.getter",
    # "function.accessor.mutableaddress": "function.accessor.mutableaddress",
    # "function.accessor.setter": "function.accessor.setter",
    # "function.accessor.willset": "function.accessor.willset",
    # "function.accessor.read": "function.accessor.read",
    # "function.accessor.modify": "function.accessor.modify",
    # "function.accessor.init": "function.accessor.init",
    # "function.constructor": "function.constructor",
    # "function.destructor": "function.destructor",
    # "function.free": "function.free",
    # "function.method.class": "function.method.class",
    # "function.method.instance": "function.method.instance",
    # "function.method.static": "function.method.static",
    # "function.operator": "function.operator",
    # "function.operator.infix": "function.operator.infix",
    # "function.operator.postfix": "function.operator.postfix",
    # "function.operator.prefix": "function.operator.prefix",
    # "function.subscript": "function.subscript",
    # "generic_type_param": "generic_type_param",
    # "module": "module",
    # "precedencegroup": "precedencegroup",
    "protocol": "protocol",
    "struct": "struct",
    "typealias": "typealias",
    # "var.class": "var.class",
    # "var.global": "var.global",
    # "var.instance": "var.instance",
    # "var.local": "var.local",
    # "var.parameter": "var.parameter",
    # "var.static": "var.static",
    # "macro": "macro",
}

def handleDeclarations(declarations, cookie, cluster, canonical_usr):
    for declaration in declarations:
        handleDeclaration(declaration, cookie, cluster, canonical_usr)

def handleDeclaration(declaration, cookie, cluster, canonical_usr):
    for usr in declaration['usrs']:
        cookie.canonical_usr_for_usr[usr] = canonical_usr

    if declaration["kind"] in kind_labels and not declaration["name"].startswith("$"):
        canonical_usr = declaration['usrs'][0]
        cookie.declaration_for_usr[canonical_usr] = declaration

        subcluster = dict()
        cluster[canonical_usr] = subcluster
        cluster = subcluster
        cookie.references[canonical_usr] = set()

    if canonical_usr:
        for reference in declaration["references"] + declaration["immediateInheritedTypeReferences"]:
            cookie.references[canonical_usr].add(reference)

    handleDeclarations(declaration['declarations'], cookie, cluster, canonical_usr)

def json_dumps(obj, indent=""):
    string = json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, default=json_encode_value)
    string = re.sub("^", indent, string, flags=re.MULTILINE)
    return string

def json_encode_value(value):
    if isinstance(value, set):
        return list(sorted(value))
    else:
        raise TypeError(f"Object of type {type(value)} is not serializable")

class Cookie:
    declaration_for_usr = dict()
    canonical_usr_for_usr = dict()
    references = dict()


def nodeLabel(declaration):
    label = kind_labels[declaration["kind"]] + " " + declaration["name"]
    return label


def identifier(value):
    value = re.sub(r'[^A-Za-z0-9]', '_', value)
    return value
    sha256 = hashlib.sha256()
    sha256.update(value.encode('utf-8'))
    return 'n'+sha256.hexdigest()[:8]

def read_json_file(path):
    with open(path, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    main()
