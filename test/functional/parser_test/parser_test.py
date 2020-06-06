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

    def parse_txt_files(self):
        files_lst = os.listdir(self.root_files_dir)
        for file in files_lst:
            path_to_file = os.path.join(self.root_files_dir, file)

            with open(path_to_file, 'r') as f:
                result_text = f.read()

            outp_dict = kp_extractor.process(decision_text=result_text)
            self.assertEqual(
                outp_dict['could_not_process'],
                False,
                "Error in txt-file: {f}".format(f=file)
            )

    def parse_err_files(self):
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
    ordered_methods = ['parse_txt_files', 'parse_err_files']
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
