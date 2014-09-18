#!/usr/bin/env python
"""
Bacon index calculator, using the IMDB movie graph.

Usage:
    kevin_bacon.py <actor_name>
"""
import logging
import re
from docopt import docopt
from graphs.primitives import Graph

ACTOR_FILE = 'actors.list'
BACON = 'Bacon, Kevin (I)'
ACTOR_RE = re.compile('([^\t]+)\t+([^\t]+)')
TITLE_RE = re.compile('([\w .,"&!?\']+) (\(\d+\))')

_log = logging.getLogger(__name__)


def _seek_to_actors(file):
    """Given a file object, advance the read pointer to the first actual actor in the list."""
    seeking = True
    while seeking:
        line = file.readline()
        _log.debug('Read "%s"', line)
        if line == "THE ACTORS LIST\n":
            seeking = False

    file.readline()  # Underline
    file.readline()  # Blank line
    headers = file.readline()
    _log.debug('Read line "%s"', headers)
    assert re.match('Name\t+Titles', headers)
    file.readline()  # Underline
    _log.debug('Finished seeking.')


def _read_next_actor(file):
    """Read and return the next actor from the file.

    Assumes that actors are delimited by a blank line.
    """
    actor_lines = [file.readline()]
    next_line = file.readline()

    while next_line != '\n':
        actor_lines.append(next_line)
        next_line = file.readline()

    return _format_actor_lines(actor_lines)


def _format_actor_lines(lines):
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
    actor_line = lines.pop(0)
    _log.debug('Parsing actor line %s', actor_line)
    match = ACTOR_RE.match(actor_line)
    if match is None:
        raise BaconException('Failed to match actor on line: %s' %actor_line)
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

    for actor, titles in actor_titles.items():
        _log.debug('Processing actor "%s"', actor)
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

    found, explored = graph.breadth_first_search(kevin_node, target_node)

    last_explored = explored[len(explored) - 1]
    _log.debug('Last explored: %s', last_explored)
    _, hops = last_explored
    return hops


def main():
    arguments = docopt(__doc__, version='0.1.0')
    target_actor = arguments['<actor_name>']

    with open(ACTOR_FILE, 'r', encoding='latin1') as actor_file:
        actor_titles = {}
        _seek_to_actors(actor_file)
        actor, titles = _read_next_actor(actor_file)

        while actor:
            actor_titles[actor] = titles
            actor, titles = _read_next_actor(actor_file)

    hops = _find_hops_to_kevin(actor_titles, target_actor)

    print('Found path in %s hops.' % hops)


class BaconException(Exception):
    pass


if __name__ == "__main__":
    main()