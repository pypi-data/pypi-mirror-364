"""
Slides tools for Google Slides operations.
"""

import logging
from typing import Any

from google_workspace_mcp.app import mcp  # Import from central app module
from google_workspace_mcp.models import (
    SlidesAddFormattedTextOutput,
    SlidesAddListOutput,
    SlidesAddNotesOutput,
    SlidesAddTableOutput,
    SlidesAddTextOutput,
    SlidesCreateFromMarkdownOutput,
    SlidesCreatePresentationOutput,
    SlidesCreateSlideOutput,
    SlidesDeleteSlideOutput,
    SlidesDuplicateSlideOutput,
    SlidesGetPresentationOutput,
    SlidesGetSlidesOutput,
    SlidesInsertChartOutput,
    SlidesSharePresentationOutput,
)
from google_workspace_mcp.services.drive import DriveService
from google_workspace_mcp.services.sheets_service import SheetsService
from google_workspace_mcp.services.slides import SlidesService

logger = logging.getLogger(__name__)


# --- Slides Tool Functions --- #


@mcp.tool(
    name="get_presentation",
    description="Get a presentation by ID with its metadata and content.",
)
async def get_presentation(presentation_id: str) -> SlidesGetPresentationOutput:
    """
    Get presentation information including all slides and content.

    Args:
        presentation_id: The ID of the presentation.

    Returns:
        SlidesGetPresentationOutput containing presentation data.
    """
    logger.info(f"Executing get_presentation tool with ID: '{presentation_id}'")
    if not presentation_id or not presentation_id.strip():
        raise ValueError("Presentation ID is required")

    slides_service = SlidesService()
    result = slides_service.get_presentation(presentation_id=presentation_id)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error getting presentation"))

    return SlidesGetPresentationOutput(
        presentation_id=result.get("presentationId", presentation_id),
        title=result.get("title", ""),
        slides=result.get("slides", []),
        masters=result.get("masters", []),
        layouts=result.get("layouts", []),
    )


@mcp.tool(
    name="get_slides",
    description="Retrieves all slides from a presentation with their elements and notes.",
)
async def get_slides(presentation_id: str) -> SlidesGetSlidesOutput:
    """
    Retrieves all slides from a presentation.

    Args:
        presentation_id: The ID of the presentation.

    Returns:
        SlidesGetSlidesOutput containing the list of slides.
    """
    logger.info(f"Executing get_slides tool from presentation: '{presentation_id}'")
    if not presentation_id or not presentation_id.strip():
        raise ValueError("Presentation ID is required")

    slides_service = SlidesService()
    slides = slides_service.get_slides(presentation_id=presentation_id)

    if isinstance(slides, dict) and slides.get("error"):
        raise ValueError(slides.get("message", "Error getting slides"))

    if not slides:
        slides = []

    return SlidesGetSlidesOutput(count=len(slides), slides=slides)


@mcp.tool(
    name="create_presentation",
    description="Creates a new Google Slides presentation with the specified title.",
)
async def create_presentation(
    title: str,
) -> SlidesCreatePresentationOutput:
    """
    Create a new presentation.

    Args:
        title: The title for the new presentation.

    Returns:
        SlidesCreatePresentationOutput containing created presentation data.
    """
    logger.info(f"Executing create_presentation with title: '{title}'")
    if not title or not title.strip():
        raise ValueError("Presentation title cannot be empty")

    slides_service = SlidesService()
    result = slides_service.create_presentation(title=title)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error creating presentation"))

    return SlidesCreatePresentationOutput(
        presentation_id=result["presentation_id"],
        title=result["title"],
        presentation_url=result["presentation_url"],
    )


@mcp.tool(
    name="create_slide",
    description="Adds a new slide to a Google Slides presentation with a specified layout.",
)
async def create_slide(
    presentation_id: str,
    layout: str = "TITLE_AND_BODY",
) -> SlidesCreateSlideOutput:
    """
    Add a new slide to a presentation.

    Args:
        presentation_id: The ID of the presentation.
        layout: The layout for the new slide (e.g., TITLE_AND_BODY, TITLE_ONLY, BLANK).

    Returns:
        SlidesCreateSlideOutput containing response data confirming slide creation.
    """
    logger.info(
        f"Executing create_slide in presentation '{presentation_id}' with layout '{layout}'"
    )
    if not presentation_id or not presentation_id.strip():
        raise ValueError("Presentation ID cannot be empty")
    # Optional: Validate layout against known predefined layouts?

    slides_service = SlidesService()
    result = slides_service.create_slide(presentation_id=presentation_id, layout=layout)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error creating slide"))

    return SlidesCreateSlideOutput(
        slide_id=result["slide_id"], presentation_id=presentation_id, layout=layout
    )


@mcp.tool(
    name="add_text_to_slide",
    description="Adds text to a specified slide in a Google Slides presentation.",
)
async def add_text_to_slide(
    presentation_id: str,
    slide_id: str,
    text: str,
    shape_type: str = "TEXT_BOX",
    position_x: float = 100.0,
    position_y: float = 100.0,
    size_width: float = 400.0,
    size_height: float = 100.0,
) -> SlidesAddTextOutput:
    """
    Add text to a slide by creating a text box.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide.
        text: The text content to add.
        shape_type: Type of shape (default TEXT_BOX). Must be 'TEXT_BOX'.
        position_x: X coordinate for position (default 100.0 PT).
        position_y: Y coordinate for position (default 100.0 PT).
        size_width: Width of the text box (default 400.0 PT).
        size_height: Height of the text box (default 100.0 PT).

    Returns:
        SlidesAddTextOutput containing response data confirming text addition.
    """
    logger.info(f"Executing add_text_to_slide on slide '{slide_id}'")
    if not presentation_id or not slide_id or text is None:
        raise ValueError("Presentation ID, Slide ID, and Text are required")

    # Validate shape_type
    valid_shape_types = {"TEXT_BOX"}
    if shape_type not in valid_shape_types:
        raise ValueError(
            f"Invalid shape_type '{shape_type}' provided. Must be one of {valid_shape_types}."
        )

    slides_service = SlidesService()
    result = slides_service.add_text(
        presentation_id=presentation_id,
        slide_id=slide_id,
        text=text,
        shape_type=shape_type,
        position=(position_x, position_y),
        size=(size_width, size_height),
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error adding text to slide"))

    return SlidesAddTextOutput(
        element_id=result.get("element_id", ""),
        presentation_id=presentation_id,
        slide_id=slide_id,
    )


@mcp.tool(
    name="add_formatted_text_to_slide",
    description="Adds rich-formatted text (with bold, italic, etc.) to a slide.",
)
async def add_formatted_text_to_slide(
    presentation_id: str,
    slide_id: str,
    text: str,
    position_x: float = 100.0,
    position_y: float = 100.0,
    size_width: float = 400.0,
    size_height: float = 100.0,
) -> SlidesAddFormattedTextOutput:
    """
    Add formatted text to a slide with markdown-style formatting.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide.
        text: The text content with formatting (use ** for bold, * for italic).
        position_x: X coordinate for position (default 100.0 PT).
        position_y: Y coordinate for position (default 100.0 PT).
        size_width: Width of the text box (default 400.0 PT).
        size_height: Height of the text box (default 100.0 PT).

    Returns:
        SlidesAddFormattedTextOutput containing response data confirming text addition.
    """
    logger.info(f"Executing add_formatted_text_to_slide on slide '{slide_id}'")
    if not presentation_id or not slide_id or text is None:
        raise ValueError("Presentation ID, Slide ID, and Text are required")

    slides_service = SlidesService()
    result = slides_service.add_formatted_text(
        presentation_id=presentation_id,
        slide_id=slide_id,
        formatted_text=text,
        position=(position_x, position_y),
        size=(size_width, size_height),
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error adding formatted text to slide"))

    return SlidesAddFormattedTextOutput(
        element_id=result.get("element_id", ""),
        presentation_id=presentation_id,
        slide_id=slide_id,
        formatting_applied=result.get("formatting_applied", True),
    )


@mcp.tool(
    name="add_bulleted_list_to_slide",
    description="Adds a bulleted list to a slide in a Google Slides presentation.",
)
async def add_bulleted_list_to_slide(
    presentation_id: str,
    slide_id: str,
    items: list[str],
    position_x: float = 100.0,
    position_y: float = 100.0,
    size_width: float = 400.0,
    size_height: float = 200.0,
) -> SlidesAddListOutput:
    """
    Add a bulleted list to a slide.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide.
        items: List of bullet point text items.
        position_x: X coordinate for position (default 100.0 PT).
        position_y: Y coordinate for position (default 100.0 PT).
        size_width: Width of the text box (default 400.0 PT).
        size_height: Height of the text box (default 200.0 PT).

    Returns:
        SlidesAddListOutput containing response data confirming list addition.
    """
    logger.info(f"Executing add_bulleted_list_to_slide on slide '{slide_id}'")
    if not presentation_id or not slide_id or not items:
        raise ValueError("Presentation ID, Slide ID, and Items are required")

    slides_service = SlidesService()
    result = slides_service.add_bulleted_list(
        presentation_id=presentation_id,
        slide_id=slide_id,
        items=items,
        position=(position_x, position_y),
        size=(size_width, size_height),
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error adding bulleted list to slide"))

    return SlidesAddListOutput(
        element_id=result.get("element_id", ""),
        presentation_id=presentation_id,
        slide_id=slide_id,
        items_count=len(items),
    )


@mcp.tool(
    name="add_table_to_slide",
    description="Adds a table to a slide in a Google Slides presentation.",
)
async def add_table_to_slide(
    presentation_id: str,
    slide_id: str,
    rows: int,
    columns: int,
    data: list[list[str]],
    position_x: float = 100.0,
    position_y: float = 100.0,
    size_width: float = 400.0,
    size_height: float = 200.0,
) -> SlidesAddTableOutput:
    """
    Add a table to a slide.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide.
        rows: Number of rows in the table.
        columns: Number of columns in the table.
        data: 2D array of strings containing table data.
        position_x: X coordinate for position (default 100.0 PT).
        position_y: Y coordinate for position (default 100.0 PT).
        size_width: Width of the table (default 400.0 PT).
        size_height: Height of the table (default 200.0 PT).

    Returns:
        SlidesAddTableOutput containing response data confirming table addition.
    """
    logger.info(f"Executing add_table_to_slide on slide '{slide_id}'")
    if not presentation_id or not slide_id:
        raise ValueError("Presentation ID and Slide ID are required")

    if rows < 1 or columns < 1:
        raise ValueError("Rows and columns must be positive integers")

    if len(data) > rows or any(len(row) > columns for row in data):
        raise ValueError("Data dimensions exceed specified table size")

    slides_service = SlidesService()
    result = slides_service.add_table(
        presentation_id=presentation_id,
        slide_id=slide_id,
        rows=rows,
        columns=columns,
        data=data,
        position=(position_x, position_y),
        size=(size_width, size_height),
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error adding table to slide"))

    return SlidesAddTableOutput(
        element_id=result.get("element_id", ""),
        presentation_id=presentation_id,
        slide_id=slide_id,
        rows=rows,
        columns=columns,
    )


@mcp.tool(
    name="add_slide_notes",
    description="Adds presenter notes to a slide in a Google Slides presentation.",
)
async def add_slide_notes(
    presentation_id: str,
    slide_id: str,
    notes: str,
) -> SlidesAddNotesOutput:
    """
    Add presenter notes to a slide.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide.
        notes: The notes content to add.

    Returns:
        SlidesAddNotesOutput containing response data confirming notes addition.
    """
    logger.info(f"Executing add_slide_notes on slide '{slide_id}'")
    if not presentation_id or not slide_id or not notes:
        raise ValueError("Presentation ID, Slide ID, and Notes are required")

    slides_service = SlidesService()
    result = slides_service.add_slide_notes(
        presentation_id=presentation_id,
        slide_id=slide_id,
        notes_text=notes,
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error adding notes to slide"))

    return SlidesAddNotesOutput(
        success=result.get("success", True),
        presentation_id=presentation_id,
        slide_id=slide_id,
        notes_length=len(notes),
    )


@mcp.tool(
    name="duplicate_slide",
    description="Duplicates a slide in a Google Slides presentation.",
)
async def duplicate_slide(
    presentation_id: str,
    slide_id: str,
    insert_at_index: int | None = None,
) -> SlidesDuplicateSlideOutput:
    """
    Duplicate a slide in a presentation.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide to duplicate.
        insert_at_index: Optional index where to insert the duplicated slide.

    Returns:
        SlidesDuplicateSlideOutput containing response data with the new slide ID.
    """
    logger.info(f"Executing duplicate_slide for slide '{slide_id}'")
    if not presentation_id or not slide_id:
        raise ValueError("Presentation ID and Slide ID are required")

    slides_service = SlidesService()
    result = slides_service.duplicate_slide(
        presentation_id=presentation_id,
        slide_id=slide_id,
        insert_at_index=insert_at_index,
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error duplicating slide"))

    return SlidesDuplicateSlideOutput(
        new_slide_id=result["new_slide_id"],
        presentation_id=presentation_id,
        source_slide_id=slide_id,
    )


@mcp.tool(
    name="delete_slide",
    description="Deletes a slide from a Google Slides presentation.",
)
async def delete_slide(
    presentation_id: str,
    slide_id: str,
) -> SlidesDeleteSlideOutput:
    """
    Delete a slide from a presentation.

    Args:
        presentation_id: The ID of the presentation.
        slide_id: The ID of the slide to delete.

    Returns:
        SlidesDeleteSlideOutput containing response data confirming slide deletion.
    """
    logger.info(
        f"Executing delete_slide: slide '{slide_id}' from presentation '{presentation_id}'"
    )
    if not presentation_id or not slide_id:
        raise ValueError("Presentation ID and Slide ID are required")

    slides_service = SlidesService()
    result = slides_service.delete_slide(
        presentation_id=presentation_id, slide_id=slide_id
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error deleting slide"))

    return SlidesDeleteSlideOutput(
        success=result.get("success", True),
        presentation_id=presentation_id,
        deleted_slide_id=slide_id,
    )


@mcp.tool(
    name="create_presentation_from_markdown",
    description="Creates a Google Slides presentation from structured Markdown content with enhanced formatting support using markdowndeck.",
)
async def create_presentation_from_markdown(
    title: str,
    markdown_content: str,
) -> SlidesCreateFromMarkdownOutput:
    """
    Create a Google Slides presentation from Markdown using the markdowndeck library.

    Args:
        title: The title for the new presentation.
        markdown_content: Markdown content structured for slides.

    Returns:
        SlidesCreateFromMarkdownOutput containing created presentation data.
    """
    logger.info(f"Executing create_presentation_from_markdown with title '{title}'")
    if (
        not title
        or not title.strip()
        or not markdown_content
        or not markdown_content.strip()
    ):
        raise ValueError("Title and markdown content are required")

    slides_service = SlidesService()
    result = slides_service.create_presentation_from_markdown(
        title=title, markdown_content=markdown_content
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(
            result.get("message", "Error creating presentation from Markdown")
        )

    return SlidesCreateFromMarkdownOutput(
        presentation_id=result["presentation_id"],
        title=result["title"],
        presentation_url=result["presentation_url"],
        slides_created=result.get("slides_created", 0),
    )


@mcp.tool(name="share_presentation_with_domain")
async def share_presentation_with_domain(
    presentation_id: str,
) -> SlidesSharePresentationOutput:
    """
    Shares a Google Slides presentation with the entire organization domain.
    The domain is configured by the server administrator.

    This tool makes the presentation viewable by anyone in the organization.

    Args:
        presentation_id: The ID of the Google Slides presentation to share.

    Returns:
        SlidesSharePresentationOutput containing response data confirming the sharing operation.
    """
    logger.info(
        f"Executing share_presentation_with_domain for presentation ID: '{presentation_id}'"
    )

    if not presentation_id or not presentation_id.strip():
        raise ValueError("Presentation ID cannot be empty.")

    sharing_domain = "rizzbuzz.com"

    drive_service = DriveService()
    result = drive_service.share_file_with_domain(
        file_id=presentation_id, domain=sharing_domain, role="reader"
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(
            result.get("message", "Failed to share presentation with domain.")
        )

    # Construct the shareable link
    presentation_link = f"https://docs.google.com/presentation/d/{presentation_id}/"

    return SlidesSharePresentationOutput(
        success=True,
        message=f"Presentation successfully shared with the '{sharing_domain}' domain.",
        presentation_id=presentation_id,
        presentation_link=presentation_link,
        domain=sharing_domain,
        role="reader",
    )


# @mcp.tool(name="insert_chart_from_data")
async def insert_chart_from_data(
    presentation_id: str,
    slide_id: str,
    chart_type: str,
    data: list[list[Any]],
    title: str,
    position_x: float = 50.0,
    position_y: float = 50.0,
    size_width: float = 480.0,
    size_height: float = 320.0,
) -> SlidesInsertChartOutput:
    """
    Creates and embeds a native, theme-aware Google Chart into a slide from a data table.
    This tool handles the entire process: creating a data sheet in a dedicated Drive folder,
    generating the chart, and embedding it into the slide.

    Supported `chart_type` values:
    - 'BAR': For bar charts. The API creates a vertical column chart.
    - 'LINE': For line charts.
    - 'PIE': For pie charts.
    - 'COLUMN': For vertical column charts (identical to 'BAR').

    Required `data` format:
    The data must be a list of lists, where the first inner list contains the column headers.
    Example: [["Month", "Revenue"], ["Jan", 2500], ["Feb", 3100], ["Mar", 2800]]

    Args:
        presentation_id: The ID of the presentation to add the chart to.
        slide_id: The ID of the slide where the chart will be placed.
        chart_type: The type of chart to create ('BAR', 'LINE', 'PIE', 'COLUMN').
        data: A list of lists containing the chart data, with headers in the first row.
        title: The title that will appear on the chart.
        position_x: The X-coordinate for the chart's top-left corner on the slide (in points).
        position_y: The Y-coordinate for the chart's top-left corner on the slide (in points).
        size_width: The width of the chart on the slide (in points).
        size_height: The height of the chart on the slide (in points).

    Returns:
        SlidesInsertChartOutput containing response data confirming the chart creation and embedding.
    """
    logger.info(
        f"Executing insert_chart_from_data: type='{chart_type}', title='{title}'"
    )
    sheets_service = SheetsService()
    slides_service = SlidesService()
    drive_service = DriveService()

    spreadsheet_id = None
    try:
        # 1. Get the dedicated folder for storing data sheets
        data_folder_id = drive_service._get_or_create_data_folder()

        # 2. Create a temporary Google Sheet for the data
        sheet_title = f"[Chart Data] - {title}"
        sheet_result = sheets_service.create_spreadsheet(title=sheet_title)
        if not sheet_result or sheet_result.get("error"):
            raise RuntimeError(
                f"Failed to create data sheet: {sheet_result.get('message')}"
            )

        spreadsheet_id = sheet_result["spreadsheet_id"]

        # Move the new sheet to the correct folder and remove it from root
        drive_service.service.files().update(
            fileId=spreadsheet_id,
            addParents=data_folder_id,
            removeParents="root",
            fields="id, parents",
        ).execute()
        logger.info(f"Moved data sheet {spreadsheet_id} to folder {data_folder_id}")

        # 3. Write the data to the temporary sheet
        num_rows = len(data)
        num_cols = len(data[0]) if data else 0
        if num_rows == 0 or num_cols < 2:
            raise ValueError(
                "Data must have at least one header row and one data column."
            )

        range_a1 = f"Sheet1!A1:{chr(ord('A') + num_cols - 1)}{num_rows}"
        write_result = sheets_service.write_range(spreadsheet_id, range_a1, data)
        if not write_result or write_result.get("error"):
            raise RuntimeError(
                f"Failed to write data to sheet: {write_result.get('message')}"
            )

        # 4. Create the chart object within the sheet
        metadata = sheets_service.get_spreadsheet_metadata(spreadsheet_id)
        sheet_id_numeric = metadata["sheets"][0]["properties"]["sheetId"]

        # --- START OF FIX: Map user-friendly chart type to API-specific chart type ---
        chart_type_upper = chart_type.upper()
        if chart_type_upper in ["BAR", "COLUMN"]:
            api_chart_type = "COLUMN"
        elif chart_type_upper == "PIE":
            api_chart_type = "PIE_CHART"
        else:
            api_chart_type = chart_type_upper
        # --- END OF FIX ---

        chart_result = sheets_service.create_chart_on_sheet(
            spreadsheet_id, sheet_id_numeric, api_chart_type, num_rows, num_cols, title
        )
        if not chart_result or chart_result.get("error"):
            raise RuntimeError(
                f"Failed to create chart in sheet: {chart_result.get('message')}"
            )
        chart_id = chart_result["chartId"]

        # 5. Embed the chart into the Google Slide
        embed_result = slides_service.embed_sheets_chart(
            presentation_id,
            slide_id,
            spreadsheet_id,
            chart_id,
            position=(position_x, position_y),
            size=(size_width, size_height),
        )
        if not embed_result or embed_result.get("error"):
            raise RuntimeError(
                f"Failed to embed chart into slide: {embed_result.get('message')}"
            )

        return SlidesInsertChartOutput(
            success=True,
            message=f"Successfully added native '{title}' chart to slide.",
            presentation_id=presentation_id,
            slide_id=slide_id,
            chart_element_id=embed_result.get("element_id"),
        )

    except Exception as e:
        logger.error(f"Chart creation workflow failed: {e}", exc_info=True)
        # Re-raise to ensure the MCP framework catches it and reports an error
        raise RuntimeError(
            f"An error occurred during the chart creation process: {e}"
        ) from e
