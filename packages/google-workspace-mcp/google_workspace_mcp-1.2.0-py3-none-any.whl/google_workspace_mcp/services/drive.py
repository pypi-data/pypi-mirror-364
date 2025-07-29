"""
Google Drive service implementation for file operations.
Provides comprehensive file management capabilities through Google Drive API.
"""

import base64
import binascii
import io
import logging
import mimetypes
from typing import Any

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from google_workspace_mcp.services.base import BaseGoogleService

logger = logging.getLogger(__name__)


class DriveService(BaseGoogleService):
    """
    Service for interacting with Google Drive API.
    """

    def __init__(self):
        """Initialize the Drive service."""
        super().__init__("drive", "v3")

    def _escape_drive_query(self, query: str) -> str:
        """
        Smart query processing for Drive API queries.

        Automatically converts simple text searches to proper Drive API format:
        - Simple text like "sprint planning" becomes fullText contains 'sprint planning'
        - Already formatted queries like "name contains 'test'" are passed through
        - Handles apostrophe escaping automatically
        - Validates queries to prevent invalid syntax

        Args:
            query: Query string (can be simple text or Drive API format)

        Returns:
            Properly formatted query string for Drive API

        Raises:
            ValueError: If query contains invalid syntax like unsupported parentheses
        """
        if not query or not query.strip():
            return ""

        query = query.strip()

        # Remove surrounding double quotes if present
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]

        # Check for unsupported syntax - parentheses are not supported in files.list queries
        if "(" in query or ")" in query:
            raise ValueError(
                "Parentheses are not supported in Drive file search queries. "
                "Use separate search calls or restructure your query. "
                "For complex searches, try: fullText contains 'term1' OR fullText contains 'term2'"
            )

        # Check if this is already a structured Drive API query
        # Look for Drive API operators and syntax
        drive_api_indicators = [
            " contains ",
            " = ",
            " != ",
            " > ",
            " < ",
            " >= ",
            " <= ",
            " in ",
            " and ",
            " or ",
            " not ",
            "mimeType",
            "parents",
            "trashed",
            "sharedWithMe",
            "starred",
            "modifiedTime",
            "createdTime",
            "name",
            "fullText",
        ]

        is_structured_query = any(
            indicator in query.lower() for indicator in drive_api_indicators
        )

        if is_structured_query:
            # Validate that it's not a mixed query (text + operators + API syntax)
            # Mixed queries like "ArcLio (sprint OR planning) modifiedTime > '2024-01-01'" are invalid
            words = query.split()
            has_unquoted_text = False

            for word in words:
                # Skip quoted strings, operators, and API field names
                if (
                    word.startswith("'")
                    or word.endswith("'")
                    or word.lower() in ["and", "or", "not", "contains", "in"]
                    or any(
                        field in word.lower()
                        for field in [
                            "mimetype",
                            "name",
                            "fulltext",
                            "modifiedtime",
                            "createdtime",
                            "trashed",
                            "starred",
                            "sharedwithme",
                            "parents",
                        ]
                    )
                    or word in ["=", "!=", ">", "<", ">=", "<="]
                    or word.startswith("'")
                    and word.endswith("'")
                ):
                    continue

                # Check if this looks like unquoted text mixed with operators
                if not word.replace("-", "").replace("_", "").isalnum():
                    continue

                # If we find unquoted alphanumeric text in a structured query, it might be mixed
                if (
                    any(op in query.lower() for op in [" and ", " or "])
                    and len(word) > 2
                ):
                    has_unquoted_text = True
                    break

            if has_unquoted_text:
                raise ValueError(
                    "Mixed query syntax detected. Use either: "
                    "1) Simple text: 'sprint planning meeting' "
                    "2) Drive API syntax: fullText contains 'sprint' OR fullText contains 'planning' "
                    "3) Structured queries: modifiedTime > '2024-01-01' AND name contains 'sprint'"
                )

            # This looks like a valid structured Drive API query, just escape apostrophes
            return query.replace("'", "\\'")
        # This is a simple text search, convert to fullText search
        # Escape apostrophes in the search term
        escaped_text = query.replace("'", "\\'")
        # Wrap in fullText contains for better search results
        return f"fullText contains '{escaped_text}'"

    def search_files(
        self,
        query: str,
        page_size: int = 10,
        shared_drive_id: str | None = None,
        include_shared_drives: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Search for files in Google Drive.

        Args:
            query: Search query string
            page_size: Maximum number of files to return (1-1000)
            shared_drive_id: Optional shared drive ID to search within a specific shared drive
            include_shared_drives: Whether to include shared drives in search (default True)

        Returns:
            List of file metadata dictionaries (id, name, mimeType, etc.) or an error dictionary
        """
        try:
            logger.info(
                f"Searching files with query: '{query}', page_size: {page_size}, "
                f"shared_drive_id: {shared_drive_id}, include_shared_drives: {include_shared_drives}"
            )

            # Validate and constrain page_size
            page_size = max(1, min(page_size, 1000))

            # Properly escape the query for Drive API
            escaped_query = self._escape_drive_query(query)

            # Build list parameters with comprehensive shared drive support
            list_params = {
                "q": escaped_query,
                "pageSize": page_size,
                "fields": "files(id, name, mimeType, modifiedTime, size, webViewLink, iconLink, parents)",
                "supportsAllDrives": True,
                "includeItemsFromAllDrives": True,
            }

            if shared_drive_id:
                # Search within a specific shared drive
                list_params["driveId"] = shared_drive_id
                list_params["corpora"] = "drive"
            elif include_shared_drives:
                # Search across all drives (user's files + shared drives + shared folders)
                list_params["corpora"] = "allDrives"
            else:
                # Search only user's personal files
                list_params["corpora"] = "user"

            results = self.service.files().list(**list_params).execute()
            files = results.get("files", [])

            logger.info(f"Found {len(files)} files matching query '{query}'")
            return files

        except Exception as e:
            return self.handle_api_error("search_files", e)

    def read_file_content(self, file_id: str) -> dict[str, Any] | None:
        """
        Read the content of a file from Google Drive.

        Args:
            file_id: The ID of the file to read

        Returns:
            Dict containing mimeType and content (possibly base64 encoded)
        """
        try:
            # Get file metadata
            file_metadata = (
                self.service.files()
                .get(fileId=file_id, fields="mimeType, name", supportsAllDrives=True)
                .execute()
            )

            original_mime_type = file_metadata.get("mimeType")
            file_name = file_metadata.get("name", "Unknown")

            logger.info(
                f"Reading file '{file_name}' ({file_id}) with mimeType: {original_mime_type}"
            )

            # Handle Google Workspace files by exporting
            if original_mime_type.startswith("application/vnd.google-apps."):
                return self._export_google_file(file_id, file_name, original_mime_type)
            return self._download_regular_file(file_id, file_name, original_mime_type)

        except Exception as e:
            return self.handle_api_error("read_file", e)

    def get_file_metadata(self, file_id: str) -> dict[str, Any]:
        """
        Get metadata information for a file from Google Drive.

        Args:
            file_id: The ID of the file to get metadata for

        Returns:
            Dict containing file metadata or error information
        """
        try:
            if not file_id:
                return {"error": True, "message": "File ID cannot be empty"}

            logger.info(f"Getting metadata for file with ID: {file_id}")

            # Retrieve file metadata with comprehensive field selection
            file_metadata = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, size, createdTime, modifiedTime, "
                    "webViewLink, webContentLink, iconLink, parents, owners, "
                    "shared, trashed, capabilities, permissions, "
                    "description, starred, explicitlyTrashed",
                    supportsAllDrives=True,
                )
                .execute()
            )

            logger.info(
                f"Successfully retrieved metadata for file: {file_metadata.get('name', 'Unknown')}"
            )
            return file_metadata

        except Exception as e:
            return self.handle_api_error("get_file_metadata", e)

    def create_folder(
        self,
        folder_name: str,
        parent_folder_id: str | None = None,
        shared_drive_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new folder in Google Drive.

        Args:
            folder_name: The name for the new folder
            parent_folder_id: Optional parent folder ID to create the folder within
            shared_drive_id: Optional shared drive ID to create the folder in a shared drive

        Returns:
            Dict containing the created folder information or error details
        """
        try:
            if not folder_name or not folder_name.strip():
                return {"error": True, "message": "Folder name cannot be empty"}

            logger.info(
                f"Creating folder '{folder_name}' with parent_folder_id: {parent_folder_id}, shared_drive_id: {shared_drive_id}"
            )

            # Build folder metadata
            folder_metadata = {
                "name": folder_name.strip(),
                "mimeType": "application/vnd.google-apps.folder",
            }

            # Set parent folder if specified
            if parent_folder_id:
                folder_metadata["parents"] = [parent_folder_id]
            elif shared_drive_id:
                # If shared drive is specified but no parent, set shared drive as parent
                folder_metadata["parents"] = [shared_drive_id]

            # Create the folder with shared drive support
            create_params = {
                "body": folder_metadata,
                "fields": "id, name, parents, webViewLink, createdTime",
                "supportsAllDrives": True,
            }

            if shared_drive_id:
                create_params["driveId"] = shared_drive_id

            created_folder = self.service.files().create(**create_params).execute()

            logger.info(
                f"Successfully created folder '{folder_name}' with ID: {created_folder.get('id')}"
            )
            return created_folder

        except Exception as e:
            return self.handle_api_error("create_folder", e)

    def _export_google_file(
        self, file_id: str, file_name: str, mime_type: str
    ) -> dict[str, Any]:
        """Export a Google Workspace file in an appropriate format."""
        # Determine export format
        export_mime_type = None
        if mime_type == "application/vnd.google-apps.document":
            export_mime_type = "text/markdown"  # Consistently use markdown for docs
        elif mime_type == "application/vnd.google-apps.spreadsheet":
            export_mime_type = "text/csv"
        elif mime_type == "application/vnd.google-apps.presentation":
            export_mime_type = "text/plain"
        elif mime_type == "application/vnd.google-apps.drawing":
            export_mime_type = "image/png"

        if not export_mime_type:
            logger.warning(f"Unsupported Google Workspace type: {mime_type}")
            return {
                "error": True,
                "error_type": "unsupported_type",
                "message": f"Unsupported Google Workspace file type: {mime_type}",
                "mimeType": mime_type,
                "operation": "_export_google_file",
            }

        # Export the file
        try:
            request = self.service.files().export_media(
                fileId=file_id, mimeType=export_mime_type
            )

            content_bytes = self._download_content(request)
            if isinstance(content_bytes, dict) and content_bytes.get("error"):
                return content_bytes

            # Process the content based on MIME type
            if export_mime_type.startswith("text/"):
                try:
                    content = content_bytes.decode("utf-8")
                    return {
                        "file_id": file_id,
                        "name": file_name,
                        "mime_type": export_mime_type,
                        "content": content,
                        "encoding": "utf-8",
                    }
                except UnicodeDecodeError:
                    content = base64.b64encode(content_bytes).decode("utf-8")
                    return {
                        "file_id": file_id,
                        "name": file_name,
                        "mime_type": export_mime_type,
                        "content": content,
                        "encoding": "base64",
                    }
            else:
                content = base64.b64encode(content_bytes).decode("utf-8")
                return {
                    "file_id": file_id,
                    "name": file_name,
                    "mime_type": export_mime_type,
                    "content": content,
                    "encoding": "base64",
                }
        except Exception as e:
            return self.handle_api_error("_export_google_file", e)

    def _download_regular_file(
        self, file_id: str, file_name: str, mime_type: str
    ) -> dict[str, Any]:
        """Download a regular (non-Google Workspace) file."""
        request = self.service.files().get_media(fileId=file_id, supportsAllDrives=True)

        content_bytes = self._download_content(request)
        if isinstance(content_bytes, dict) and content_bytes.get("error"):
            return content_bytes

        # Process text files
        if mime_type.startswith("text/") or mime_type == "application/json":
            try:
                content = content_bytes.decode("utf-8")
                return {
                    "file_id": file_id,
                    "name": file_name,
                    "mime_type": mime_type,
                    "content": content,
                    "encoding": "utf-8",
                }
            except UnicodeDecodeError:
                logger.warning(
                    f"UTF-8 decoding failed for file {file_id} ('{file_name}', {mime_type}). Using base64."
                )
                content = base64.b64encode(content_bytes).decode("utf-8")
                return {
                    "file_id": file_id,
                    "name": file_name,
                    "mime_type": mime_type,
                    "content": content,
                    "encoding": "base64",
                }
        else:
            # Binary file
            content = base64.b64encode(content_bytes).decode("utf-8")
            return {
                "file_id": file_id,
                "name": file_name,
                "mime_type": mime_type,
                "content": content,
                "encoding": "base64",
            }

    def _download_content(self, request) -> bytes:
        """Download content from a request."""
        try:
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            return fh.getvalue()

        except Exception as e:
            return self.handle_api_error("download_content", e)

    def upload_file_content(
        self,
        filename: str,
        content_base64: str,
        parent_folder_id: str | None = None,
        shared_drive_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Upload a file to Google Drive using its content.

        Args:
            filename: The name for the file in Google Drive.
            content_base64: Base64 encoded content of the file.
            parent_folder_id: Optional parent folder ID.
            shared_drive_id: Optional shared drive ID.

        Returns:
            Dict containing file metadata on success, or error information on failure.
        """
        try:
            logger.info(f"Uploading file '{filename}' from content.")

            # Decode the base64 content
            try:
                content_bytes = base64.b64decode(content_base64, validate=True)
            except (ValueError, TypeError, binascii.Error) as e:
                logger.error(f"Invalid base64 content for file '{filename}': {e}")
                return {
                    "error": True,
                    "error_type": "invalid_content",
                    "message": "Invalid base64 encoded content provided.",
                    "operation": "upload_file_content",
                }

            # Get file MIME type from filename
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type is None:
                mime_type = "application/octet-stream"

            file_metadata = {"name": filename}
            if parent_folder_id:
                file_metadata["parents"] = [parent_folder_id]
            elif shared_drive_id:
                file_metadata["parents"] = [shared_drive_id]

            # Use MediaIoBaseUpload for in-memory content
            media = MediaIoBaseUpload(io.BytesIO(content_bytes), mimetype=mime_type)

            create_params = {
                "body": file_metadata,
                "media_body": media,
                "fields": "id,name,mimeType,modifiedTime,size,webViewLink",
                "supportsAllDrives": True,
            }
            if shared_drive_id:
                create_params["driveId"] = shared_drive_id

            file = self.service.files().create(**create_params).execute()

            logger.info(f"Successfully uploaded file with ID: {file.get('id')}")
            return file

        except HttpError as e:
            return self.handle_api_error("upload_file_content", e)
        except Exception as e:
            logger.error(f"Non-API error in upload_file_content: {str(e)}")
            return {
                "error": True,
                "error_type": "local_error",
                "message": f"Error uploading file from content: {str(e)}",
                "operation": "upload_file_content",
            }

    def delete_file(self, file_id: str) -> dict[str, Any]:
        """
        Delete a file from Google Drive.

        Args:
            file_id: The ID of the file to delete

        Returns:
            Dict containing success status or error information
        """
        try:
            if not file_id:
                return {"success": False, "message": "File ID cannot be empty"}

            logger.info(f"Deleting file with ID: {file_id}")
            self.service.files().delete(fileId=file_id).execute()

            return {"success": True, "message": f"File {file_id} deleted successfully"}

        except Exception as e:
            return self.handle_api_error("delete_file", e)

    def list_shared_drives(self, page_size: int = 100) -> list[dict[str, Any]]:
        """
        Lists the user's shared drives.

        Args:
            page_size: Maximum number of shared drives to return. Max is 100.

        Returns:
            List of shared drive metadata dictionaries (id, name) or an error dictionary.
        """
        try:
            logger.info(f"Listing shared drives with page size: {page_size}")
            # API allows pageSize up to 100 for drives.list
            actual_page_size = min(max(1, page_size), 100)

            results = (
                self.service.drives()
                .list(pageSize=actual_page_size, fields="drives(id, name, kind)")
                .execute()
            )
            drives = results.get("drives", [])

            # Filter for kind='drive#drive' just to be sure, though API should only return these
            processed_drives = [
                {"id": d.get("id"), "name": d.get("name")}
                for d in drives
                if d.get("kind") == "drive#drive" and d.get("id") and d.get("name")
            ]
            logger.info(f"Found {len(processed_drives)} shared drives.")
            return processed_drives
        except HttpError as error:
            logger.error(f"Error listing shared drives: {error}")
            return self.handle_api_error("list_shared_drives", error)
        except Exception as e:
            logger.exception("Unexpected error listing shared drives")
            return {
                "error": True,
                "error_type": "unexpected_service_error",
                "message": str(e),
                "operation": "list_shared_drives",
            }

    def share_file_with_domain(
        self, file_id: str, domain: str, role: str = "reader"
    ) -> dict[str, Any]:
        """
        Shares a file with an entire domain.

        Args:
            file_id: The ID of the file to share.
            domain: The domain to share the file with (e.g., 'example.com').
            role: The permission role ('reader', 'commenter', 'writer'). Defaults to 'reader'.

        Returns:
            A dictionary containing the permission details or an error dictionary.
        """
        try:
            if not file_id or not domain:
                raise ValueError("File ID and domain are required.")

            logger.info(
                f"Sharing file {file_id} with domain '{domain}' as role '{role}'"
            )

            permission = {"type": "domain", "role": role, "domain": domain}

            # Create the permission
            permission_result = (
                self.service.permissions()
                .create(
                    fileId=file_id,
                    body=permission,
                    sendNotificationEmail=False,  # Avoid spamming the domain
                    supportsAllDrives=True,
                )
                .execute()
            )

            logger.info(
                f"Successfully created domain permission ID: {permission_result.get('id')}"
            )
            return {
                "success": True,
                "file_id": file_id,
                "permission_id": permission_result.get("id"),
                "domain": domain,
                "role": role,
            }

        except HttpError as error:
            # Check for a 403 error related to sharing policies
            if error.resp.status == 403:
                error_content = error.content.decode("utf-8")
                if (
                    "cannotShareTeamDriveItem" in error_content
                    or "sharingRateLimitExceeded" in error_content
                ):
                    logger.error(
                        f"Domain sharing policy prevents sharing file {file_id}: {error_content}"
                    )
                    # Return a more specific error message
                    return self.handle_api_error(
                        "share_file_with_domain_policy_error", error
                    )

            return self.handle_api_error("share_file_with_domain", error)
        except Exception as e:
            return self.handle_api_error("share_file_with_domain", e)

    def _get_or_create_data_folder(self) -> str:
        """
        Finds the dedicated folder for storing chart data, creating it if it doesn't exist.
        The result is cached to avoid repeated API calls within the same session.

        Returns:
            The ID of the data folder.
        """
        folder_name = "[MCP] Generated Chart Data"
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

        logger.info(f"Searching for data folder: '{folder_name}'")
        search_result = self.search_files(query=query, page_size=1)

        if search_result and len(search_result) > 0:
            folder_id = search_result[0]["id"]
            logger.info(f"Found existing data folder with ID: {folder_id}")
            return folder_id
        logger.info("Data folder not found. Creating a new one.")
        create_result = self.create_folder(folder_name=folder_name)
        if create_result and not create_result.get("error"):
            folder_id = create_result["id"]
            logger.info(f"Successfully created data folder with ID: {folder_id}")
            return folder_id
        raise RuntimeError(
            "Failed to create the necessary data folder in Google Drive."
        )
