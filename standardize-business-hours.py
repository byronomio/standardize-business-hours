import csv
import re
from datetime import datetime

# Paths to the input and output CSV files
input_file_path = 'path_to_input.csv'
output_file_path = 'path_to_output.csv'

def convert_to_24hr(time_str):
    """
    Converts time from 12-hour AM/PM format to 24-hour format.
    
    Args:
        time_str (str): The time string in 12-hour format.
    
    Returns:
        str: The time string converted to 24-hour format or the original string if conversion fails.
    """
    try:
        # Attempt to parse and convert time with minutes and AM/PM
        return datetime.strptime(time_str.strip(), "%I:%M%p").strftime("%H:%M")
    except ValueError:
        try:
            # Attempt to parse and convert time without minutes (e.g., '8am')
            return datetime.strptime(time_str.strip(), "%I%p").strftime("%H:%M")
        except ValueError:
            # Return the original string if both conversion attempts fail
            return time_str  

def parse_availability(availability):
    """
    Parses the availability string to extract structured information about scheduling, such as days and times of operation.
    
    Args:
        availability (str): The raw availability string from the CSV file.
    
    Returns:
        tuple: Contains structured data (day_from, day_to, time_from, time_to, notes).
    """
    # Initialize default values
    day_from, day_to, time_from, time_to, notes = '', '', '', '', ''
    
    # Check for and handle special cases that do not follow typical time range formats
    if any(word in availability.lower() for word in ["by appointment", "24/7", "24 hours"]):
        notes = availability
    else:
        # Regular expression to find day names
        day_pattern = re.compile(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)')
        days = day_pattern.findall(availability)
        if days:
            day_from = days[0]
            day_to = days[-1] if len(days) > 1 else day_from
        
        # Regular expression to find time ranges
        time_pattern = re.compile(r'(\d{1,2}(?::\d{2})?(?:am|pm|AM|PM)?)-(\d{1,2}(?::\d{2})?(?:am|pm|AM|PM)?)')
        time_match = time_pattern.search(availability)
        if time_match:
            time_from = convert_to_24hr(time_match.group(1))
            time_to = convert_to_24hr(time_match.group(2))

    return day_from, day_to, time_from, time_to, notes

def standardize_availability(file_path, output_file_path):
    """
    Reads an input CSV file and processes each 'Availability' entry to standardize and structure it, 
    then writes the results to a new CSV file with additional structured columns.
    
    Args:
        file_path (str): Path to the input CSV file.
        output_file_path (str): Path to the output CSV file.
    """
    with open(file_path, newline='', encoding='utf-8') as infile, \
         open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile, delimiter=';', quotechar='"')
        fieldnames = reader.fieldnames + ['Day From', 'Day To', 'Time From', 'Time To', 'Notes']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        for row in reader:
            availability = row['Availability'].strip()
            day_from, day_to, time_from, time_to, notes = parse_availability(availability)
            row.update({
                'Day From': day_from,
                'Day To': day_to,
                'Time From': time_from,
                'Time To': time_to,
                'Notes': notes
            })
            writer.writerow(row)

# Execute the function to process the CSV and standardize availability times
standardize_availability(input_file_path, output_file_path)

print("Availability times have been standardized and structured into separate columns in the new file.")
