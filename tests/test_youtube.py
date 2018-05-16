import unittest
from unittest.mock import patch, mock_open
from youtube.utils import read_jsonl_1


class TestYoutube(unittest.TestCase):

    def test_read_queries(self):
        with patch('builtins.open', mock_open(read_data='[[1],[1]]\n[[2],[2]]')) as mock_file:
            stuff = mock_file.read()
            r = list(read_jsonl_1('somefile'))
            print(r)
            mock_file.assert_called_once_with('somefile', 'r')


if __name__ == '__main__':
    unittest.main()
