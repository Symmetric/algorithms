#!/usr/bin/env python
"""
Bacon index calculator, using the IMDB movie graph.

Usage:
    kevin_bacon.py <actor_name>
"""
from _pickle import Unpickler, Pickler
import logging
import pickle
from os.path import exists
import os
from progressbar.progressbar import ProgressBar
import re
from docopt import docopt
from graphs.primitives import Graph, GraphException

PICKLE_FILE = 'pickle'
SEEKING_START = 0
SEEKING_HEADERS = 1
SEEKING_SEPARATOR = 2
ACTOR_FILE = 'actors.list'
BACON = 'Bacon, Kevin (I)'
ACTOR_RE = re.compile('([^\t]+)\t+([^\t]+)')
# TITLE_RE = re.compile('([\w .,-:"&!?\'\(\)]+) \((\d+)(:?/\w+)?\).*')
TITLE_RE = re.compile('(.*) \((?:(?:(\d+))|(\?\?\?\?))(?:/\w+)?\).*')

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _seek_to_actors(line, seeking):
    """Given a file object, advance the read pointer to the first actual actor in the list."""
    _log.debug('Read line "%s"', line)
    if seeking == SEEKING_START and re.match('Name\t+Titles', line):
        return SEEKING_HEADERS
    elif seeking == SEEKING_HEADERS and re.match('[-]+\s+[-]+'):
        return SEEKING_SEPARATOR
    else:
        return SEEKING_START


# def _read_next_actor(file):
#     """Read and return the next actor from the file.
#
#     Assumes that actors are delimited by a blank line.
#     """
#     actor_lines = [file.readline()]
#     next_line = file.readline()
#
#     while next_line != '\n':
#         actor_lines.append(next_line)
#         next_line = file.readline()
#
#     return _format_actor_lines(actor_lines)


def _format_actor_entry(entry):
    """Parse the text of an Actor entry.

    Expects the following input format:

    "
    Aackerlund, Thor        Ecstasy of Order: The Tetris Masters (2011)  [Himself]
                            The NES Club (2015)  [Himself]
                            "Culture x History x Attitude" (2012) {Dallas Comic-Con, Carolina Games Summit, Pinballz Arcade (#1.3)}  [Himself]

    "

    Where
    RULES:
    1       Movies and recurring TV roles only, no TV guest appearances
    2       Please submit entries in the format outlined at the end of the list
    3       Feel free to submit new actors

    "xxxxx"        = a television series
    "xxxxx" (mini) = a television mini-series
    [xxxxx]        = character name
    <xx>           = number to indicate billing position in credits
    (TV)           = TV movie, or made for cable movie
    (V)            = made for video movie (this category does NOT include TV
                     episodes repackaged for video, guest appearances in
                     variety/comedy specials released on video, or
                     self-help/physical fitness videos)
    """
    lines = entry.split('\n')
    actor_line = lines.pop(0)
    _log.debug('Parsing actor line %s', actor_line)
    match = ACTOR_RE.match(actor_line)
    if match is None:
        raise BaconException('Failed to match actor on line: %s' % actor_line)
    actor, first_role = match.groups()

    _log.debug('Got actor, first_role = %s, %s', actor, first_role)
    title_strings = [first_role] + [title.strip() for title in lines]
    titles = []

    # Extract the titles from the list of title input strings
    for title_string in title_strings:
        match = TITLE_RE.match(title_string)
        if match is None:
            raise BaconException('Failed to match title on line: %s' % title_string)
        titles.append(match.group(1))

    return actor, titles


def _create_actor_graph(actor_titles):
    graph = Graph()
    films_to_actors = {}

    print('Creating actor graph...')
    progress = ProgressBar()
    for actor, titles in progress(actor_titles.items()):
        _log.info('Processing actor "%s"', actor)
        # First add a node for the actor
        graph.add_node_by_label(actor)

        # Next add edges to any actors with matching titles
        for title in titles:
            if title in films_to_actors:
                # We've already got at least one actor from this title. Add edges.
                for other_actor in films_to_actors[title]:
                    graph.add_edge_by_label(actor, other_actor, edge_label=title)

                # Also add this actor to the film's actor list, in case further matching actors are found.
                films_to_actors[title].append(actor)
            else:
                # This film hasn't been seen before. Start a new actor list.
                films_to_actors[title] = [actor]

    return graph


def _find_hops_to_kevin(actor_titles, target_actor):
    graph = _create_actor_graph(actor_titles)
    _log.debug('Build graph %s', graph)
    kevin_node = graph.get_node_by_label(BACON)
    target_node = graph.get_node_by_label(target_actor)

    found, explored, _ = graph.breadth_first_search(kevin_node, target_node)

    last_explored = explored[len(explored) - 1]
    _log.debug('Last explored: %s', last_explored)
    _, hops = last_explored
    return hops


def _print_path_to_kevin(actor_titles, target_actor):
    """
    Format and print the path to Kevin Bacon.

    :param graph: A Graph containing actor Nodes and film Edges.
    :param path: A list of Edges in the Graph from the Kevin node to the target node.
    :return: None
    """
    graph, path = _find_path_to_kevin(actor_titles, target_actor)
    kevin = graph.get_node_by_label(BACON)
    source = kevin
    for edge in path:
        destination = edge.get_other_node(source)
        print('%s was in %s with %s' % (source.label, edge.label, destination.label))
        # Update source for next iteration
        source = destination


def _find_path_to_kevin(actor_titles, target_actor):
    graph = _create_actor_graph(actor_titles)
    _log.debug('Build graph %s', graph)
    kevin_node = graph.get_node_by_label(BACON)
    target_node = graph.get_node_by_label(target_actor)

    path = graph.bfs_path(kevin_node, target_node)

    _log.debug('Got path: %s', path)

    return graph, path


def main():
    arguments = docopt(__doc__, version='0.1.0')
    target_actor = arguments['<actor_name>']

    pickle_data = None

    if exists(PICKLE_FILE):
        with open(PICKLE_FILE) as pickle_file:
            pickle_data = Unpickler(pickle_file).load()

    try:
        if not pickle_data:
            print('No pickle found.')
            with open(ACTOR_FILE, 'r', encoding='latin1') as actor_file:
                actor_titles = {}

                print('Loading input file...')
                actor_lines = actor_file.read().strip().split('\n\n')
                actor_last_lines = actor_lines[-10:]

                print('Parsing input file...')
                progress = ProgressBar()
                for actor in progress(actor_lines):
                    actor, titles = _format_actor_entry(actor)
                    actor_titles[actor] = titles

                pickle_data = {'actor_titles': actor_titles}
                print('Saving pickle...')
                with open(PICKLE_FILE, 'w') as pickle_file:
                    Pickler(pickle_file).dump()
        else:
            print('Pickle found, loading cached data.')
            actor_titles = pickle_data['actor_titles']

        print('Searching for path from Kevin...')
        _find_path_to_kevin(actor_titles, target_actor)
    except BaconException as e:
        print('\nERROR: %s' % e)


class BaconException(Exception):
    pass
