import unittest
from sus_adk.session import Session

class TestSession(unittest.TestCase):
    def test_set_and_get_cookie(self):
        session = Session()
        session.set_cookie('foo', 'bar')
        self.assertEqual(session.get_cookie('foo'), 'bar')

    def test_overwrite_cookie(self):
        session = Session({'foo': 'bar'})
        session.set_cookie('foo', 'baz')
        self.assertEqual(session.get_cookie('foo'), 'baz')

    def test_as_dict(self):
        cookies = {'a': '1', 'b': '2'}
        session = Session(cookies)
        self.assertEqual(session.as_dict(), cookies)

    def test_get_missing_cookie(self):
        session = Session()
        self.assertIsNone(session.get_cookie('missing'))

if __name__ == '__main__':
    unittest.main() 