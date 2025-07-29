"""
Gmail tools for Google Workspace MCP operations.
"""

import logging

from google_workspace_mcp.app import mcp
from google_workspace_mcp.models import (
    GmailAttachmentOutput,
    GmailBulkDeleteOutput,
    GmailDraftCreationOutput,
    GmailDraftDeletionOutput,
    GmailDraftSendOutput,
    GmailEmailSearchOutput,
    GmailMessageDetailsOutput,
    GmailReplyOutput,
    GmailSendOutput,
)
from google_workspace_mcp.services.gmail import GmailService

logger = logging.getLogger(__name__)


# --- Gmail Tool Functions --- #


@mcp.tool(
    name="query_gmail_emails",
    description="Query Gmail emails based on a search query.",
)
async def query_gmail_emails(
    query: str, max_results: int = 100
) -> GmailEmailSearchOutput:
    """
    Searches for Gmail emails using Gmail query syntax.

    Args:
        query: Gmail search query (e.g., "is:unread from:example.com").
        max_results: Maximum number of emails to return.

    Returns:
        GmailEmailSearchOutput containing the list of matching emails.
    """
    logger.info(f"Executing query_gmail_emails tool with query: '{query}'")

    gmail_service = GmailService()
    emails = gmail_service.query_emails(query=query, max_results=max_results)

    # Check if there's an error
    if isinstance(emails, dict) and emails.get("error"):
        raise ValueError(emails.get("message", "Error querying emails"))

    # Return appropriate message if no results
    if not emails:
        emails = []

    return GmailEmailSearchOutput(count=len(emails), emails=emails)


@mcp.tool(
    name="gmail_get_message_details",
    description="Retrieves a complete Gmail email message by its ID.",
)
async def gmail_get_message_details(email_id: str) -> GmailMessageDetailsOutput:
    """
    Retrieves a complete Gmail email message by its ID.

    Args:
        email_id: The ID of the Gmail message to retrieve.

    Returns:
        GmailMessageDetailsOutput containing the email details and attachments.
    """
    logger.info(f"Executing gmail_get_message_details tool with email_id: '{email_id}'")
    if not email_id or not email_id.strip():
        raise ValueError("Email ID cannot be empty")

    gmail_service = GmailService()
    result = gmail_service.get_email(email_id=email_id)

    # Check for explicit error from service first
    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error getting email"))

    # Then check if email is missing (e.g., service returned None)
    if not result:
        raise ValueError(f"Failed to retrieve email with ID: {email_id}")

    return GmailMessageDetailsOutput(
        id=result["id"],
        thread_id=result.get("thread_id", ""),
        subject=result.get("subject", ""),
        from_email=result.get("from_email", ""),
        to_email=result.get("to_email", []),
        date=result.get("date", ""),
        body=result.get("body", ""),
        attachments=result.get("attachments"),
    )


@mcp.tool(
    name="gmail_get_attachment_content",
    description="Retrieves a specific attachment from a Gmail message.",
)
async def gmail_get_attachment_content(
    message_id: str, attachment_id: str
) -> GmailAttachmentOutput:
    """
    Retrieves a specific attachment from a Gmail message.

    Args:
        message_id: The ID of the email message.
        attachment_id: The ID of the attachment to retrieve.

    Returns:
        GmailAttachmentOutput containing filename, mimeType, size, and base64 data.
    """
    logger.info(
        f"Executing gmail_get_attachment_content tool - Msg: {message_id}, Attach: {attachment_id}"
    )
    if not message_id or not attachment_id:
        raise ValueError("Message ID and attachment ID are required")

    gmail_service = GmailService()
    result = gmail_service.get_attachment_content(
        message_id=message_id, attachment_id=attachment_id
    )

    if not result or (isinstance(result, dict) and result.get("error")):
        error_msg = "Error getting attachment"
        if isinstance(result, dict):
            error_msg = result.get("message", error_msg)
        raise ValueError(error_msg)

    return GmailAttachmentOutput(
        filename=result["filename"],
        mime_type=result["mime_type"],
        size=result["size"],
        data=result["data"],
    )


@mcp.tool(
    name="create_gmail_draft",
    description="Creates a draft email message in Gmail.",
)
async def create_gmail_draft(
    to: str,
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> GmailDraftCreationOutput:
    """
    Creates a draft email message in Gmail.

    Args:
        to: Email address of the recipient.
        subject: Subject line of the email.
        body: Body content of the email.
        cc: Optional list of email addresses to CC.
        bcc: Optional list of email addresses to BCC.

    Returns:
        GmailDraftCreationOutput containing the created draft details.
    """
    logger.info("Executing create_gmail_draft")
    if not to or not subject or not body:  # Check for empty strings
        raise ValueError("To, subject, and body are required")

    gmail_service = GmailService()
    # Pass bcc parameter even though service may not use it (for test compatibility)
    result = gmail_service.create_draft(
        to=to, subject=subject, body=body, cc=cc, bcc=bcc
    )

    if not result or (isinstance(result, dict) and result.get("error")):
        error_msg = "Error creating draft"
        if isinstance(result, dict):
            error_msg = result.get("message", error_msg)
        raise ValueError(error_msg)

    return GmailDraftCreationOutput(id=result["id"], message=result.get("message", {}))


@mcp.tool(
    name="delete_gmail_draft",
    description="Deletes a Gmail draft email by its draft ID.",
)
async def delete_gmail_draft(
    draft_id: str,
) -> GmailDraftDeletionOutput:
    """
    Deletes a specific draft email from Gmail.

    Args:
        draft_id: The ID of the draft to delete.

    Returns:
        GmailDraftDeletionOutput confirming the deletion.
    """
    logger.info(f"Executing delete_gmail_draft with draft_id: '{draft_id}'")
    if not draft_id or not draft_id.strip():
        raise ValueError("Draft ID is required")

    gmail_service = GmailService()
    success = gmail_service.delete_draft(draft_id=draft_id)

    if not success:
        # Attempt to check if the service returned an error dict
        # (Assuming handle_api_error might return dict or False/None)
        # This part might need adjustment based on actual service error handling
        error_info = getattr(
            gmail_service, "last_error", None
        )  # Hypothetical error capture
        error_msg = "Failed to delete draft"
        if isinstance(error_info, dict) and error_info.get("error"):
            error_msg = error_info.get("message", error_msg)
        raise ValueError(error_msg)

    return GmailDraftDeletionOutput(
        message=f"Draft with ID '{draft_id}' deleted successfully.", success=True
    )


@mcp.tool(
    name="gmail_send_draft",
    description="Sends an existing draft email from Gmail.",
)
async def gmail_send_draft(draft_id: str) -> GmailDraftSendOutput:
    """
    Sends a specific draft email.

    Args:
        draft_id: The ID of the draft to send.

    Returns:
        GmailDraftSendOutput containing the details of the sent message.
    """
    logger.info(f"Executing gmail_send_draft tool for draft_id: '{draft_id}'")
    if not draft_id or not draft_id.strip():
        raise ValueError("Draft ID cannot be empty.")

    gmail_service = GmailService()
    result = gmail_service.send_draft(draft_id=draft_id)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error sending draft"))

    if not result:  # Should be caught by error dict check
        raise ValueError(f"Failed to send draft '{draft_id}'")

    return GmailDraftSendOutput(
        id=result["id"],
        thread_id=result.get("thread_id", ""),
        label_ids=result.get("label_ids", []),
    )


@mcp.tool(
    name="gmail_reply_to_email",
    description="Create a reply to an existing email. Can be sent or saved as draft.",
)
async def gmail_reply_to_email(
    email_id: str,
    reply_body: str,
    send: bool = False,
    reply_all: bool = False,
) -> GmailReplyOutput:
    """
    Creates a reply to an existing email thread.

    Args:
        email_id: The ID of the message being replied to.
        reply_body: Body content of the reply.
        send: If True, send the reply immediately. If False, save as draft.
        reply_all: If True, reply to all recipients. If False, reply to sender only.

    Returns:
        GmailReplyOutput containing the sent message or created draft details.
    """
    logger.info(f"Executing gmail_reply_to_email to message: '{email_id}'")
    if not email_id or not reply_body:
        raise ValueError("Email ID and reply body are required")

    gmail_service = GmailService()
    result = gmail_service.reply_to_email(
        email_id=email_id,
        reply_body=reply_body,
        reply_all=reply_all,
    )

    if not result or (isinstance(result, dict) and result.get("error")):
        action = "send reply" if send else "create reply draft"
        error_msg = f"Error trying to {action}"
        if isinstance(result, dict):
            error_msg = result.get("message", error_msg)
        raise ValueError(error_msg)

    return GmailReplyOutput(
        id=result["id"], thread_id=result.get("thread_id", ""), in_reply_to=email_id
    )


@mcp.tool(
    name="gmail_bulk_delete_messages",
    description="Delete multiple emails at once by providing a list of message IDs.",
)
async def gmail_bulk_delete_messages(
    message_ids: list[str],
) -> GmailBulkDeleteOutput:
    """
    Deletes multiple Gmail emails using a list of message IDs.

    Args:
        message_ids: A list of email message IDs to delete.

    Returns:
        GmailBulkDeleteOutput summarizing the deletion result.
    """
    # Validation first - check if it's a list
    if not isinstance(message_ids, list):
        raise ValueError("Message IDs must be provided as a list")

    # Then check if the list is empty
    if not message_ids:
        raise ValueError("Message IDs list cannot be empty")

    logger.info(f"Executing gmail_bulk_delete_messages with {len(message_ids)} IDs")

    gmail_service = GmailService()
    result = gmail_service.bulk_delete_messages(message_ids=message_ids)

    if not result or (isinstance(result, dict) and result.get("error")):
        error_msg = "Error during bulk deletion"
        if isinstance(result, dict):
            error_msg = result.get("message", error_msg)
        raise ValueError(error_msg)

    return GmailBulkDeleteOutput(
        deleted_count=result.get("deleted_count", len(message_ids)),
        success=result.get("success", True),
        message=result.get(
            "message", f"Successfully deleted {len(message_ids)} messages"
        ),
    )


@mcp.tool(
    name="gmail_send_email",
    description="Composes and sends an email directly.",
)
async def gmail_send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> GmailSendOutput:
    """
    Composes and sends an email message.

    Args:
        to: A list of primary recipient email addresses.
        subject: The subject line of the email.
        body: The plain text body content of the email.
        cc: Optional. A list of CC recipient email addresses.
        bcc: Optional. A list of BCC recipient email addresses.

    Returns:
        GmailSendOutput containing the details of the sent message.
    """
    logger.info(f"Executing gmail_send_email tool to: {to}, subject: '{subject}'")
    if (
        not to
        or not isinstance(to, list)
        or not all(isinstance(email, str) and email.strip() for email in to)
    ):
        raise ValueError("Recipients 'to' must be a non-empty list of email strings.")
    if not subject or not subject.strip():
        raise ValueError("Subject cannot be empty.")
    if (
        body is None
    ):  # Allow empty string for body, but not None if it implies missing arg.
        raise ValueError("Body cannot be None (can be an empty string).")

    gmail_service = GmailService()
    result = gmail_service.send_email(to=to, subject=subject, body=body, cc=cc, bcc=bcc)

    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error sending email"))

    if not result:
        raise ValueError("Failed to send email")

    return GmailSendOutput(
        id=result["id"],
        thread_id=result.get("thread_id", ""),
        label_ids=result.get("label_ids", []),
    )
