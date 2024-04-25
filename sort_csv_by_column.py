import pandas as pd
import click

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--column', default=None, help='Column name to sort by. If not provided, the first column is used.')
def sort_csv_by_column(file_path: str, column: str = None):
    """
    Sorts a CSV file by the specified column and saves it.

    FILE_PATH: Path to the CSV file to sort.
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Determine the key by which to sort; default to the first column if none provided
    if column is None:
        column = df.columns[0]
    elif column not in df.columns:
        available_keys = ", ".join(df.columns)
        raise ValueError(f"'{column}' is not a column in the CSV file. Available columns are: {available_keys}")

    # Sort the DataFrame by the key
    sorted_df = df.sort_values(by=column)

    # Save the sorted DataFrame back to the same file
    sorted_df.to_csv(file_path, index=False)

    print(f"File '{file_path}' sorted by '{column}' and saved successfully.")

if __name__ == '__main__':
    sort_csv_by_column()
