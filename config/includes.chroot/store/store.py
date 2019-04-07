#!/usr/bin/env python3
import sys
import time
import datetime
import argparse
import re
import os
import configparser
import shutil
import subprocess


def get_parser():
    parser = argparse.ArgumentParser(description='Update/list store')
    parser.add_argument('--store-dir',
                        metavar='STORE_DIR',
                        default='/store',
                        help='Store directory')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='Makes store command verbose')

    subparsers = parser.add_subparsers(
            title='subcommands',
            description='valid subcommands',
            dest='command',
            help='additional help')
    subparsers.add_parser('list')
    subparsers.add_parser('update')
    subparsers.add_parser('check')

    return parser


def parse_database(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    database = []
    for section in config.sections():
        package = {
            'name': config[section]['name'],
            'version': config[section]['version'],
        }
        if 'tarball' in config[section]:
            package['tarball'] = config[section]['tarball']
        if 'python' in config[section]:
            package['python'] = config[section]['python']
        database.append(package)
    return database


def is_package_installed(store_dir, package):
    package_dir = store_dir + '/' + package['name'] + '-' + package['version']
    return os.path.isdir(package_dir)


def package_id(package):
    return package['name'] + '-' + package['version']


def system_wget(url, cache_dir):
    p = subprocess.Popen(['wget', '-c', '%s' % (url)], cwd=cache_dir)
    p.wait()


def system_virtualenv(package, store_dir):
    virtualenv_dir = store_dir + '/packages/' + package_id(package)
    if os.path.isdir(virtualenv_dir):
        shutil.rmtree(virtualenv_dir)
    p = subprocess.Popen(['python3', '-m', 'venv', virtualenv_dir])
    p.wait()
    command = [virtualenv_dir + '/bin/pip', 'install', package['python'] + '==' + package['version']]
    p = subprocess.Popen(command)
    p.wait()
    if p.returncode != 0:
        print("ERROR " + " ".join(command))
        shutil.rmtree(virtualenv_dir)


def system_untar(package, store_dir):
    temp_dir = store_dir + '/tmp'
    cache_dir = store_dir + '/cache'
    packages_dir = store_dir + '/packages'
    shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    filename = cache_dir + '/' + os.path.basename(package['tarball'])
    options = untar_options(filename)
    if options is None:
        print("filename " + filename + " not supported")
    else:
        p = subprocess.Popen(['tar', options, filename], cwd=temp_dir)
        p.wait()
        dirs = os.listdir(temp_dir)
        if len(dirs) == 1:
            src_file = temp_dir + '/' + dirs[0]
            dest_file = packages_dir + '/' + package['name'] + '-' + package['version']
            print('mv %s %s' % (src_file, dest_file))
            shutil.move(src_file, dest_file)
        else:
            package_dir = packages_dir + '/' + package['name'] + '-' + package['version']
            os.mkdir(package_dir)
            for f in dirs:
                src_file = temp_dir + '/' + f
                shutil.move(src_file, package_dir)


def untar_options(filename):
    if filename.endswith('.tar.gz'):
        return "xfz"
    if filename.endswith('.tar.xz'):
        return "xf"
    return None


def lookup_package(database, pkg_id):
    for package in database:
        if package_id(package) == pkg_id:
            return package
    return None


def command_update(store_dir, database):
    for package in database:
        if is_package_installed(store_dir + '/packages', package):
            print('%s already installed' % (package_id(package)))
        else:
           if 'tarball' in package:
               print('%s install from tarball' % (package_id(package)))
               system_wget(package['tarball'], store_dir + '/cache')
               system_untar(package, store_dir)

           elif 'python' in package:
               print('%s install python app' % (package_id(package)))
               system_virtualenv(package, store_dir)
           else:
               print('ERROR: %s not supported' % (package_id(package)))


def command_list(store_dir, database):
    for package in sorted(database, key=lambda x: package_id(x)):
        if is_package_installed(store_dir, package):
            status = 'installed'
        else:
            status = '-'
        print("%-16s %-10s %s" % (package['name'], package['version'], status))


def command_check(store_dir, database):
    for f in os.listdir(store_dir):
        if f in ["database", "packages", "cache", "tmp"]:
            continue
        else:
            print("ERROR: invalid file %s", f)

    packages_dir = store_dir + "/packages"
    for f in os.listdir(packages_dir):
        if lookup_package(database, f) is None:
            print("ERROR: package %s not in database" % (f))


def main():
    args = get_parser().parse_args()

    if (args.verbose):
        print(args)

    database = parse_database(args.store_dir + '/database')
    if (args.verbose):
        print(database)

    if args.command == 'list':
        command_list(args.store_dir + '/packages', database)
    elif args.command == 'update':
        command_update(args.store_dir, database)
    elif args.command == 'check':
        command_check(args.store_dir, database)


if __name__ == '__main__':
    main()
