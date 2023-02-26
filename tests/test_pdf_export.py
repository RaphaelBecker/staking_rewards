import unittest
import pandas as pd
import pdfkit


class testPDFExport(unittest.TestCase):

    def test_module(self):
        # create a sample dataframe
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})

        # create an HTML string from the dataframe
        html = df.to_html()

        # create a PDF from the HTML string using pdfkit
        pdfkit.from_string(html, 'output.pdf')