"""
Drive tools for Google Drive operations.
"""

import logging
from typing import Any

from google_workspace_mcp.app import mcp  # Import from central app module
from google_workspace_mcp.models import (
    DriveFileContentOutput,
    DriveFileDeletionOutput,
    DriveFileUploadOutput,
    DriveFolderCreationOutput,
    DriveFolderFindOutput,
    DriveFolderSearchOutput,
    DriveSearchOutput,
    DriveSharedDrivesOutput,
)
from google_workspace_mcp.services.drive import DriveService

logger = logging.getLogger(__name__)


# --- Drive Tool Functions --- #


@mcp.tool(
    name="drive_search_files",
    description="""Search for files in Google Drive with intelligent query handling.

QUERY FORMATS SUPPORTED:
1. Simple text searches (recommended): "sprint planning meeting notes" - searches content and filenames
2. Drive API syntax: name contains 'project' AND modifiedTime > '2024-01-01'

CRITICAL LIMITATIONS:
- Parentheses ( ) are NOT supported in file searches
- Mixed syntax (text + operators) is not allowed
- For OR logic with multiple terms, use separate tool calls

VALID EXAMPLES:
✅ "project documents 2024" (simple text)
✅ name contains 'sprint' (API syntax)
✅ fullText contains 'meeting' AND modifiedTime > '2024-01-01' (combined API syntax)
✅ mimeType = 'application/pdf' (file type filter)

INVALID EXAMPLES (will cause errors):
❌ "project (sprint OR planning)" - parentheses not supported
❌ "ArcLio sprint OR planning" - mixed text and operators
❌ "meeting modifiedTime > '2024-01-01'" - mixed syntax

COMMON FILE TYPE FILTERS:
- Google Docs: mimeType = 'application/vnd.google-apps.document'
- PDFs: mimeType = 'application/pdf'
- Images: mimeType contains 'image/'

DATE FORMAT: Use RFC 3339 format like '2024-01-01' for date searches.""",
)
async def drive_search_files(
    query: str,
    page_size: int = 10,
    shared_drive_id: str | None = None,
) -> DriveSearchOutput:
    """
    Search for files in Google Drive.

    Args:
        query: Search query - either simple text or valid Drive API syntax (no parentheses)
        page_size: Maximum number of files to return (1 to 1000, default 10)
        shared_drive_id: Optional shared drive ID to search within specific shared drive

    Returns:
        DriveSearchOutput containing a list of matching files with metadata
    """
    logger.info(
        f"Executing drive_search_files with query: '{query}', page_size: {page_size}, shared_drive_id: {shared_drive_id}"
    )

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    drive_service = DriveService()
    files = drive_service.search_files(
        query=query, page_size=page_size, shared_drive_id=shared_drive_id
    )

    if isinstance(files, dict) and files.get("error"):
        raise ValueError(f"Search failed: {files.get('message', 'Unknown error')}")

    return DriveSearchOutput(files=files or [])


@mcp.tool(
    name="drive_read_file_content",
    description="Read the content of a file from Google Drive.",
)
async def drive_read_file_content(file_id: str) -> DriveFileContentOutput:
    """
    Read the content of a file from Google Drive.

    Args:
        file_id: The ID of the file to read.

    Returns:
        DriveFileContentOutput containing the file content and metadata.
    """
    logger.info(f"Executing drive_read_file_content tool with file_id: '{file_id}'")
    if not file_id or not file_id.strip():
        raise ValueError("File ID cannot be empty")

    drive_service = DriveService()
    result = drive_service.read_file_content(file_id=file_id)

    if result is None:
        raise ValueError("File not found or could not be read")

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error reading file"))

    return DriveFileContentOutput(
        file_id=result["file_id"],
        name=result["name"],
        content=result["content"],
        mime_type=result["mime_type"],
    )


@mcp.tool(
    name="drive_upload_file",
    description="Uploads a file to Google Drive by providing its content directly.",
)
async def drive_upload_file(
    filename: str,
    content_base64: str,
    parent_folder_id: str | None = None,
    shared_drive_id: str | None = None,
) -> DriveFileUploadOutput:
    """
    Uploads a file to Google Drive using its base64 encoded content.

    Args:
        filename: The desired name for the file in Google Drive (e.g., "report.pdf").
        content_base64: The content of the file, encoded in base64.
        parent_folder_id: Optional parent folder ID to upload the file to.
        shared_drive_id: Optional shared drive ID to upload the file to a shared drive.

    Returns:
        DriveFileUploadOutput containing the uploaded file metadata.
    """
    logger.info(
        f"Executing drive_upload_file with filename: '{filename}', parent_folder_id: {parent_folder_id}, shared_drive_id: {shared_drive_id}"
    )
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    if not content_base64 or not content_base64.strip():
        raise ValueError("File content (content_base64) cannot be empty")

    drive_service = DriveService()
    result = drive_service.upload_file_content(
        filename=filename,
        content_base64=content_base64,
        parent_folder_id=parent_folder_id,
        shared_drive_id=shared_drive_id,
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error uploading file"))

    return DriveFileUploadOutput(
        id=result["id"],
        name=result["name"],
        web_view_link=result["web_view_link"],
        size=result["size"],
    )


@mcp.tool(
    name="drive_create_folder",
    description="Create a new folder in Google Drive.",
)
async def drive_create_folder(
    folder_name: str,
    parent_folder_id: str | None = None,
    shared_drive_id: str | None = None,
) -> DriveFolderCreationOutput:
    """
    Create a new folder in Google Drive.

    Args:
        folder_name: The name for the new folder.
        parent_folder_id: Optional parent folder ID to create the folder within.
        shared_drive_id: Optional shared drive ID to create the folder in a shared drive.

    Returns:
        DriveFolderCreationOutput containing the created folder information.
    """
    logger.info(
        f"Executing drive_create_folder with folder_name: '{folder_name}', parent_folder_id: {parent_folder_id}, shared_drive_id: {shared_drive_id}"
    )

    if not folder_name or not folder_name.strip():
        raise ValueError("Folder name cannot be empty")

    drive_service = DriveService()
    result = drive_service.create_folder(
        folder_name=folder_name,
        parent_folder_id=parent_folder_id,
        shared_drive_id=shared_drive_id,
    )

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(
            f"Folder creation failed: {result.get('message', 'Unknown error')}"
        )

    return DriveFolderCreationOutput(
        id=result["id"], name=result["name"], web_view_link=result["web_view_link"]
    )


@mcp.tool(
    name="drive_delete_file",
    description="Delete a file from Google Drive using its file ID.",
)
async def drive_delete_file(
    file_id: str,
) -> DriveFileDeletionOutput:
    """
    Delete a file from Google Drive.

    Args:
        file_id: The ID of the file to delete.

    Returns:
        DriveFileDeletionOutput confirming the deletion.
    """
    logger.info(f"Executing drive_delete_file with file_id: '{file_id}'")
    if not file_id or not file_id.strip():
        raise ValueError("File ID cannot be empty")

    drive_service = DriveService()
    result = drive_service.delete_file(file_id=file_id)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error deleting file"))

    return DriveFileDeletionOutput(
        success=result.get("success", True),
        message=result.get("message", f"File '{file_id}' deleted successfully"),
        file_id=file_id,
    )


@mcp.tool(
    name="drive_list_shared_drives",
    description="Lists shared drives accessible by the user.",
)
async def drive_list_shared_drives(page_size: int = 100) -> DriveSharedDrivesOutput:
    """
    Lists shared drives (formerly Team Drives) that the user has access to.

    Args:
        page_size: Maximum number of shared drives to return (1 to 100, default 100).

    Returns:
        DriveSharedDrivesOutput containing a list of shared drives.
    """
    logger.info(f"Executing drive_list_shared_drives tool with page_size: {page_size}")

    drive_service = DriveService()
    drives = drive_service.list_shared_drives(page_size=page_size)

    if isinstance(drives, dict) and drives.get("error"):
        raise ValueError(drives.get("message", "Error listing shared drives"))

    if not drives:
        drives = []

    return DriveSharedDrivesOutput(count=len(drives), shared_drives=drives)


@mcp.tool(
    name="drive_search_files_in_folder",
)
async def drive_search_files_in_folder(
    folder_id: str,
    query: str = "",
    page_size: int = 10,
) -> DriveFolderSearchOutput:
    """
    Search for files or folders within a specific folder ID. Trashed files are excluded.
    This works for both regular folders and Shared Drives (when using the Shared Drive's ID as the folder_id).

    Args:
        folder_id: The ID of the folder or Shared Drive to search within.
        query: Optional search query string, following Google Drive API syntax.
               If empty, returns all items.
               Example to find only sub-folders: "mimeType = 'application/vnd.google-apps.folder'"
        page_size: Maximum number of files to return (1 to 1000, default 10).

    Returns:
        DriveFolderSearchOutput containing a list of files and folders.
    """
    logger.info(
        f"Executing drive_search_files_in_folder with folder_id: '{folder_id}', "
        f"query: '{query}', page_size: {page_size}"
    )

    if not folder_id or not folder_id.strip():
        raise ValueError("Folder ID cannot be empty")

    # Build the search query to search within the specific folder
    folder_query = f"'{folder_id}' in parents and trashed=false"
    if query and query.strip():
        # Automatically escape apostrophes in user query
        escaped_query = query.strip().replace("'", "\\'")
        # Combine folder constraint with user query
        combined_query = f"{escaped_query} and {folder_query}"
    else:
        combined_query = folder_query

    drive_service = DriveService()
    files = drive_service.search_files(
        query=combined_query,
        page_size=page_size,
        include_shared_drives=True,  # Always include shared drives for folder searches
    )

    if isinstance(files, dict) and files.get("error"):
        raise ValueError(
            f"Folder search failed: {files.get('message', 'Unknown error')}"
        )

    return DriveFolderSearchOutput(folder_id=folder_id, files=files or [])


# @mcp.tool(
#     name="drive_get_folder_info",
# )
async def drive_get_folder_info(folder_id: str) -> dict[str, Any]:
    """
    Get detailed information about a folder in Google Drive.

    Useful for understanding folder permissions and hierarchy.

    Args:
        folder_id: The ID of the folder to get information about.

    Returns:
        A dictionary containing folder metadata or an error message.
    """
    logger.info(f"Executing drive_get_folder_info with folder_id: '{folder_id}'")

    if not folder_id or not folder_id.strip():
        raise ValueError("Folder ID cannot be empty")

    drive_service = DriveService()
    folder_info = drive_service.get_file_metadata(file_id=folder_id)

    if isinstance(folder_info, dict) and folder_info.get("error"):
        raise ValueError(
            f"Failed to get folder info: {folder_info.get('message', 'Unknown error')}"
        )

    # Verify it's actually a folder
    if folder_info.get("mimeType") != "application/vnd.google-apps.folder":
        raise ValueError(
            f"ID '{folder_id}' is not a folder (mimeType: {folder_info.get('mimeType')})"
        )

    return folder_info


@mcp.tool(
    name="drive_find_folder_by_name",
)
async def drive_find_folder_by_name(
    folder_name: str,
    include_files: bool = False,
    file_query: str = "",
    page_size: int = 10,
    shared_drive_id: str | None = None,
) -> DriveFolderFindOutput:
    """
    Finds folders by name using a two-step search: first an exact match, then a partial match.
    Automatically handles apostrophes in folder names and search queries. Trashed items are excluded.

    Crucial Note: This tool finds **regular folders** within "My Drive" or a Shared Drive.
    It **does not** find Shared Drives themselves. To list available Shared Drives,
    use the `drive_list_shared_drives` tool.

    Args:
        folder_name: The name of the folder to search for.
        include_files: Whether to also search for files within the found folder (default False).
        file_query: Optional search query for files within the folder. Only used if include_files=True.
        page_size: Maximum number of files to return (1 to 1000, default 10).
        shared_drive_id: Optional shared drive ID to search within a specific shared drive.

    Returns:
        DriveFolderFindOutput containing folders found and optionally file search results.
    """
    logger.info(
        f"Executing drive_find_folder_by_name with folder_name: '{folder_name}', "
        f"include_files: {include_files}, file_query: '{file_query}', "
        f"page_size: {page_size}, shared_drive_id: {shared_drive_id}"
    )

    if not folder_name or not folder_name.strip():
        raise ValueError("Folder name cannot be empty")

    drive_service = DriveService()
    escaped_folder_name = folder_name.strip().replace("'", "\\'")

    # --- Step 1: Attempt Exact Match ---
    logger.info(f"Step 1: Searching for exact folder name: '{escaped_folder_name}'")
    exact_query = f"name = '{escaped_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders = drive_service.search_files(
        query=exact_query,
        page_size=5,
        shared_drive_id=shared_drive_id,
        include_shared_drives=True,
    )

    # If no exact match, fall back to partial match
    if not folders:
        logger.info(
            f"No exact match found. Step 2: Searching for folder name containing '{escaped_folder_name}'"
        )
        contains_query = f"name contains '{escaped_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folders = drive_service.search_files(
            query=contains_query,
            page_size=5,
            shared_drive_id=shared_drive_id,
            include_shared_drives=True,
        )

    if isinstance(folders, dict) and folders.get("error"):
        raise ValueError(
            f"Folder search failed: {folders.get('message', 'Unknown error')}"
        )

    result = DriveFolderFindOutput(
        folder_name=folder_name,
        folders_found=folders or [],
        folder_count=len(folders) if folders else 0,
    )

    if not include_files:
        return result

    if not folders:
        result.message = f"No folders found with name matching '{folder_name}'"
        return result

    target_folder = folders[0]
    folder_id = target_folder["id"]

    # Build the search query for files within the folder
    folder_constraint = f"'{folder_id}' in parents and trashed=false"

    if file_query and file_query.strip():
        # Use the same smart query logic as drive_search_files
        clean_file_query = file_query.strip()
        if (
            " " not in clean_file_query
            and ":" not in clean_file_query
            and "=" not in clean_file_query
        ):
            escaped_file_query = clean_file_query.replace("'", "\\'")
            wrapped_file_query = f"fullText contains '{escaped_file_query}'"
        else:
            wrapped_file_query = clean_file_query.replace("'", "\\'")
        combined_query = f"{wrapped_file_query} and {folder_constraint}"
    else:
        combined_query = folder_constraint

    files = drive_service.search_files(
        query=combined_query, page_size=page_size, include_shared_drives=True
    )

    if isinstance(files, dict) and files.get("error"):
        raise ValueError(
            f"File search in folder failed: {files.get('message', 'Unknown error')}"
        )

    result.target_folder = target_folder
    result.files = files or []
    result.file_count = len(files) if files else 0

    return result
