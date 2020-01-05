import sys
sys.path.insert(0,'./src')

import unittest
import mock
from src.misc import random
from src.misc import roll_dice_for_corrupted_files


files_json = {'Files':
              [
                  'file_1',
                  'file_2',
                  'file_3'
              ]
             }

class TestRollDice(unittest.TestCase):

    @mock.patch('random.randint')
    def test_roll_dice_no_corrupt(self, mock_random):
        mock_random.return_value = 11
        file_json_no_corrupt = roll_dice_for_corrupted_files(files_json)
        for i in file_json_no_corrupt['Files']:
            self.assertFalse(i['corrupted'])

    @mock.patch('random.randint')
    def test_roll_dice_corrupt(self, mock_random):
        mock_random.return_value = 2
        file_json_no_corrupt = roll_dice_for_corrupted_files(files_json)

        for i in range(len(file_json_no_corrupt['Files'])):
            file_cor_attr = file_json_no_corrupt['Files'][i]['corrupted']
            if i == 2:
                self.assertTrue(file_cor_attr)
                continue
            self.assertFalse(file_cor_attr)


if __name__ == '__main__':
    unittest.main()
