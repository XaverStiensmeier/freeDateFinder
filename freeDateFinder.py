import argparse
import requests
from datetime import datetime, timedelta
from icalendar import Calendar

def parse_time(time_str):
    """Parse a time string like '05:00' or '23:30' into a datetime object."""
    return datetime.strptime(time_str, "%H:%M").time()

def parse_date(date_str):
    """Parse a date string like '12.03.24' or '24.01.25' into a datetime object."""
    return datetime.strptime(date_str, "%d.%m.%y").date()

def parse_duration(duration_str):
    """Parse a duration string like '05:13' or '2:00' into a timedelta object."""
    hours, minutes = map(int, duration_str.split(":"))
    return timedelta(hours=hours, minutes=minutes)

def fetch_ical(url):
    """Fetch iCalendar from a URL and return the parsed Calendar object."""
    response = requests.get(url)
    if response.status_code == 200:
        return Calendar.from_ical(response.content)
    else:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return None

def is_time_within_range(time_obj, earliest, latest):
    """Check if a time is within the specified range of 'earliest' and 'latest'."""
    return earliest <= time_obj <= latest

def get_free_intervals(events, start_date, end_date, earliest_time, latest_time, min_length):
    """Find all available intervals that fit the given criteria."""
    free_intervals = []

    # Sort events by start time
    events.sort(key=lambda event: event['start'])

    # Check before the first event
    if events:
        first_event = events[0]
        if first_event['start'].date() >= start_date:
            # The gap before the first event
            gap_start = datetime.combine(first_event['start'].date(), earliest_time)
            gap_end = first_event['start']
            if gap_end - gap_start >= min_length:
                free_intervals.append((gap_start, gap_end))

    # Check gaps between events
    for i in range(1, len(events)):
        prev_event = events[i - 1]
        curr_event = events[i]
        
        gap_start = prev_event['end']
        gap_end = curr_event['start']
        if gap_end.date() >= start_date and gap_start.date() <= end_date:
            # Ensure gap is long enough
            if gap_end - gap_start >= min_length:
                free_intervals.append((gap_start, gap_end))

    # Check after the last event
    if events:
        last_event = events[-1]
        if last_event['end'].date() <= end_date:
            gap_start = last_event['end']
            gap_end = datetime.combine(last_event['end'].date(), latest_time)
            if gap_end - gap_start >= min_length:
                free_intervals.append((gap_start, gap_end))

    return free_intervals

def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description='Load iCalendar files and find free intervals based on the provided criteria.')
    parser.add_argument('--links', metavar='URL', type=str, nargs='+', 
                        help='List of URLs pointing to iCalendar (.ics) files')
    parser.add_argument('--earliest', type=str, default="00:00", help='Earliest available time (HH:MM)')
    parser.add_argument('--latest', type=str, default="23:59", help='Latest available time (HH:MM)')
    parser.add_argument('--start', type=str, required=True, help='Start date in format DD.MM.YY')
    parser.add_argument('--end', type=str, required=True, help='End date in format DD.MM.YY')
    parser.add_argument('--min_length', type=str, required=True, help='Minimum duration of free intervals (HH:MM)')

    args = parser.parse_args()

    # Parse the date range, time range, and min_length
    start_date = parse_date(args.start)
    end_date = parse_date(args.end)
    earliest_time = parse_time(args.earliest)
    latest_time = parse_time(args.latest)
    min_length = parse_duration(args.min_length)

    all_events = []

    # Process each iCalendar URL
    for url in args.links:
        print(f"Loading iCalendar from: {url}")
        calendar = fetch_ical(url)
        
        if calendar:
            # Parse events from the iCalendar
            for component in calendar.walk():
                if component.name == "VEVENT":
                    event_start = component.get('dtstart').dt
                    event_end = component.get('dtend').dt
                    
                    # Filter events that fall within the requested date range
                    if start_date <= event_start.date() <= end_date:
                        all_events.append({
                            'start': event_start,
                            'end': event_end
                        })
            print(f"Successfully loaded calendar from {url}.")

    # Get free intervals
    free_intervals = get_free_intervals(all_events, start_date, end_date, earliest_time, latest_time, min_length)

    # Print the free intervals
    if free_intervals:
        print("\nAvailable free intervals:")
        for start, end in free_intervals:
            print(f"Start: {start}, End: {end}, Duration: {end - start}")
    else:
        print("No free intervals found that match the criteria.")

if __name__ == "__main__":
    main()