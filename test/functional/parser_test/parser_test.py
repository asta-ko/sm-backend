import unittest
import logging
import os
import sys

sys.path.append(os.path.join('../../../', 'oi_sud', 'cases', 'parsers'))
from result_texts import kp_extractor


class TestMethods(unittest.TestCase):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    root_files_dir = os.path.join(root_dir, 'tests_txt_folder')
    root_err_files_dir = os.path.join(root_dir, 'tests_err_folder')

    cases_cancelled = ['case_cancelled_0.txt', 'case_cancelled_1.txt']
    cases_returned = ['case_returned_0.txt', 'case_returned_1.txt', 'case_returned_2.txt', 'case_returned_3.txt',
                      'case_returned_4.txt', 'case_returned_5.txt']
    cases_forward = ['case_forward_0.txt', 'case_forward_1.txt']
    cases_fines_dict = {
        'case_fine_0.txt': {'num': '500', 'is_hidden': False},
        'case_fine_1.txt': {'num': '1000', 'is_hidden': False},
        'case_fine_2.txt': {'num': None, 'is_hidden': True},
        'case_fine_3.txt': {'num': '1000', 'is_hidden': False},
        'case_fine_4.txt': {'num': '1000', 'is_hidden': False}
    }
    cases_works_dict = {
        'case_works_0.txt': {'num': 40, 'is_hidden': False},
        'case_works_1.txt': {'num': 24, 'is_hidden': False},
        'case_works_2.txt': {'num': 80, 'is_hidden': False},
        'case_works_3.txt': {'num': 20, 'is_hidden': False},
        'case_works_4.txt': {'num': 40, 'is_hidden': False},
        'case_works_5.txt': {'num': 60, 'is_hidden': False}
    }

    cases_caution = ['case_caution_0.txt', 'case_caution_1.txt']

    def test_parsing_cancelled_cases(self):
        for file in self.cases_cancelled:
            path_to_file = os.path.join(self.root_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            self.assertEqual(
                outp_dict['cancelled'],
                True,
                "Error in txt-file: {f}".format(f=file)
            )

    def test_parsing_returned_cases(self):
        for file in self.cases_returned:
            path_to_file = os.path.join(self.root_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            self.assertEqual(
                outp_dict['returned'],
                True,
                "Error in txt-file: {f}".format(f=file)
            )

    def test_parsing_forward_cases(self):
        for file in self.cases_forward:
            path_to_file = os.path.join(self.root_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            self.assertEqual(
                outp_dict['forward'],
                True,
                "Error in txt-file: {f}".format(f=file)
            )

    def test_parsing_fines_cases(self):
        for file in self.cases_fines_dict:
            path_to_file = os.path.join(self.root_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            outp_dict_test = self.cases_fines_dict[file]
            self.assertEqual(
                outp_dict['fine']['num'],
                outp_dict_test['num'],
                "Error in txt-file: {f}".format(f=file)
            )
            self.assertEqual(
                outp_dict['fine']['is_hidden'],
                outp_dict_test['is_hidden'],
                "Error in txt-file: {f}".format(f=file)
            )

    def test_parsing_works_cases(self):
        for file in self.cases_works_dict:
            path_to_file = os.path.join(self.root_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            outp_dict_test = self.cases_works_dict[file]
            self.assertEqual(
                outp_dict['works']['num'],
                outp_dict_test['num'],
                "Error in txt-file: {f}".format(f=file)
            )
            self.assertEqual(
                outp_dict['works']['is_hidden'],
                outp_dict_test['is_hidden'],
                "Error in txt-file: {f}".format(f=file)
            )

    def test_parsing_caution_cases(self):
        for file in self.cases_caution:
            path_to_file = os.path.join(self.root_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            self.assertEqual(
                outp_dict['caution'],
                True,
                "Error in txt-file: {f}".format(f=file)
            )

    def test_parsing_err_cases(self):
        files_lst = os.listdir(self.root_err_files_dir)
        for file in files_lst:
            path_to_file = os.path.join(self.root_err_files_dir, file)
            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            self.assertEqual(
                outp_dict['could_not_process'],
                True,
                "Error in err-file: {f}".format(f=file)
            )


def suite():
    suite = unittest.TestSuite()
    ordered_methods = ['test_parsing_cancelled_cases', 'test_parsing_returned_cases', 'test_parsing_forward_cases',
                       'test_parsing_fines_cases', 'test_parsing_works_cases', 'test_parsing_caution_cases',
                       'test_parsing_err_cases']
    for method in ordered_methods:
        suite.addTest(TestMethods(method))

    return suite


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    runner = unittest.TextTestRunner(verbosity=2)
    test_resuilt = runner.run(suite())
    if test_resuilt.failures + test_resuilt.errors:
        logging.error("Tests failed")
    else:
        logging.info("Tests succeeded")
