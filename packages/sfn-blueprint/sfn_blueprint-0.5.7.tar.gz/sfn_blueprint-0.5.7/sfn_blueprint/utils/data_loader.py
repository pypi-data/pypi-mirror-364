import dask.dataframe as dd
import dask.delayed as delayed
import pandas as pd
from sfn_blueprint.utils.logging import setup_logger
from sfn_blueprint.agents.base_agent import SFNAgent
import os

class SFNDataLoader(SFNAgent):
    def __init__(self):
        super().__init__(name="Data Loader", role="Data Loading Specialist")
        self.logger, _ = setup_logger(logger_name="SFNDataLoader")

        # Mapping file extensions to their respective loaders
        self.loader_map = {
            'csv': self.load_csv,
            'xlsx': self.load_excel,
            'json': self.load_json,
            'parquet': self.load_parquet,
        }

    def execute_task(self, task) -> dd.DataFrame:
        file_path = task.path

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get the file extension
        file_extension = os.path.splitext(file_path)[-1][1:].lower()
        self.logger.info(f"Received file with extension: {file_extension}")

        if file_extension in self.loader_map:
            self.logger.info(f"Loading file using {file_extension.upper()} loader")
            try:
                return self.loader_map[file_extension](file_path)
            except Exception as e:
                self.logger.error(f"Error loading {file_extension.upper()} file: {e}")
                raise
        else:
            self.logger.error(f"Unsupported file format: {file_extension}")
            raise ValueError("Unsupported file format. Please provide a CSV, Excel, JSON, or Parquet file.")

    def load_csv(self, file_path):
        self.logger.info("Loading CSV file")
        dask_df = dd.read_csv(file_path, assume_missing=True)
        pandas_df = dask_df.compute()
        return pandas_df
    """ PANDAS function no DASK"""

    def load_excel(self, file_path):
        self.logger.info("Loading Excel file")
        # Dask doesn't support Excel natively, so fallback to pandas
        # Use dask.delayed to load the Excel file with pandas
        delayed_df = delayed(pd.read_excel)(file_path, index_col=0)

        # Convert delayed pandas DataFrame to Dask DataFrame
        dask_df = dd.from_delayed([delayed_df])
        # Compute the Dask DataFrame to get a pandas DataFrame
        pandas_df = dask_df.compute()
        return pandas_df

    def load_json(self, file_path):
        self.logger.info("Loading JSON file")
        pandas_df = pd.read_json(file_path)
        return pandas_df

    def load_parquet(self, file_path):
        self.logger.info("Loading Parquet file")
        dask_df = dd.read_parquet(file_path)
        pandas_df = dask_df.compute()
        return pandas_df