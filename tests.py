import unittest
import main


# https://www.journaldev.com/15899/python-unittest-unit-test-example
class TestCMAB(unittest.TestCase):

    def tearDown(self) -> None:
        main.debug = False

    def test_debug_false(self):
        logged_message = main.log_debug("message")
        self.assertIsNone(logged_message)
    
    def test_debug_true(self):
        main.debug = True
        logged_message = main.log_debug("message")
        self.assertEqual(logged_message, "message")

    def test_get_next_link(self):
        main.distances = [(1, "term1"),(0.5, "term2"),(0.3, "term3")]
        _, next_link = main.get_next_link()
        self.assertEqual(next_link, "term1")
        
        main.pages_visited = ["term1"]
        _, next_link = main.get_next_link()
        self.assertEqual(next_link, "term2")

if __name__ == '__main__':
    unittest.main()
    