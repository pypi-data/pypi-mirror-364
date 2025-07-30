"""
"""

import unittest

import cift as cf

from .utils import PrettyEqual

class TestPoly(PrettyEqual, unittest.TestCase):

    def test_single_poly(self):
        layers = cf.parse(
            "L LFOO;\n"
            "P 10 10 10 20 30 30 10 30;\n"
            "E\n"
            )
        self.assertPrettyEqual(
            layers,
            {
                'LFOO': [
                    (
                        (10, 10),
                        (10, 20),
                        (30, 30),
                        (10, 30),
                        ),
                    ]
                },
            )

    def test_multi_poly(self):
        layers = cf.parse(
            "L LFOO;\n"
            "P 10 10 10 20 30 30 10 30;\n"
            "P 50 20 40 10 30 30 10 30;\n"
            "E\n"
            )
        self.assertPrettyEqual(
            layers,
            {
                'LFOO': [
                    (
                        (10, 10),
                        (10, 20),
                        (30, 30),
                        (10, 30),
                        ),
                    (
                        (50, 20),
                        (40, 10),
                        (30, 30),
                        (10, 30),
                        ),
                    ]
                },
            )

    def test_relaxed_multi_layer(self):
        layers = cf.parse(
            "L LONE;\n"
            "P 10 10 10 20 30 30 10 30;\n"
            "L Lroot;\n"
            "P 10 10 10 20 30 30 10 30;\n"
            "L XOne;\n"
            "P 50 20 40 10 30 30 10 30;\n"
            "L Y_r;\n"
            "P 50 20 40 10 30 30 10 30;\n"
            "L Kfoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoof;\n"
            "P 60 20 40 10 30 30 10 30;\n"
            "E\n",
            grammar=cf.grammar.lenient_layers
            )
        self.assertPrettyEqual(
            set(layers.keys()),
            {
                'LONE',
                'Lroot',
                'XOne',
                'Y_r',
                'Kfoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoofoof'
                }
            )

    def test_multi_layer(self):
        layers = cf.parse(
            "L LONE;\n"
            "P 10 10 10 20 30 30 10 30;\n"
            "L LTWO;\n"
            "P 50 20 40 10 30 30 10 30;\n"
            "L LONE;\n"
            "P 60 20 40 10 30 30 10 30;\n"
            "E\n"
            )
        self.assertPrettyEqual(
            layers,
            {
                'LONE': [
                    (
                        (10, 10),
                        (10, 20),
                        (30, 30),
                        (10, 30),
                        ),
                    (
                        (60, 20),
                        (40, 10),
                        (30, 30),
                        (10, 30),
                        ),
                    ],
                'LTWO': [
                    (
                        (50, 20),
                        (40, 10),
                        (30, 30),
                        (10, 30),
                        ),
                    ]
                },
            )

    def test_box(self):
        layers = cf.parse(
            "L TEST;\n"
            "B 10 20 3 4;\n"
            "E\n"
            )
        self.assertPrettyEqual(
            layers,
            {
                'TEST': [
                    (
                        (-10 // 2 + 3, -20 // 2 + 4),
                        (+10 // 2 + 3, -20 // 2 + 4),
                        (+10 // 2 + 3, +20 // 2 + 4),
                        (-10 // 2 + 3, +20 // 2 + 4),
                        ),
                    ]
                },
            )

    def test_unrotated_box(self):
        layers = cf.parse(
            "L TEST;\n"
            "B 10 20 3 4 1 0;\n"
            "E\n"
            )
        self.assertPrettyEqual(
            layers,
            {
                'TEST': [
                    (
                        (-10 // 2 + 3, -20 // 2 + 4),
                        (+10 // 2 + 3, -20 // 2 + 4),
                        (+10 // 2 + 3, +20 // 2 + 4),
                        (-10 // 2 + 3, +20 // 2 + 4),
                        ),
                    ]
                },
            )

    def test_rotated_box(self):
        layers = cf.parse(
            "L TEST;\n"
            "B 10 20 3 4 0 -1;\n"
            "E\n"
            )
        self.assertPrettyEqual(
            layers,
            {
                'TEST': [
                    (  # Pay attention to the order here
                        (-20 // 2 + 3, +10 // 2 + 4),
                        (-20 // 2 + 3, -10 // 2 + 4),
                        (+20 // 2 + 3, -10 // 2 + 4),
                        (+20 // 2 + 3, +10 // 2 + 4),
                        ),
                    ]
                },
            )

    def test_many_rotations(self):
        """
        Test that multiple nested rotations work correctly
        """

        layers = cf.parse("""
            DS 1 1 1;
            C 2 R 707 707  ;
            DF;
            DS 2 1 1;
            C 3 ;
            DF;
            DS 3 1 1;
            C 4 R 707 707  ;
            DF;
            DS 4 1 1;
            C 5 ;
            DF;
            DS 5 1 1;
            C 6 R 707 707  ;
            DF;
            DS 6 1 1;
            C 7 ;
            DF;
            DS 7 1 1;
            C 8 R 707 707  ;
            DF;
            DS 8 1 1;
            C 9 ;
            DF;
            DS 9 1 1;
            C 10 R 707 707  ;
            DF;
            DS 10 1 1;
            C 11 ;
            DF;
            DS 11 1 1;
            C 12 R 707 707  ;
            DF;
            DS 12 1 1;
            C 13 ;
            DF;
            DS 13 1 1;
            C 14  ;
            DF;
            DS 14 1 1;
            C 15 ;
            DF;
            DS 15 1 1;
            L TEST;
            P  -10 -5  10 -5  10 5  -10 5  ;
            DF;
            C 1 ;
            E
            """)

        self.assertGeomsEqualStrictPretty(
            layers,
            {
                'TEST': [
                    [
                        # TODO I am personally not sure
                        # whether this should be the correct order!!!!
                        # Sit down and reason about it!!
                        (-5, 10),
                        (-5, -10),
                        (5, -10),
                        (5, 10),
                        ],
                    ]
                }
            )


if __name__ == '__main__':
    unittest.main()

