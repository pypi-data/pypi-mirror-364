"""
Google Sheets tool handlers for Google Workspace MCP.
"""

import logging
from typing import Any

from google_workspace_mcp.app import mcp
from google_workspace_mcp.models import (
    SheetsAddSheetOutput,
    SheetsAppendOutput,
    SheetsClearOutput,
    SheetsCreationOutput,
    SheetsDeleteSheetOutput,
    SheetsReadOutput,
    SheetsWriteOutput,
)
from google_workspace_mcp.services.sheets_service import SheetsService

logger = logging.getLogger(__name__)


@mcp.tool(
    name="sheets_create_spreadsheet",
    description="Creates a new Google Spreadsheet with a specified title.",
)
async def sheets_create_spreadsheet(title: str) -> SheetsCreationOutput:
    """
    Creates a new, empty Google Spreadsheet.

    Args:
        title: The title for the new Google Spreadsheet.

    Returns:
        SheetsCreationOutput containing the spreadsheet_id, title, and spreadsheet_url.
    """
    logger.info(f"Executing sheets_create_spreadsheet tool with title: '{title}'")
    if not title or not title.strip():
        raise ValueError("Spreadsheet title cannot be empty.")

    sheets_service = SheetsService()
    result = sheets_service.create_spreadsheet(title=title)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error creating spreadsheet"))

    if not result or not result.get("spreadsheet_id"):
        raise ValueError(
            f"Failed to create spreadsheet '{title}' or did not receive a spreadsheet ID."
        )

    return SheetsCreationOutput(
        spreadsheet_id=result["spreadsheet_id"],
        title=result["title"],
        spreadsheet_url=result["spreadsheet_url"],
    )


@mcp.tool(
    name="sheets_read_range",
    description="Reads data from a specified range in a Google Spreadsheet (e.g., 'Sheet1!A1:B5').",
)
async def sheets_read_range(spreadsheet_id: str, range_a1: str) -> SheetsReadOutput:
    """
    Reads data from a given A1 notation range in a Google Spreadsheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_a1: The A1 notation of the range to read (e.g., "Sheet1!A1:B5", or "A1:B5" if referring
                  to the first visible sheet or if sheet name is part of it).

    Returns:
        SheetsReadOutput containing the range and cell values.
    """
    logger.info(
        f"Executing sheets_read_range tool for spreadsheet_id: '{spreadsheet_id}', range: '{range_a1}'"
    )
    if not spreadsheet_id or not spreadsheet_id.strip():
        raise ValueError("Spreadsheet ID cannot be empty.")
    if not range_a1 or not range_a1.strip():
        raise ValueError("Range (A1 notation) cannot be empty.")

    sheets_service = SheetsService()
    result = sheets_service.read_range(spreadsheet_id=spreadsheet_id, range_a1=range_a1)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error reading range from spreadsheet"))

    if (
        not result or "values" not in result
    ):  # Check for 'values' as it's key for successful read
        raise ValueError(
            f"Failed to read range '{range_a1}' from spreadsheet '{spreadsheet_id}'."
        )

    return SheetsReadOutput(
        range=result.get("range", range_a1),
        values=result.get("values", []),
        major_dimension=result.get("major_dimension", "ROWS"),
    )


@mcp.tool(
    name="sheets_write_range",
    description="Writes data to a specified range in a Google Spreadsheet (e.g., 'Sheet1!A1:B5').",
)
async def sheets_write_range(
    spreadsheet_id: str,
    range_a1: str,
    values: list[list[Any]],
    value_input_option: str = "USER_ENTERED",
) -> SheetsWriteOutput:
    """
    Writes data (list of lists) to a given A1 notation range in a Google Spreadsheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_a1: The A1 notation of the range to write to (e.g., "Sheet1!A1:B2").
        values: A list of lists representing the data rows to write.
                Example: [["Name", "Score"], ["Alice", 100], ["Bob", 90]]
        value_input_option: How input data should be interpreted.
                            "USER_ENTERED": Values parsed as if typed by user (e.g., formulas).
                            "RAW": Values taken literally. (Default: "USER_ENTERED")
    Returns:
        SheetsWriteOutput detailing the update.
    """
    logger.info(
        f"Executing sheets_write_range tool for spreadsheet_id: '{spreadsheet_id}', range: '{range_a1}'"
    )
    if not spreadsheet_id or not spreadsheet_id.strip():
        raise ValueError("Spreadsheet ID cannot be empty.")
    if not range_a1 or not range_a1.strip():
        raise ValueError("Range (A1 notation) cannot be empty.")
    if not isinstance(values, list) or not all(isinstance(row, list) for row in values):
        raise ValueError("Values must be a list of lists.")
    if value_input_option not in ["USER_ENTERED", "RAW"]:
        raise ValueError("value_input_option must be either 'USER_ENTERED' or 'RAW'.")

    sheets_service = SheetsService()
    result = sheets_service.write_range(
        spreadsheet_id=spreadsheet_id,
        range_a1=range_a1,
        values=values,
        value_input_option=value_input_option,
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error writing to range in spreadsheet"))

    if not result or not result.get("updated_range"):
        raise ValueError(
            f"Failed to write to range '{range_a1}' in spreadsheet '{spreadsheet_id}'."
        )

    return SheetsWriteOutput(
        updated_range=result["updated_range"],
        updated_rows=result.get("updated_rows", 0),
        updated_columns=result.get("updated_columns", 0),
        updated_cells=result.get("updated_cells", 0),
    )


@mcp.tool(
    name="sheets_append_rows",
    description="Appends rows of data to a sheet or table in a Google Spreadsheet (e.g., to 'Sheet1').",
)
async def sheets_append_rows(
    spreadsheet_id: str,
    range_a1: str,
    values: list[list[Any]],
    value_input_option: str = "USER_ENTERED",
    insert_data_option: str = "INSERT_ROWS",
) -> SheetsAppendOutput:
    """
    Appends rows of data to a sheet or table in a Google Spreadsheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_a1: The A1 notation of the sheet or table to append to (e.g., "Sheet1" or "MyNamedRange").
                  Data will be appended after the last row of data in this range.
        values: A list of lists representing the data rows to append.
        value_input_option: How input data should be interpreted ("USER_ENTERED" or "RAW"). Default: "USER_ENTERED".
        insert_data_option: How new data should be inserted ("INSERT_ROWS" or "OVERWRITE"). Default: "INSERT_ROWS".

    Returns:
        SheetsAppendOutput detailing the append operation.
    """
    logger.info(
        f"Executing sheets_append_rows tool for spreadsheet_id: '{spreadsheet_id}', range: '{range_a1}'"
    )
    if not spreadsheet_id or not spreadsheet_id.strip():
        raise ValueError("Spreadsheet ID cannot be empty.")
    if not range_a1 or not range_a1.strip():
        raise ValueError("Range (A1 notation) cannot be empty.")
    if not isinstance(values, list) or not all(isinstance(row, list) for row in values):
        raise ValueError("Values must be a non-empty list of lists.")
    if not values:  # Ensure values is not an empty list
        raise ValueError("Values list cannot be empty.")
    if value_input_option not in ["USER_ENTERED", "RAW"]:
        raise ValueError("value_input_option must be either 'USER_ENTERED' or 'RAW'.")
    if insert_data_option not in ["INSERT_ROWS", "OVERWRITE"]:
        raise ValueError(
            "insert_data_option must be either 'INSERT_ROWS' or 'OVERWRITE'."
        )

    sheets_service = SheetsService()
    result = sheets_service.append_rows(
        spreadsheet_id=spreadsheet_id,
        range_a1=range_a1,
        values=values,
        value_input_option=value_input_option,
        insert_data_option=insert_data_option,
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error appending rows to spreadsheet"))

    if not result:  # Check for empty or None result as well
        raise ValueError(
            f"Failed to append rows to range '{range_a1}' in spreadsheet '{spreadsheet_id}'."
        )

    return SheetsAppendOutput(
        spreadsheet_id=spreadsheet_id,
        table_range=result.get("table_range", range_a1),
        updates=result.get("updates", {}),
    )


@mcp.tool(
    name="sheets_clear_range",
    description="Clears values from a specified range in a Google Spreadsheet (e.g., 'Sheet1!A1:B5').",
)
async def sheets_clear_range(spreadsheet_id: str, range_a1: str) -> SheetsClearOutput:
    """
    Clears all values from a given A1 notation range in a Google Spreadsheet.
    Note: This usually clears only the values, not formatting.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_a1: The A1 notation of the range to clear (e.g., "Sheet1!A1:B5").

    Returns:
        SheetsClearOutput confirming the cleared range.
    """
    logger.info(
        f"Executing sheets_clear_range tool for spreadsheet_id: '{spreadsheet_id}', range: '{range_a1}'"
    )
    if not spreadsheet_id or not spreadsheet_id.strip():
        raise ValueError("Spreadsheet ID cannot be empty.")
    if not range_a1 or not range_a1.strip():
        raise ValueError("Range (A1 notation) cannot be empty.")

    sheets_service = SheetsService()
    result = sheets_service.clear_range(
        spreadsheet_id=spreadsheet_id, range_a1=range_a1
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error clearing range in spreadsheet"))

    if not result or not result.get("cleared_range"):
        raise ValueError(
            f"Failed to clear range '{range_a1}' in spreadsheet '{spreadsheet_id}'."
        )

    return SheetsClearOutput(
        cleared_range=result["cleared_range"], spreadsheet_id=spreadsheet_id
    )


@mcp.tool(
    name="sheets_add_sheet",
    description="Adds a new sheet (tab) to an existing Google Spreadsheet.",
)
async def sheets_add_sheet(spreadsheet_id: str, title: str) -> SheetsAddSheetOutput:
    """
    Adds a new sheet with the given title to the specified spreadsheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        title: The title for the new sheet.

    Returns:
        SheetsAddSheetOutput containing properties of the newly created sheet.
    """
    logger.info(
        f"Executing sheets_add_sheet tool for spreadsheet_id: '{spreadsheet_id}', title: '{title}'"
    )
    if not spreadsheet_id or not spreadsheet_id.strip():
        raise ValueError("Spreadsheet ID cannot be empty.")
    if not title or not title.strip():
        raise ValueError("Sheet title cannot be empty.")

    sheets_service = SheetsService()
    result = sheets_service.add_sheet(spreadsheet_id=spreadsheet_id, title=title)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error adding sheet to spreadsheet"))

    if not result or not result.get("sheet_properties"):
        raise ValueError(
            f"Failed to add sheet '{title}' to spreadsheet '{spreadsheet_id}'."
        )

    return SheetsAddSheetOutput(
        sheet_properties=result["sheet_properties"], spreadsheet_id=spreadsheet_id
    )


@mcp.tool(
    name="sheets_delete_sheet",
    description="Deletes a specific sheet (tab) from a Google Spreadsheet using its numeric sheet ID.",
)
async def sheets_delete_sheet(
    spreadsheet_id: str, sheet_id: int
) -> SheetsDeleteSheetOutput:
    """
    Deletes a sheet from the specified spreadsheet using its numeric ID.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        sheet_id: The numeric ID of the sheet to delete.

    Returns:
        SheetsDeleteSheetOutput confirming the deletion.
    """
    logger.info(
        f"Executing sheets_delete_sheet tool for spreadsheet_id: '{spreadsheet_id}', sheet_id: {sheet_id}"
    )
    if not spreadsheet_id or not spreadsheet_id.strip():
        raise ValueError("Spreadsheet ID cannot be empty.")
    if not isinstance(sheet_id, int):
        raise ValueError("Sheet ID must be an integer.")

    sheets_service = SheetsService()
    result = sheets_service.delete_sheet(
        spreadsheet_id=spreadsheet_id, sheet_id=sheet_id
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error deleting sheet from spreadsheet"))

    if not result or not result.get("success"):
        raise ValueError(
            f"Failed to delete sheet ID '{sheet_id}' from spreadsheet '{spreadsheet_id}'."
        )

    return SheetsDeleteSheetOutput(
        success=result["success"],
        message=result.get("message", f"Sheet ID '{sheet_id}' deleted successfully"),
        spreadsheet_id=spreadsheet_id,
        deleted_sheet_id=sheet_id,
    )
