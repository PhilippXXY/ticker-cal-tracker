from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional

from src.models.stock_event_model import StockEvent, EventType


def generate_calendar_token() -> str:
    '''
    Generate a unique calendar token for a watchlist.
    
    Returns:
        str: A cryptographically secure random token (URL-safe).
    '''
    # Generate a cryptographically secure random token
    token = secrets.token_urlsafe(32)
    return token


def build_ics(stock_events: List[StockEvent], watchlist_name: str = "Stock Events", reminder_before: Optional[timedelta] = None) -> str:
    '''
    Build an iCalendar (.ics) file from a list of stock events.
    
    Args:
        stock_events: List of StockEvent objects to include in the calendar
        watchlist_name: Name of the watchlist/calendar
        reminder_before: Optional timedelta for alarm/reminder before event
        
    Returns:
        str: Valid iCalendar (.ics) formatted string
    '''
    # iCalendar header
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ticker Calendar Tracker//Stock Events Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{watchlist_name}",
        "X-WR-TIMEZONE:UTC",
        "X-WR-CALDESC:Stock events calendar"
    ]
    
    # Add each stock event as a VEVENT
    for event in stock_events:
        vevent_lines = _create_vevent(event, reminder_before)
        ics_lines.extend(vevent_lines)
    
    # iCalendar footer
    ics_lines.append("END:VCALENDAR")
    
    # Join with CRLF as per RFC 5545
    return "\r\n".join(ics_lines) + "\r\n"


def _create_vevent(event: StockEvent, reminder_before: Optional[timedelta] = None) -> List[str]:
    '''
    Create a VEVENT (calendar event) for a stock event.
    
    Args:
        event: StockEvent object
        reminder_before: Optional timedelta for alarm/reminder before event
        
    Returns:
        List[str]: Lines of the VEVENT in iCalendar format
    '''
    # Format date as YYYYMMDD for all-day events
    event_date_str = event.date.strftime("%Y%m%d")
    
    # Create a unique identifier for the event
    uid = f"{event.stock.symbol}-{event.type.value}-{event_date_str}@tickercaltracker.com"
    
    # Create timestamp for DTSTAMP (current time in UTC)
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Format last_updated as timestamp
    last_updated_str = event.last_updated.strftime("%Y%m%dT%H%M%SZ")
    
    # Create event summary and description based on event type
    summary, description = _get_event_details(event)
    
    vevent_lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{event_date_str}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{description}",
        f"LAST-MODIFIED:{last_updated_str}",
        "STATUS:CONFIRMED",
        "TRANSP:TRANSPARENT",
        f"CATEGORIES:{event.type.value}"
    ]
    
    # Add source if available
    if event.source:
        vevent_lines.append(f"X-SOURCE:{event.source}")
    
    # Add alarm/reminder if specified
    if reminder_before:
        alarm_lines = _create_valarm(reminder_before)
        vevent_lines.extend(alarm_lines)
    
    vevent_lines.append("END:VEVENT")
    
    return vevent_lines


def _get_event_details(event: StockEvent) -> tuple[str, str]:
    '''
    Generate summary and description for a stock event.
    
    Args:
        event: StockEvent object
        
    Returns:
        tuple[str, str]: (summary, description)
    '''
    stock_name = event.stock.name
    ticker = event.stock.symbol
    
    event_type_names = {
        EventType.EARNINGS_ANNOUNCEMENT: "Earnings Announcement",
        EventType.DIVIDEND_EX: "Dividend Ex-Date",
        EventType.DIVIDEND_DECLARATION: "Dividend Declaration",
        EventType.DIVIDEND_RECORD: "Dividend Record Date",
        EventType.DIVIDEND_PAYMENT: "Dividend Payment",
        EventType.STOCK_SPLIT: "Stock Split"
    }
    
    event_name = event_type_names.get(event.type, event.type.value)
    
    summary = f"{ticker}: {event_name}"
    
    description = f"{stock_name} ({ticker}) - {event_name}\\n\\n"
    
    # Add contextual information based on event type
    if event.type == EventType.EARNINGS_ANNOUNCEMENT:
        description += "Company earnings report will be announced."
    elif event.type == EventType.DIVIDEND_EX:
        description += "Ex-dividend date - last day to buy stock to receive the dividend."
    elif event.type == EventType.DIVIDEND_DECLARATION:
        description += "Dividend declaration date - company announces dividend details."
    elif event.type == EventType.DIVIDEND_RECORD:
        description += "Dividend record date - shareholders on record will receive dividend."
    elif event.type == EventType.DIVIDEND_PAYMENT:
        description += "Dividend payment date - dividend will be paid to shareholders."
    elif event.type == EventType.STOCK_SPLIT:
        description += "Stock split effective date."
    
    if event.source:
        description += f"\\n\\nSource: {event.source}"
    
    return summary, description


def _create_valarm(reminder_before: timedelta) -> List[str]:
    '''
    Create a VALARM (alarm/reminder) component.
    
    Args:
        reminder_before: timedelta before the event to trigger the alarm
        
    Returns:
        List[str]: Lines of the VALARM in iCalendar format
    '''
    # Convert timedelta to ISO 8601 duration format
    # Negative duration means before the event
    total_seconds = int(reminder_before.total_seconds())
    
    # Calculate days, hours, minutes
    days = total_seconds // 86400
    remaining = total_seconds % 86400
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    
    # Build duration string
    duration_parts = ["P"]
    if days > 0:
        duration_parts.append(f"{days}D")
    
    if hours > 0 or minutes > 0:
        duration_parts.append("T")
        if hours > 0:
            duration_parts.append(f"{hours}H")
        if minutes > 0:
            duration_parts.append(f"{minutes}M")
    
    # If no components, default to P0D
    if len(duration_parts) == 1:
        duration_parts.append("0D")
    
    duration_str = "".join(duration_parts)
    
    return [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder: Stock event upcoming",
        f"TRIGGER:-{duration_str}",
        "END:VALARM"
    ]