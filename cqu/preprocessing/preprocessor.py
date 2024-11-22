import os
import string
from typing import Any, Dict, List, Optional, overload

import pandas as pd

from . import supported_readers, unsupported_message
from .missing_values import MissingValueStrategies, handle_missing_values
from .standardization import (
    StringStandardizers,
    standardize_numeric,
    standardize_strings,
)
from .type_conversion import convert_types


class Preprocessor:
    file_path: Optional[str]
    file_extension: Optional[str]
    dataframe: pd.DataFrame
    label_mappings: Optional[Dict[str, Dict[str, int]]]

    @overload
    def __init__(self, file_path: str) -> None: ...

    @overload
    def __init__(self, dataframe: pd.DataFrame) -> None: ...

    def __init__(
        self, dataset_input: str | pd.DataFrame, keep_duplicates: str = "first"
    ) -> None:
        self.file_path = None
        self.file_extension = None
        self.dataframe = None
        self.label_mappings = None

        if keep_duplicates not in {"first", "last", False}:
            raise ValueError(
                "Invalid value for keep_duplicates. Please provide 'first', 'last', or False."
            )

        if isinstance(dataset_input, str):
            self.file_path = dataset_input
            self.__validate_file_path()
            self.__read_dataset()
        elif isinstance(dataset_input, pd.DataFrame):
            self.dataframe = dataset_input
        else:
            raise ValueError(
                "Invalid input type. Please provide a file path or a DataFrame."
            )

        self.__handle_columns()
        self.dataframe = self.dataframe.infer_objects()
        self.__handle_duplicate_rows(keep_duplicates)

    def get_missing_summary(self) -> Dict[str, int]:
        return self.dataframe.isnull().sum().to_dict()

    @overload
    def clean_missing(
        self, strategy: MissingValueStrategies = MissingValueStrategies.DROP_COLUMNS
    ) -> None: ...

    @overload
    def clean_missing(self, strategies: Dict[str, MissingValueStrategies]) -> None: ...

    def clean_missing(
        self,
        strategy_or_strategies: (
            MissingValueStrategies | Dict[str, MissingValueStrategies]
        ) = MissingValueStrategies.DROP_COLUMNS,
    ) -> None:
        self.dataframe = handle_missing_values(self.dataframe, strategy_or_strategies)

    def convert_dtypes(self, column_types: Dict[str, Any]) -> None:
        self.dataframe = convert_types(self.dataframe, column_types)

    def standardize_numeric_data(self, columns: Optional[List[str]] = None) -> None:
        self.dataframe = standardize_numeric(self.dataframe, columns)

    @overload
    def standardize_string_data(
        self, standardizer: StringStandardizers = StringStandardizers.CLEAN
    ) -> None: ...

    @overload
    def standardize_string_data(
        self, standardizers: Dict[str, StringStandardizers]
    ) -> None: ...

    def standardize_string_data(
        self,
        standardizer: (
            StringStandardizers | Dict[str, StringStandardizers]
        ) = StringStandardizers.CLEAN,
    ) -> None:
        self.dataframe = standardize_strings(self.dataframe, standardizer)

    def write_to(self, file_path: str) -> None:
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension not in supported_readers:
            raise ValueError(unsupported_message.format(file_extension=extension))

        method_name = f"to_{supported_readers[extension][1]}"
        method = getattr(self.dataframe, method_name)
        method(file_path)

    def __validate_file_path(self) -> None:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        _, self.file_extension = os.path.splitext(self.file_path)
        self.file_extension = self.file_extension.lower()

        if self.file_extension not in supported_readers:
            raise ValueError(
                unsupported_message.format(file_extension=self.file_extension)
            )

    def __read_dataset(self) -> None:
        data = supported_readers[self.file_extension][0](self.file_path)

        if isinstance(data, list):
            self.dataframe = data[0]
        else:
            self.dataframe = data

    def __handle_columns(self) -> None:
        self.dataframe.columns = (
            self.dataframe.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.translate(str.maketrans("", "", string.punctuation.replace("_", "")))
        )
        self.dataframe = self.dataframe.loc[:, ~self.dataframe.columns.duplicated()]

    def __handle_duplicate_rows(self, keep: str) -> None:
        self.dataframe = self.dataframe.drop_duplicates(keep=keep).reset_index(
            drop=True
        )
