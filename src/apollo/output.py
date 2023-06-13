import json
import uuid
from typing import Any


class OutputManager:
    """
    A class that manages the output of the CLI.

    This class is responsible for storing the output data from the CLI into
    a file in a specified format (JSON or dataclass).
    """

    def store_output(self, result: Any, output_type: str) -> None:
        """
        Stores the output data from the CLI into a file in a specified format.

        Args:
            result: The data to store.
            output_type: The format to store the data in (default is "json").

        Raises:
            ValueError: occurs if the output type is not JSON or dataclass.

        Returns:
            (None)
        """

        output_type = output_type.lower()
        file_id = f"{uuid.uuid4()}"[:8]
        file_ext = "json" if output_type == "json" else "txt"
        file_path = f"output/{file_id}.{file_ext}"

        with open(file_path, "w", encoding="utf8") as file:
            if output_type == "json":
                json.dump(result, file)
            elif output_type == "dataclass":
                file.writelines(f"{result}")
            else:
                raise ValueError(f"Invalid output type: {output_type}")

        print(f"Successfully stored command output in ./{file_path}")
