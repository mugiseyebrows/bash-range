import sys
from . import expand_args
import unittest

class TestExpandArgs(unittest.TestCase):

    def test_invalid_range(self):

        args = ["{5...8}"]
        self.assertEqual(args, expand_args(args))

        args = ["5..8}"]
        self.assertEqual(args, expand_args(args))

        args = ["{5....8}"]
        self.assertEqual(args, expand_args(args))

        args = ["{1..z}"]
        self.assertEqual(args, expand_args(args))

        args = ["{1..5..d}"]
        self.assertEqual(args, expand_args(args))

        args = ["{a..z..d}"]
        self.assertEqual(args, expand_args(args))

        args = ["foo{5...8}bar"]
        self.assertEqual(args, expand_args(args))

    def test_valid_list(self):
        args = ["{foo,bar}"]
        expected = ["foo", "bar"]
        self.assertEqual(expected, expand_args(args))

        args = ["ab{cd,ef}{gh,ij}\"kl\""]
        expected = ["abcdghkl","abcdijkl","abefghkl","abefijkl"]
        self.assertEqual(expected, expand_args(args))

        args = ["{foo,bar..baz}"]
        expected = ["foo", "bar..baz"]
        self.assertEqual(expected, expand_args(args))

    def test_semivalid_range(self):
        args = ["{1..3{5..7}"]
        expected = ["{1..35","{1..36","{1..37"]
        self.assertEqual(expected, expand_args(args))

        args = ["{1..3}5..7}"]
        expected = ["15..7}","25..7}","35..7}"]
        self.assertEqual(expected, expand_args(args))

        args = ["foo{1..3bar{5..7}baz"]
        expected = ["foo{1..3bar5baz","foo{1..3bar6baz","foo{1..3bar7baz"]
        self.assertEqual(expected, expand_args(args))

        args = ["foo{1..3}bar5..7}baz"]
        expected = ["foo1bar5..7}baz","foo2bar5..7}baz","foo3bar5..7}baz"]
        self.assertEqual(expected, expand_args(args))

    def test_semivalid_list(self):
        args = ["{1,2,3{4,5,6}"]
        expected = ["{1,2,34","{1,2,35","{1,2,36"]
        self.assertEqual(expected, expand_args(args))

        args = ["{1,2,3}4,5,6}"]
        expected = ["14,5,6}","24,5,6}","34,5,6}"]
        self.assertEqual(expected, expand_args(args))

    def test_empty_items(self):

        args = ["p{1,2,,3,}s"]
        expected = ["p1s","p2s","ps","p3s","ps"]
        self.assertEqual(expected, expand_args(args))

    def test_valid_range(self):
        args = ["{5..8}"]
        expected = ["5","6","7","8"]
        self.assertEqual(expected, expand_args(args))

        args = ["{20..30..4}"]
        expected = ["20","24","28"]
        self.assertEqual(expected, expand_args(args))

        args = ["{3..1}"]
        expected = ["3","2","1"]
        self.assertEqual(expected, expand_args(args))

        args = ["{d..g}"]
        expected = ["d","e","f","g"]
        self.assertEqual(expected, expand_args(args))

        args = ["{z..x}"]
        expected = ["z","y","x"]
        self.assertEqual(expected, expand_args(args))

        args = ["{U..R}"]
        expected = ["U","T","S","R"]
        self.assertEqual(expected, expand_args(args))

        args = ["foo{5..7}bar"]
        expected = ["foo5bar","foo6bar","foo7bar"]
        self.assertEqual(expected, expand_args(args))

        args = ["foo{5..7}bar{d..g}baz"]
        expected = ["foo5bardbaz","foo5barebaz","foo5barfbaz","foo5bargbaz","foo6bardbaz","foo6barebaz","foo6barfbaz","foo6bargbaz","foo7bardbaz","foo7barebaz","foo7barfbaz","foo7bargbaz"]
        self.assertEqual(expected, expand_args(args))

        args = ["\"foo\"{5..7}'bar'"]
        expected = ["foo5bar","foo6bar","foo7bar"]
        self.assertEqual(expected, expand_args(args))

        args = ["foo{a..z..7}bar{10..15..4}baz"]
        expected = ["fooabar10baz","fooabar14baz","foohbar10baz","foohbar14baz","fooobar10baz","fooobar14baz","foovbar10baz","foovbar14baz"]
        self.assertEqual(expected, expand_args(args))

    def test_string(self):
        args = ["\"{1..3}\""]
        expected = ["{1..3}"]
        self.assertEqual(expected, expand_args(args))

    def test_extra(self):
        args = ["}foo{1,2}}{3..5}bar{"]
        expected = ["}foo1}3bar{","}foo1}4bar{","}foo1}5bar{","}foo2}3bar{","}foo2}4bar{","}foo2}5bar{"]
        self.assertEqual(expected, expand_args(args))

        args = ["}foo{"]
        self.assertEqual(args, expand_args(args))

    def test_invalid(self):
        args = ["{name}"]
        self.assertEqual(args, expand_args(args))

        args = ["{name..}"]
        self.assertEqual(args, expand_args(args))

if __name__ == "__main__":
    unittest.main()