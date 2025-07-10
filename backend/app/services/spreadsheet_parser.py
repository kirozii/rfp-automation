from typing import Dict, List
import os
import pandas as pd

class SpreadsheetHandler:
    def __init__(self, input: str):
        """
        Initializes an instance of the SpreadsheetHandler. Use a single instance for a single spreadsheet.

        Args:
            input: The spreadsheet to extract questions from.
        """
        self.path = "files/" + input


    def extract_questions(self) -> pd.DataFrame:
        """
        Extracts questions from the given input file and returns the dataframe.
        """
        self.questions_df = pd.read_excel(self.path, engine='openpyxl')

        return self.questions_df

    def write_to_sheet(self, input: List[Dict]) -> None:
        """
        Writes a dictionary to the output spreadsheet.

        Args:
            input: Dictionary to be written.
        """
        self.responses_df = pd.DataFrame(input)
        output_df = pd.concat([self.questions_df, self.responses_df], axis=1)

        output_df.to_excel(self.path, index=False, engine='openpyxl')
