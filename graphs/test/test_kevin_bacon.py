import logging
from copy import deepcopy
from unittest.case import TestCase
from unittest.mock import MagicMock
from graphs.kevin_bacon import _seek_to_actors, _read_next_actor, BaconException, _create_actor_graph, \
    _find_hops_to_kevin

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

ACTOR_SAMPLE = """Aanaahad\t\tAkki, Vikki te Nikki (2014)  [Kuldeep]
\t\tLahore (2010)  [Veerender Singh]  <3>

Aanderaa, Torgny Gerhard\t\tCitizen X (2007)  [The drug-addict]
\t\tKommandør Treholt & ninjatroppen (2010)  (as Torgny Aanderaa)  [Nyhetsstemmer]  <25>
\t\tRegimet (2010)  [Inspector Hermansen]  <3>
\t\tThe Secret World (2012) (VG)  [Misc characters]
\t\t"Drømmen om Norge" (2005)  [Fin mann/Kelner/div. roller]
\t\t"Helt perfekt" (2011) {Ikke lese, ikke jobbe (#1.6)}  [Vladimir]

Aanderson, Chris\t\tDecoys 2: Alien Seduction (2007) (V)  [Guard]  <22>
\t\tHigh Noon (2009) (TV)  [Detective 'Bull' Sykes]  <23>
\t\t"Blackstone" (2011) {Bingo Night (#1.7)}  [Kevin Austin]  <26>
\t\t"Fear Itself" (2008) {Family Man (#1.3)}  <13>
\t\t"Heartland" (2007/II) {Man's Best Friend (#3.3)}  [Dwayne]  <14>
\t\t"Mixed Blessings" (2007) {The Young Apprentice (#3.12)}  [Mr. Johnson]
\t\t"Wild Roses" (2009) {Boom and Bust (#1.10)}  (uncredited)  [Junior Executive]

"""

LINKED_ACTORS_DICT = {
    'Alice': [
        'Film 1',
        'Film 2',
    ],
    'Bob': [
        'Film 1',
        'Film 3',
    ],
    'Claire': [
        'Film 1',
        'Film 4',
    ],
    'Dan': [
        'Film 3',
    ],
}


class TestKevinBacon(TestCase):
    def test_seek_to_actors(self):
        """Test that _seek_to_actors correctly reads through the header."""
        m_file = MagicMock()
        m_file.readline.side_effect = iter([
            'Blah! Blah! (blahblah)...\n',
            'SOME OTHER TEXT\n',
            '===============\n',
            'THE ACTORS LIST\n',
            '===============\n',
            '\n',
            'Name\t\tTitles\n',
            '----\t\t------\n',
            'DATA'
        ])

        _seek_to_actors(m_file)

        self.assertEqual(len(m_file.mock_calls), 8)  # Count of lines excluding DATA
        # DATA should be the next line read from the file
        self.assertEqual(m_file.readline(), 'DATA')

    def test_read_next_actor(self):
        """Test that _read_next_actor correctly extracts actor data from text blob."""
        m_file = MagicMock()
        m_file.readline.side_effect = iter(ACTOR_SAMPLE.splitlines(keepends=True))

        actor, titles = _read_next_actor(m_file)

        self.assertEquals(actor, 'Aanaahad')
        self.assertEquals(titles, ['Akki, Vikki te Nikki', 'Lahore'])

        actor, titles = _read_next_actor(m_file)

        self.assertEquals(actor, 'Aanderaa, Torgny Gerhard')
        self.assertEquals(
            titles,
            [
                'Citizen X',
                'Kommandør Treholt & ninjatroppen',
                'Regimet',
                'The Secret World',
                '"Drømmen om Norge"',
                '"Helt perfekt"'
            ]
        )
        
    def test_read_next_actor_bad_actor(self):
        """Test that _read_next_actor correctly complains on malformatted actor name."""
        m_file = MagicMock()
        m_file.readline.side_effect = iter(['ACTOR WITH_NO_TITLE\n', '\n'])

        self.assertRaises(BaconException, _read_next_actor, m_file)

    def test_read_next_actor_bad_title(self):
        """Test that _read_next_actor correctly complains on malformatted titles."""
        m_file = MagicMock()
        m_file.readline.side_effect = iter(['ACTOR\t\tTITLE 1\n', 'TITLE WITH NO DATE', '\n'])

        self.assertRaises(BaconException, _read_next_actor, m_file)

    def test_create_actor_graph(self):
        """Test that _create_actor_graph produces the expected Graph object."""
        graph = _create_actor_graph(LINKED_ACTORS_DICT)

        alice = graph.get_node_by_label('Alice')
        bob = graph.get_node_by_label('Bob')
        claire = graph.get_node_by_label('Claire')
        dan = graph.get_node_by_label('Dan')

        # Alice is in Film 1 with Bob and Claire
        self.assertTrue('Film 1' in [edge.label for edge in alice.edges])
        # Alice is not in Film 2 with either Bob or Claire
        self.assertTrue('Film 2' not in [edge.label for edge in alice.edges])

        # Check that we have the right neighbors for Alice
        alice_partners = [edge.head if edge.tail.label == 'Alice' else edge.tail for edge in alice.edges]
        self.assertTrue(bob in alice_partners)
        self.assertTrue(claire in alice_partners)
        self.assertTrue(dan not in alice_partners)

    def test_find_hops_to_kevin(self):
        """Test that _find_hops_to_kevin correctly counts the number of hops."""
        actors_dict = deepcopy(LINKED_ACTORS_DICT)
        actors_dict['Bacon, Kevin (I)'] = ["Film 1"]
        hops = _find_hops_to_kevin(actors_dict, "Dan")

        self.assertEquals(hops, 2)