#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""CSS-HTML-JS-Minify.

Minifier for the Web.
"""


import atexit
import os
import sys
import gzip
import logging as log

from argparse import ArgumentParser
from datetime import datetime
from functools import partial
from hashlib import sha1
from multiprocessing import Pool, cpu_count
from subprocess import getoutput
from time import sleep

from .css_minifier import css_minify
from .html_minifier import html_minify
from .js_minifier import js_minify


__all__ = ('process_multiple_files', 'prefixer_extensioner',
           'process_single_css_file', 'process_single_html_file',
           'process_single_js_file', 'make_arguments_parser', 'main')


##############################################################################


def process_multiple_files(file_path, watch=False, wrap=False, timestamp=False,
                           comments=False, sort=False, overwrite=False,
                           zipy=False, prefix='', add_hash=False):
    """Process multiple CSS, JS, HTML files with multiprocessing."""
    if watch:
        previous = int(os.stat(file_path).st_mtime)
        while True:
            actual = int(os.stat(file_path).st_mtime)
            if previous == actual:
                sleep(60)
            else:
                previous = actual
                if file_path.endswith(".css"):
                    process_single_css_file(
                        file_path, wrap=wrap, timestamp=timestamp,
                        comments=comments, sort=sort, overwrite=overwrite,
                        zipy=zipy, prefix=prefix, add_hash=add_hash)
                elif file_path.endswith(".js"):
                    process_single_js_file(
                        file_path, timestamp=timestamp,
                        overwrite=overwrite, zipy=zipy)
                else:
                    process_single_html_file(
                        file_path, comments=comments,
                        overwrite=overwrite, prefix=prefix, add_hash=add_hash)
    else:
        if file_path.endswith(".css"):
            process_single_css_file(
                file_path, wrap=wrap, timestamp=timestamp,
                comments=comments, sort=sort, overwrite=overwrite, zipy=zipy,
                prefix=prefix, add_hash=add_hash)
        elif file_path.endswith(".js"):
            process_single_js_file(
                file_path, timestamp=timestamp,
                overwrite=overwrite, zipy=zipy)
        else:
            process_single_html_file(
                file_path, comments=comments,
                overwrite=overwrite, prefix=prefix, add_hash=add_hash)


def prefixer_extensioner(file_path, old, new,
                         file_content=None, prefix='', add_hash=False):
    """Take a file path and safely preppend a prefix and change extension.

    This is needed because filepath.replace('.foo', '.bar') sometimes may
    replace '/folder.foo/file.foo' into '/folder.bar/file.bar' wrong!.
    >>> prefixer_extensioner('/tmp/test.js', '.js', '.min.js')
    '/tmp/test.min.js'
    """
    extension = os.path.splitext(file_path)[1].lower().replace(old, new)
    filenames = os.path.splitext(os.path.basename(file_path))[0]
    filenames = prefix + filenames if prefix else filenames
    if add_hash and file_content:  # http://stackoverflow.com/a/25568916
        filenames += "-" + sha1(file_content.encode("utf-8")).hexdigest()[:11]
    dir_names = os.path.dirname(file_path)
    file_path = os.path.join(dir_names, filenames + extension)
    return file_path


def process_single_css_file(css_file_path, wrap=False, timestamp=False,
                            comments=False, sort=False, overwrite=False,
                            zipy=False, prefix='', add_hash=False,
                            output_path=None):
    """Process a single CSS file."""
    with open(css_file_path, encoding="utf-8") as css_file:
        original_css = css_file.read()
    minified_css = css_minify(original_css, wrap=wrap,
                              comments=comments, sort=sort)
    if timestamp:
        taim = "/* {0} */ ".format(datetime.now().isoformat()[:-7].lower())
        minified_css = taim + minified_css
    if output_path is None:
        min_css_file_path = prefixer_extensioner(
            css_file_path, ".css", ".css" if overwrite else ".min.css",
            original_css, prefix=prefix, add_hash=add_hash)
        if zipy:
            gz_file_path = prefixer_extensioner(
                css_file_path, ".css",
                ".css.gz" if overwrite else ".min.css.gz", original_css,
                prefix=prefix, add_hash=add_hash)
    else:
        min_css_file_path = gz_file_path = output_path
    if not zipy or output_path is None:
        # if specific output path is requested,write write only one output file
        with open(min_css_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(minified_css)
    if zipy:
        with gzip.open(gz_file_path, "wt", encoding="utf-8") as output_gz:
            output_gz.write(minified_css)
    return min_css_file_path


def process_single_html_file(html_file_path, comments=False, overwrite=False,
                             prefix='', add_hash=False, output_path=None):
    """Process a single HTML file."""
    with open(html_file_path, encoding="utf-8") as html_file:
        minified_html = html_minify(html_file.read(), comments=comments)
    if output_path is None:
        html_file_path = prefixer_extensioner(
            html_file_path, ".html" if overwrite else ".htm", ".html",
            prefix=prefix, add_hash=add_hash)
    else:
        html_file_path = output_path
    with open(html_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(minified_html)
    return html_file_path


def process_single_js_file(js_file_path, timestamp=False, overwrite=False,
                           zipy=False, output_path=None):
    """Process a single JS file."""
    with open(js_file_path, encoding="utf-8") as js_file:
        original_js = js_file.read()
    minified_js = js_minify(original_js)
    if timestamp:
        taim = "/* {} */ ".format(datetime.now().isoformat()[:-7].lower())
        minified_js = taim + minified_js
    if output_path is None:
        min_js_file_path = prefixer_extensioner(
            js_file_path, ".js", ".js" if overwrite else ".min.js",
            original_js)
        if zipy:
            gz_file_path = prefixer_extensioner(
                js_file_path, ".js", ".js.gz" if overwrite else ".min.js.gz",
                original_js)
    else:
        min_js_file_path = gz_file_path = output_path
    if not zipy or output_path is None:
        # if specific output path is requested,write write only one output file
        with open(min_js_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(minified_js)
    if zipy:
        with gzip.open(gz_file_path, "wt", encoding="utf-8") as output_gz:
            output_gz.write(minified_js)
    return min_js_file_path
