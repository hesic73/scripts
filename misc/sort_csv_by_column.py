import pandas as pd
import fire
from loguru import logger


def sort_csv_by_column(file_path: str, column: str = None):
    """
    Sorts a CSV file by the specified column and saves it.

    :param file_path: Path to the CSV file to sort.
    :param column: Column name to sort by. If not provided, the first column is used.
    """
    try:
        df = pd.read_csv(file_path)

        # 使用第一列作为默认排序列
        if column is None:
            column = df.columns[0]
        elif column not in df.columns:
            available_keys = ", ".join(df.columns)
            logger.error(
                f"'{column}' is not a column in the CSV file. Available columns are: {available_keys}")
            return

        # 按指定列排序
        sorted_df = df.sort_values(by=column)
        sorted_df.to_csv(file_path, index=False)

        logger.success(
            f"File '{file_path}' sorted by '{column}' and saved successfully.")
    except Exception as e:
        logger.error(f"Error processing file '{file_path}': {e}")


if __name__ == "__main__":
    fire.Fire(sort_csv_by_column)
