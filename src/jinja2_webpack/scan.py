#!/usr/bin/env python

from __future__ import print_function

import argparse
import glob
import logging
import os
import sys

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2.visitor import NodeVisitor


class WebpackReferenceFinder(NodeVisitor):
    def __init__(self, reference_root, filter_name=None):
        self.assets = []
        self.directory = ''
        self.template = ''
        self.reference_root = reference_root
        self.filter_name = filter_name or 'webpack'

    def visit_Filter(self, node, *args, **kwargs):
        if node.name == self.filter_name:
            spec = node.node.value
            relpath = os.path.join(self.directory, spec)
            path = os.path.relpath(relpath, self.reference_root)
            logging.debug('Expanded usage of %s in %s to %s',
                          spec, self.template, path)
            self.assets.append(path)


def create_environment(root, directory_globs):
    directories = ['.']
    for pattern in directory_globs:
        result = glob.glob(os.path.join(root, pattern))
        logging.debug('Directory glob %s: %s', pattern, result)
        directories += result
    env = Environment(loader=FileSystemLoader(directories))
    return env


def find_resources(root, reference_root, env, template_globs):
    templates = []
    for pattern in template_globs:
        result = glob.glob(os.path.join(root, pattern))
        logging.debug('Template glob %s: %s', pattern, result)
        templates += result

    finder = WebpackReferenceFinder(reference_root)
    for template in templates:
        logging.debug('Parsing %s', template)
        finder.directory = os.path.dirname(template)
        finder.template = os.path.relpath(template, root)
        template_source = env.loader.get_source(env, template)[0]
        try:
            parsed_content = env.parse(template_source)
        except:
            logging.exception('Error with template', template)
            raise
        finder.visit(parsed_content)
    return finder.assets


def build_output(reference_root, assets, outfile):
    print('// root: ', reference_root, file=outfile)
    for asset in assets:
        path = './%s' % asset
        # only put actual paths, not entry points
        if os.path.exists(os.path.join(reference_root, path)):
            print('require("%s");' % path, file=outfile)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', '-o', type=argparse.FileType('w'),
                        default=sys.stdout, help='Output file')
    parser.add_argument('--directories', '-d', nargs='+',
                        default=['./templates'],
                        help='Directory glob relative to root')
    parser.add_argument('--verbose', '-v', action='count',
                        help='-v for INFO -vv for DEBUG', default=0)
    parser.add_argument('--root', '-r', default='.',
                        help='Root directory for the scan')
    parser.add_argument('template', nargs='+',
                        default=['./templates/*.jinja2'],
                        help='Template glob relative to root')
    return parser.parse_args()


def main():
    args = parse_args()

    log_level = {
        0: logging.WARN,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(args.verbose, logging.DEBUG)
    logging.basicConfig(level=log_level)

    if args.outfile.name:
        reference_root = os.path.dirname(args.outfile.name)
    else:
        reference_root = args.root

    env = create_environment(args.root, args.directories)
    assets = find_resources(args.root, reference_root, env, args.template)
    build_output(reference_root, assets, args.outfile)


if __name__ == '__main__':
    main()
