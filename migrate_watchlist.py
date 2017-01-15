"""
Description: Import DOGnzb watchlist into CouchPotato
Author: Craig Palermo
Date: 1/14/2017
"""

import argparse
import json
import logging
import sys

import requests

parser = argparse.ArgumentParser()
parser.add_argument('--file',
                    dest='filename',
                    required=True,
                    help='Filename of DOGnzb watchlist export (MUST BE IN SAME DIRECTORY AS THIS SCRIPT)')
parser.add_argument('--cb_apikey',
                    dest='cb_api_key',
                    required=True,
                    help='API key of your CouchPotato server (see CP settings)')
parser.add_argument('--cb_port',
                    dest='cb_port',
                    default=5050,
                    help='CouchPotato port, default is 5050')
parser.add_argument('--cb_host',
                    dest='cb_host',
                    default='localhost',
                    help='CouchPotato hostname, default is localhost')

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class CPMovie:
    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier


class CPClient:
    def __init__(self, args):
        self.args = args
        self.api_url = 'http://{}:{}/api/{}/'.format(args.cb_host, args.cb_port, args.cb_api_key)

    def movie_add(self, movie: CPMovie):
        """
        Add a movie to CouchPotato's wanted list. Requires object containing movie name and IMDb identifier
        from the DOGnzb export.
        :param movie:
        :return:
        """
        logging.info('Adding "{}" to CouchPotato wanted'.format(movie.name))

        r = requests.post(''.join((self.api_url, 'movie.add')), data={
            'title': movie.name,
            'identifier': movie.identifier
        })

        if r.status_code == 200:
            logging.info('Successfully added "{}" to CouchPotato wanted'.format(movie.name))
            return True
        else:
            logging.warning('Unable to add "{}" to CouchPotato wanted'.format(movie.name))
            return False


def main():
    args = parser.parse_args()
    filename = args.filename

    logging.info('=== STARTING NEW RUN ===')

    # open file for reading
    logging.debug('Reading dognzbd watchlist from file')
    file = open(filename, 'r')

    # decode json string
    logging.debug('Loading dognzbd watchlist from JSON and extracting movie data')
    watchlist = json.load(file)
    movies = [CPMovie(x['name'], x['ids']['IMDb']) for x in watchlist['items']]

    # add items in watchlist to couchpotato watchlist
    logging.debug('Adding movies to CouchPotato wanted list')
    cp = CPClient(args)
    result = [cp.movie_add(x) for x in movies]

    # count results
    success = len(filter(lambda x: x, result))
    error = len(result) - success

    logging.debug(
        'Program successfully added {} and failed to add {} titles to your CouchPotato watch list'.format(
            success,
            error
        )
    )


if __name__ == '__main__':
    main()
