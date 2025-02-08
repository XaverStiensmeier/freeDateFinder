import argparse
import requests
from icalendar import Calendar

def fetch_ical(url):
    """Fetch iCalendar from a URL and return the parsed Calendar object."""
    response = requests.get(url)
    if response.status_code == 200:
        return Calendar.from_ical(response.content)
    else:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return None

def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description='Load iCalendar files from URLs and parse them.')
    parser.add_argument('--links', metavar='URL', type=str, nargs='+',
                        help='List of URLs pointing to iCalendar (.ics) files')
    args = parser.parse_args()

    # Process each iCalendar URL
    for url in args.links:
        print(f"Loading iCalendar from: {url}")
        calendar = fetch_ical(url)
        
        if calendar:
            print(f"Successfully loaded calendar from {url}.")
            # Print the events (or other relevant data from the calendar)
            for component in calendar.walk():
                if component.name == "VEVENT":
                    print(f"Event: {component.get('summary')}")
                    print(f"Start: {component.get('dtstart').dt}")
                    print(f"End: {component.get('dtend').dt}")
                    print('---')
        print()

if __name__ == "__main__":
    main()