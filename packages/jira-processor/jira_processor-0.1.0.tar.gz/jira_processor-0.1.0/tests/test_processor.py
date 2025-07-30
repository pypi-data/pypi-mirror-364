import unittest
from jira_processor import processor

class TestProcessor(unittest.TestCase):

    def test_extract_parent_issue(self):
        # Example test case
        self.assertEqual(processor.extract_parent_issue('JIRA-123'), 'EXPECTED_KEY')

    # Add more test cases as needed

if __name__ == '__main__':
    unittest.main()
