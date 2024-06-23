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
    parser.add_argument('--path-root', default='', help='')
    parser.add_argument('--cluster', action='store_true', help='')
    args = parser.parse_args()

    cookie = Cookie()

    for input_path in args.input:
        content = read_json_file(input_path)
        handleDeclarations(content['rootDeclarations'], cookie)


    graph = dict()

    for canonical_usr, declaration in cookie.declaration_for_usr.items():
        if nodeLabel(declaration, args.path_root) not in graph:
            graph[nodeLabel(declaration, args.path_root)] = set()

        for reference in declaration["references"] + declaration["immediateInheritedTypeReferences"]:
            if canonical_reference_usr := cookie.canonical_usr_for_usr.get(reference):
                referenced_declaration = cookie.declaration_for_usr[canonical_reference_usr]
                if nodeLabel(declaration, args.path_root) == nodeLabel(referenced_declaration, args.path_root): continue
                graph[nodeLabel(declaration, args.path_root)].add(nodeLabel(referenced_declaration, args.path_root))

    print("""digraph {
    rankdir = LR;
    node [ shape=rect, style=filled, color=white , pencolor=black];
    graph [bgcolor = "#00000010", color="#00000030"];
""")

    clusters = set()

    for label in sorted(graph):
        while len(label) > 0 and '/' in label:
            label = re.sub(r'/[^/]*$', '', label)
            clusters.add(label)

    for tail_id in sorted(graph):
        foo = tail_id.split('/')
        if args.cluster:
            node = foo.pop()
        else:
            node = tail_id

        if args.cluster:
            cluster_id = list()
            for moo in foo:
                cluster_id.append(identifier(moo))
                print(f'subgraph cluster_{"_".join(cluster_id)} {{ label="{moo}";')

        if tail_id not in clusters:
            label = re.sub(r'.folder$', '...', node)
            print(f'"{tail_id}" [label="{label}"];')

        if args.cluster:
            for moo in foo:
                print(f"}}")

    for tail_id in sorted(graph):
        for head_id in sorted(graph[tail_id]):
            if tail_id.startswith(head_id): continue
            # if head_id.startswith(tail_id): continue
            print(f'"{tail_id}" -> "{head_id}";')

    print("}")


skipped_locations = [
]

kind_labels = {
    "associatedtype": "associatedtype",
    "class": "class",
    "enum": "enum",
    "enumelement": "enumelement",
    "extension": "extension",
    "extension.class": "extension.class",
    "extension.enum": "extension.enum",
    "extension.protocol": "extension.protocol",
    "extension.struct": "extension.struct",
    "function.accessor.address": "function.accessor.address",
    "function.accessor.didset": "function.accessor.didset",
    "function.accessor.getter": "function.accessor.getter",
    "function.accessor.mutableaddress": "function.accessor.mutableaddress",
    "function.accessor.setter": "function.accessor.setter",
    "function.accessor.willset": "function.accessor.willset",
    "function.accessor.read": "function.accessor.read",
    "function.accessor.modify": "function.accessor.modify",
    "function.accessor.init": "function.accessor.init",
    "function.constructor": "function.constructor",
    "function.destructor": "function.destructor",
    "function.free": "function.free",
    "function.method.class": "function.method.class",
    "function.method.instance": "function.method.instance",
    "function.method.static": "function.method.static",
    "function.operator": "function.operator",
    "function.operator.infix": "function.operator.infix",
    "function.operator.postfix": "function.operator.postfix",
    "function.operator.prefix": "function.operator.prefix",
    "function.subscript": "function.subscript",
    "generic_type_param": "generic_type_param",
    "module": "module",
    "precedencegroup": "precedencegroup",
    "protocol": "protocol",
    "struct": "struct",
    "typealias": "typealias",
    "var.class": "var.class",
    "var.global": "var.global",
    "var.instance": "var.instance",
    "var.local": "var.local",
    "var.parameter": "var.parameter",
    "var.static": "var.static",
    "macro": "macro",
}

def handleDeclarations(declarations, cookie):
    for declaration in declarations:
        handleDeclaration(declaration, cookie)

def handleDeclaration(declaration, cookie):
    for skipped_location in skipped_locations:
        if skipped_location in declaration["location"]:
            return

    canonical_usr = declaration['usrs'][0]

    cookie.declaration_for_usr[canonical_usr] = declaration

    for usr in declaration['usrs']:
        cookie.canonical_usr_for_usr[usr] = canonical_usr
    handleDeclarations(declaration['declarations'], cookie)


class Cookie:
    declaration_for_usr = dict()
    canonical_usr_for_usr = dict()


def nodeLabel(declaration, pathRoot):
    label = declaration["location"].replace(pathRoot, '')
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
