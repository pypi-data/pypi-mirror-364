from ecmind_blue_client.client import parse_sqlstring
from pytest import fail

import unittest


class TestSqlParseString(unittest.TestCase):
    hostname = "localhost"
    port = 4000
    use_ssl = True

    def test_simple_sqlstring(self):
        string = r"SELECT * FROM benutzer"

        self.assertEqual(parse_sqlstring(string), string)

    def test_missing_param_raises(self):
        string = r"insert number %d here"

        with self.assertRaises(IndexError):
            parse_sqlstring(string)
            fail("Calling parse_sqlstring with a placeholder and no param to insert should raise an IndexError, but didn't.")

    def test_extra_param_raises(self):
        string = r"contains only one number %d, not more"

        with self.assertRaises(ValueError):
            parse_sqlstring(string, "1", "2")
            fail("Calling parse_sqlstring with one placeholder and two values to insert should raise a ValueError, but didn't.")

    def test_unknown_placeholder(self):
        string = r"The %x is not a valid placeholder"

        with self.assertRaises(ValueError):
            parse_sqlstring(string, "1")
            fail(r"The placeholder '%x' is not a valid placeholder and should raise a ValueError, but didn't.")

    def test_escaped_percent_sign(self):
        string = r"30 %% faster!"

        self.assertEqual(parse_sqlstring(string), r"30 % faster!")

    def test_double_percent_into_placeholder(self):
        string = r"30%%done"

        self.assertEqual(parse_sqlstring(string), r"30%done")

    def test_single_int_placeholder(self):
        string = r"insert number %d here"

        self.assertEqual(parse_sqlstring(string, 3), "insert number 3 here")

    def test_single_int_as_str(self):
        string = r"insert number %d here"

        self.assertEqual(parse_sqlstring(string, "3"), "insert number 3 here")

    def test_non_int_param_raises(self):
        string = r"insert number %d here"

        with self.assertRaises(ValueError):
            parse_sqlstring(string, "not a number")
            fail(
                r"Calling parse_sqlstring with a %d placeholder and a not-convertible-to-int parameter should raise a ValueError, but didn't."
            )

    def test_number_at_start(self):
        string = r"%d apple per day"

        self.assertEqual(parse_sqlstring(string, 1), "1 apple per day")

    def test_number_at_end(self):
        string = r"number %d"

        self.assertEqual(parse_sqlstring(string, 3), "number 3")

    def test_float_and_int(self):
        string = r"eating %f out of %d apples"

        self.assertEqual(parse_sqlstring(string, 3.5, 4), "eating 3.5 out of 4 apples")

    def test_tuple_params(self):
        string = r"numbers %d and %d are good"

        self.assertEqual(parse_sqlstring(string, 3, 4), "numbers 3 and 4 are good")

    def test_single_word(self):
        string = "My name is %w"
        self.assertEqual(parse_sqlstring(string, "Mickey"), "My name is 'Mickey'")

    def test_word_raises_on_whitespace(self):
        string = "My name is %w"

        with self.assertRaises(ValueError):
            parse_sqlstring(string, "Mickey Mouse")
            fail(
                r"Calling parse_sqlstring with a %w placeholder and a string that contains whitespace "
                "is not allowed. It should raise a ValueError but didn't."
            )

    def test_simple_string(self):
        string = r"My name is %s and I like it here."

        self.assertEqual(parse_sqlstring(string, "Mickey"), "My name is 'Mickey' and I like it here.")

    def test_string_with_whitespace(self):
        string = r"My name is %s and I like it here."

        self.assertEqual(parse_sqlstring(string, "Mickey Mouse"), "My name is 'Mickey Mouse' and I like it here.")

    def test_string_with_doublequotes(self):
        string = r'My name is "%s"'

        self.assertEqual(parse_sqlstring(string, "Mickey"), 'My name is "Mickey"')

    def test_string_with_singlequotes(self):
        string = r"My name is '%s'"

        self.assertEqual(parse_sqlstring(string, "Mickey"), "My name is 'Mickey'")

    def test_param_with_doublequotes(self):
        string = r"My name is %s"

        self.assertEqual(parse_sqlstring(string, '"Mickey"'), 'My name is \'""Mickey""\'')

    def test_param_with_singlequotes(self):
        string = r"My name is %s"

        self.assertEqual(parse_sqlstring(string, "'Mickey'"), "My name is '''Mickey'''")
        # one quote from the escaping since the string doesn't have quotation marks.
        # Two more from the escaped quote in the param. Makes a total of 3 (left and right)

    def test_unquoted_fails_on_whitespace(self):
        string = r"My name is %u"
        param = "Mickey Mouse"

        with self.assertRaises(ValueError):
            parse_sqlstring(string, param)
            fail(r"Calling parse_sqlstr with a %u parameter where the param has whitespace should raise a ValueError, but didn't.")

    def test_unquoted_fails_on_singlequote(self):
        string = r"My name is %u"
        param = "Mickey'Phantomias'Mouse"

        with self.assertRaises(ValueError):
            parse_sqlstring(string, param)
            fail(
                r"Calling parse_sqlstr with a %u parameter where the param has single quotation marks should raise a ValueError, but didn't."
            )

    def test_unquoted_fails_on_doublequote(self):
        string = r"My name is %u"
        param = 'Mickey"Phantomias"Mouse'

        with self.assertRaises(ValueError):
            parse_sqlstring(string, param)
            fail(
                r"Calling parse_sqlstr with a %u parameter where the param has double quotation marks should raise a ValueError, but didn't."
            )
