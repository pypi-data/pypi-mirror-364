"""
"""

import unittest

import cift as cf

class TestSymb(unittest.TestCase):

    def test_symb_single(self):
        layers = cf.parse(
            "DS 1;\n"
            "   L LTST;\n"
            "   P 10 10 10 20 30 30 10 30;\n"
            "DF;\n"
            "C 1;\n"
            "E\n"
            )
        self.assertEqual(
            layers,
            {
                'LTST': [
                    (
                        (10, 10),
                        (10, 20),
                        (30, 30),
                        (10, 30),
                        ),
                    ]
                },
            )

    def test_symb_layers(self):
        layers = cf.parse(
            "DS 1;\n"
            "   L LONE;\n"
            "   P 10 10 10 20 30 30 10 30;\n"
            "DF;\n"
            "L LTWO;\n"
            "C 1;\n"
            "P 10 10 0 10 10 0;\n"
            "E\n"
            )
        self.assertEqual(
            layers,
            {
                'LONE': [
                    (
                        (10, 10),
                        (10, 20),
                        (30, 30),
                        (10, 30),
                        ),
                    ],
                'LTWO': [
                    (
                        (10, 10),
                        (0, 10),
                        (10, 0),
                        ),
                    ]
                },
            )

    def test_symb_deep(self):
        layers = cf.parse(
            "DS 1;\n"
            "   L LONE;\n"
            "   P 10 10 10 20 30 30 10 30;\n"
            "DF;\n"
            "DS 2;\n"
            "   L LTWO;\n"
            "   P 20 20 0 10 10 0;\n"
            "   C 1;\n"
            "DF;\n"
            "DS 3;\n"
            "   C 1;\n"
            "   C 2;\n"
            "DF;\n"
            "C 3;\n"
            "E\n"
            )
        self.assertEqual(
            layers,
            {
                'LONE': [
                    (
                        (10, 10),
                        (10, 20),
                        (30, 30),
                        (10, 30),
                        ),
                    ] * 2,  # <-- pay attention here
                'LTWO': [
                    (
                        (20, 20),
                        (0, 10),
                        (10, 0),
                        ),
                    ],
                },
            )

    def test_symb_rotate(self):
        layers = cf.parse(
            "DS 1 1 1;\n"
            "    L LONE;\n"
            "    P 0 0 0 10 10 0;\n"
            "DF;\n"
            "DS 2 1 1;\n"
            "    Call symbol #1 Rotated to 0 -10;\n"
            "DF;\n"
            "C 2;\n"
            "E\n"
            )
        self.assertEqual(
            layers,
            {
                'LONE': [
                    (
                        (0, 0),
                        (10, 0),
                        (0, -10),
                        ),
                    ],
                },
            )

    def test_symb_translate(self):
        layers = cf.parse(
            "DS 1 1 1;\n"
            "    L LONE;\n"
            "    P 0 0 0 10 10 0;\n"
            "DF;\n"
            "DS 2 1 1;\n"
            "    Call symbol #1 Translated to 2,3;\n"
            "DF;\n"
            "C 2;\n"
            "E\n"
            )
        self.assertEqual(
            layers,
            {
                'LONE': [
                    (
                        (0 + 2, 0 + 3),
                        (0 + 2, 10 + 3),
                        (10 + 2, 0 + 3),
                        ),
                    ],
                },
            )

    def test_symb_callorder(self):
        layers = cf.parse("""
            DS 1;
                C 2;
                C 3;
            DF;
            DS 2;
                L LONE;
                P 0 0 0 10 10 0;
            DF;
            DS 3;
                L LTWO;
                P 10 20 0 10 10 0;
            DF;
            C 1;
            E
            """
            )
        self.assertEqual(
            layers,
            {
                'LONE': [
                    (
                        (0, 0),
                        (0, 10),
                        (10, 0),
                        ),
                    ],
                'LTWO': [
                    (
                        (10, 20),
                        (0, 10),
                        (10, 0),
                        ),
                    ],
                },
            )

    def test_symb_transform(self):
        layers = cf.parse(
            "DS 1 1 1;\n"
            "    L LONE;\n"
            "    P 0 0 0 10 10 0;\n"
            "DF;\n"
            "DS 2 1 1;\n"
            "    C 1 R 0 -1 T 2 3;\n"
            "DF;\n"
            "C 2;\n"
            "E\n"
            )
        self.assertEqual(
            layers,
            {
                'LONE': [
                    (
                        (0 + 2, 0 + 3),
                        (10 + 2, 0 + 3),
                        (0 + 2, -10 + 3),
                        ),
                    ],
                },
            )

# TODO anti-tests
# TODO really complicated transform test with many stacked transforms

if __name__ == '__main__':
    unittest.main()

