from typing import Dict, List
import pandas as pd

class SpreadsheetHandler:
    def __init__(self, input: str):
        """
        Initializes an instance of the SpreadsheetHandler. Use a single instance for a single spreadsheet.

        Args:
            input: The spreadsheet to extract questions from. Do not provide the file extension.
        """
        self.input = "files/" + input + ".xlsx"
        self.output = "files/" + input + "output.xlsx"

    def set_output(self, output: str) -> None:
        """
        Sets the output spreadsheet to the one provided.

        Args:
            output: Output spreadsheet. Do not provide the file extension.
        """
        self.output = output + ".xlsx"

    def extract_questions(self) -> pd.DataFrame:
        """
        Extracts questions from the given input file and returns the dataframe.
        """
        self.questions_df = pd.read_excel(self.input, engine='openpyxl')

        return self.questions_df

    def write_to_sheet(self, input: List[Dict]) -> None:
        """
        Writes a dictionary to the output spreadsheet.

        Args:
            input: Dictionary to be written.
        """
        self.responses_df = pd.DataFrame(input)
        output_df = pd.concat([self.questions_df, self.responses_df], axis=1)

        output_df.to_excel(self.output, index=False, engine='openpyxl')
