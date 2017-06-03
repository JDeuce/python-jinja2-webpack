#!/usr/bin/env python

from __future__ import print_function

import argparse
import glob
import logging
import os
import sys

from jinja2 import Environment, FileSystemLoader
from jinja2.visitor import NodeVisitor

from .utils import normalize_path


class WebpackReferenceFinder(NodeVisitor):
    def __init__(self, reference_root, filter_name=None):
        self.assets = []
        self.directory = ''
        self.template = ''
        self.reference_root = reference_root
        self.filter_name = filter_name or 'webpack'

    def visit_Filter(self, node, *args, **kwargs):
        if node.name != self.filter_name:
            return
        try:
            spec = node.node.value
        except AttributeError:
            logging.info('Skipping reference to %r because it is not a string',
                         node)
            return

        if spec.startswith('.'):
            # set relative imports relative to reference root
            relpath = os.path.join(self.directory, os.path.normpath(spec))
            path = os.path.relpath(relpath, self.reference_root)
            logging.debug('Expanded usage of %s in d:%s t:%s to %s (%s)',
                          spec, self.directory, self.template, path, relpath)
        else:
            # passthru global imports
            path = spec
            logging.debug('Passthru usage of %s in d:%s t:%s',
                          spec, self.directory, self.template)
        self.assets.append(path)


def create_environment(root, directory_globs):
    directories = [root]
    for pattern in directory_globs:
        result = glob.glob(os.path.join(root, pattern))
        logging.debug('Directory glob %s: %s', pattern, result)
        directories += result
    env = Environment(loader=FileSystemLoader(directories))
    logging.info('Using directories: %s', directories)
    return env


def find_resources(root, reference_root, env, template_globs):
    templates = []
    for pattern in template_globs:
        result = glob.glob(os.path.join(root, pattern))
        relative_result = [os.path.relpath(t, root) for t in result]
        logging.debug('Template glob %s: %s', pattern, relative_result)
        templates += relative_result
    logging.info('Using templates: %s', templates)

    finder = WebpackReferenceFinder(reference_root)
    for template in templates:
        finder.directory = os.path.join(root, os.path.dirname(template))
        finder.template = template = normalize_path(template)
        logging.info('Processing %s in directory %s',
                     template, finder.directory)
        template_source = env.loader.get_source(env, template)[0]
        try:
            parsed_content = env.parse(template_source)
        except:
            logging.exception('Error with template %s', template)
            raise
        finder.visit(parsed_content)
    return finder.assets


def build_output(reference_root, assets, outfile):
    logging.debug('Using reference root %s', reference_root)
    print('// root: ', os.path.abspath(reference_root), file=outfile)
    for path in assets:
        # we only need to include paths to static assets in the
        # generated file, entry points are already in webpack and
        # won't exist as files on disk
        refpath = os.path.join(reference_root, path)
        exists = os.path.exists(refpath)
        logging.info('Building output for %s (%s): %s', path, refpath,
                     exists and 'require' or 'skip')

        if exists:
            path = normalize_path(path)
            print('require("./%s");' % path, file=outfile)


def scan(reference_root, root, directories, templates):
    env = create_environment(root, directories)
    assets = find_resources(root, reference_root, env, templates)
    return assets


def parse_args(args=None):
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
    parser.add_argument('--reference-root', default=None,
                        help='Root for references in requires() calls')
    parser.add_argument('template', nargs='+',
                        default=['./templates/*.jinja2'],
                        help='Template glob relative to root')
    return parser.parse_args(args=args)


def main(args=None, _no_close_file=False):
    args = parse_args(args)

    log_level = {
        0: logging.WARN,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(args.verbose, logging.DEBUG)
    logging.basicConfig(level=log_level)

    # use seperate ref root from cmd line
    if args.reference_root:
        reference_root = args.reference_root
    # use directory of the output file if a name is specified
    elif hasattr(args.outfile, 'name'):
        reference_root = os.path.dirname(args.outfile.name)
    # use regular root as ref root
    else:
        reference_root = args.root

    assets = scan(reference_root, args.root, args.directories, args.template)

    build_output(reference_root, assets, args.outfile)

    if hasattr(args.outfile, 'name'):
        args.outfile.close()


if __name__ == '__main__':  # pragma: no cover
    main()
