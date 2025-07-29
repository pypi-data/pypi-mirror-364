"""
Google Calendar tool handlers for Google Workspace MCP.
"""

import logging

from google_workspace_mcp.app import mcp  # Import from central app module
from google_workspace_mcp.models import (
    CalendarEventCreationOutput,
    CalendarEventDeletionOutput,
    CalendarEventDetailsOutput,
    CalendarEventsOutput,
)
from google_workspace_mcp.services.calendar import CalendarService

logger = logging.getLogger(__name__)


# --- Calendar Tool Functions --- #


# @mcp.tool(
#     name="list_calendars",
#     description="Lists all calendars accessible by the user.",
# )
# async def list_calendars() -> dict[str, Any]:
#     """
#     Lists all calendars accessible by the user.

#     Returns:
#         A dictionary containing the list of calendars or an error message.
#     """
#     logger.info("Executing list_calendars tool")

#     calendar_service = CalendarService()
#     calendars = calendar_service.list_calendars()

#     if isinstance(calendars, dict) and calendars.get("error"):
#         raise ValueError(calendars.get("message", "Error listing calendars"))

#     if not calendars:
#         return {"message": "No calendars found."}

#     # Return raw service result
#     return {"count": len(calendars), "calendars": calendars}


@mcp.tool(
    name="calendar_get_events",
    description="Retrieve calendar events within a specified time range.",
)
async def calendar_get_events(
    time_min: str,
    time_max: str,
    calendar_id: str = "primary",
    max_results: int = 250,
    show_deleted: bool = False,
) -> CalendarEventsOutput:
    """
    Retrieve calendar events within a specified time range.

    Args:
        time_min: Start of time range (ISO datetime string)
        time_max: End of time range (ISO datetime string)
        calendar_id: Calendar identifier (default: 'primary')
        max_results: Maximum number of events to return
        show_deleted: Whether to include deleted events

    Returns:
        CalendarEventsOutput: Structured output containing the events data
    """
    logger.info(f"Executing calendar_get_events tool for calendar {calendar_id}")

    calendar_service = CalendarService()
    result = calendar_service.get_events(
        time_min=time_min,
        time_max=time_max,
        calendar_id=calendar_id,
        max_results=max_results,
        show_deleted=show_deleted,
    )

    # Check for errors in the service result
    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error retrieving calendar events"))

    # Extract events list - the service returns a dict with 'items' key containing events
    events = result.get("items", []) if isinstance(result, dict) else result
    if not events:
        events = []

    # Return the Pydantic model instance
    return CalendarEventsOutput(count=len(events), events=events)


@mcp.tool(
    name="calendar_get_event_details",
    description="Retrieves detailed information for a specific calendar event by its ID.",
)
async def calendar_get_event_details(
    event_id: str, calendar_id: str = "primary"
) -> CalendarEventDetailsOutput:
    """
    Retrieves detailed information for a specific calendar event by its ID.

    Args:
        event_id: The unique identifier of the event
        calendar_id: Calendar identifier (default: 'primary')

    Returns:
        CalendarEventDetailsOutput: Structured output containing the event details
    """
    logger.info(f"Executing calendar_get_event_details tool for event {event_id}")

    calendar_service = CalendarService()
    result = calendar_service.get_event_details(
        event_id=event_id, calendar_id=calendar_id
    )

    # Check for errors in the service result
    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error retrieving event details"))

    if not result:  # Should be caught by error dict check
        raise ValueError(f"Failed to retrieve details for event '{event_id}'")

    # Return the Pydantic model instance
    return CalendarEventDetailsOutput(
        id=result["id"],
        summary=result.get("summary", ""),
        start=result.get("start", {}),
        end=result.get("end", {}),
        description=result.get("description"),
        attendees=result.get("attendees"),
        location=result.get("location"),
    )


@mcp.tool(
    name="create_calendar_event",
    description="Creates a new event in a specified Google Calendar.",
)
async def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    location: str = None,
    description: str = None,
    attendees: list[str] = None,
    send_notifications: bool = True,
    timezone: str = None,
) -> CalendarEventCreationOutput:
    """
    Creates a new event in a specified Google Calendar.

    Args:
        summary: Event title/summary
        start_time: Event start time (ISO datetime string)
        end_time: Event end time (ISO datetime string)
        calendar_id: Calendar identifier (default: 'primary')
        location: Event location (optional)
        description: Event description (optional)
        attendees: List of attendee email addresses (optional)
        send_notifications: Whether to send notifications (default: True)
        timezone: Timezone for the event (optional)

    Returns:
        CalendarEventCreationOutput: Structured output containing the created event data
    """
    logger.info(f"Executing create_calendar_event tool for summary: {summary}")

    calendar_service = CalendarService()
    result = calendar_service.create_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        calendar_id=calendar_id,
        location=location,
        description=description,
        attendees=attendees,
        send_notifications=send_notifications,
        timezone=timezone,
    )

    # Check for errors in the service result
    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error creating calendar event"))

    if not result:
        raise ValueError("Error creating calendar event")

    # Return the Pydantic model instance
    return CalendarEventCreationOutput(
        id=result["id"],
        html_link=result.get("htmlLink", ""),
        summary=result.get("summary", summary),
        start=result.get("start", {}),
        end=result.get("end", {}),
    )


@mcp.tool(
    name="delete_calendar_event",
    description="Deletes an event from Google Calendar by its event ID.",
)
async def delete_calendar_event(
    event_id: str,
    calendar_id: str = "primary",
    send_notifications: bool = True,
) -> CalendarEventDeletionOutput:
    """
    Deletes an event from Google Calendar by its event ID.

    Args:
        event_id: The unique identifier of the event to delete
        calendar_id: Calendar identifier (default: 'primary')
        send_notifications: Whether to send notifications (default: True)

    Returns:
        CalendarEventDeletionOutput: Structured output containing the deletion result
    """
    logger.info(f"Executing delete_calendar_event tool for event {event_id}")

    calendar_service = CalendarService()
    result = calendar_service.delete_event(
        event_id=event_id,
        calendar_id=calendar_id,
        send_notifications=send_notifications,
    )

    # Check for errors in the service result
    if isinstance(result, dict) and result.get("error"):
        raise ValueError(result.get("message", "Error deleting calendar event"))

    # Return the Pydantic model instance
    return CalendarEventDeletionOutput(
        message=f"Event with ID '{event_id}' deleted successfully from calendar '{calendar_id}'.",
        success=True,
    )
