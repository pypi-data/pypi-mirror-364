import argparse
import asyncio
import csv
import os
import re
import sys
import serial
import pandas as pd


# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Read and clean ROV serial data.")
    parser.add_argument('-c', '--com-port', default='COM3',
                        help="COM port to read from (e.g. COM3, COM1)")
    parser.add_argument('-b', '--baud-rate', default=9600,        type=int,
                        help="Sets the baud rate for reading from the serial port e.g. 9600, 19200, 38400 etc. defaults to 9600 ")
    parser.add_argument('-r', '--raw-output-path', default='RAW.csv',
                        help="Output path for the RAW CSV file")
    parser.add_argument('-o', '--cleaned-output-path', default='CLEANED.csv',
                        help="Output path for the CLEANED CSV file")
    parser.add_argument('-i', '--clean-interval', type=int, default=1,
                        help="Interval (in seconds) between cleaning RAW to CLEANED")
    parser.add_argument("-g", "--gpnmea", nargs='+', default=["GPDPT 1", "GPRMC 3", "GPRMC 5"],
                        help="The NMEA sentence and column to extract (e.g. 'GPRMC 3', 'GPDPT 1' Use 1 if it only has one value like depth. It is zero-indexed (i.e. if you want the 1st column you'd put 0 and if you wanted the 2nd you'd put 1 etc.))")
    return parser.parse_args()


def validate_nmea_sentences(gpnmea_args):
    pattern = re.compile(r"^[A-Z]{3,5}\s(\d{1,3})(,\d{1,3})*$")
    for item in gpnmea_args:
        if not pattern.match(item):
            print(
                f"Error: Invalid NMEA format '{item}'. Must be like 'GPRMC 3' or 'GPRMC 1,3,5'.")
            sys.exit(1)
        cols = item.split()[1].split(',')
        for col in cols:
            num = int(col)
            if num < 1 or num > 100:
                print(
                    f"Error: NMEA column out of range in '{item}'. Must be between 1 and 100.")
                sys.exit(1)

# Function to check if new data is available for cleaning
def is_new_data_available(raw_output_path):
    """
    Checks if any new data has been put into the raw file for cleaning
    """
    try:
        # Get the last line from the RAW.csv file
        with open(raw_output_path, 'r') as file:
            lines = file.readlines()
            # Check if there's a new line (i.e., if the last line is different from the last processed one)
            if len(lines) > 1:
                # New data is available (since there is more than one line)
                return True
    except FileNotFoundError:
        return False  # If the file doesn't exist, assume there's no data
    return False  # No new data if only one line is present


async def read_serial(com_port, baud_rate, data_queue):
    """
    Reads the data being written to a certain serial port and queues it up to be written to file
    """
    # Open the serial port
    with serial.Serial(com_port, baud_rate, timeout=1) as ser:
        while True:
            line = ser.readline()
            print(f"RAW feed: {line}")
            if line:
                await data_queue.put(line)
            await asyncio.sleep(0.1)


async def save_raw_log(raw_output_path, data_queue):
    """
    Saves the incoming raw feed, and batch saves it to the specified output path
    """
    if not os.path.exists(raw_output_path):
        print(f"Creating {raw_output_path}...")
        with open(raw_output_path, mode="wb") as file:
            pass
    while True:
        line = await data_queue.get()
        if line:
            with open(raw_output_path, mode='ab') as file:
                file.write(line)


async def clean_raw_log(raw_output_path, cleaned_output_path, header_args):
    """
    For each requested NMEA sentence/column, walk backwards through RAW.csv
    until you find a non-empty field, then write exactly one row (no header)
    to CLEANED.csv containing those latest values.
    """
    try:
        # Read all non-empty lines from RAW.csv
        with open(raw_output_path, "r", errors="replace") as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            print("No data in RAW file.")
            return

        latest_values = {}

        for item in header_args:
            sentence, cols = item.split()
            indices = [int(i.strip())
                       for i in cols.split(",") if i.strip().isdigit()]
            value_map = {}

            for raw_line in reversed(lines):
                parts = raw_line.split(',')
                if parts and parts[0].strip().upper().startswith(f'${sentence}'.upper()):
                    for idx in indices:
                        if f"{sentence}_{idx}" not in value_map:
                            if idx < len(parts) and parts[idx].strip():
                                value_map[f"{sentence}_{idx}"] = parts[idx].strip()
                    if len(value_map) == len(indices):
                        break

            for key in [f"{sentence}_{i}" for i in indices]:
                latest_values[key] = value_map.get(key, "")

        # Single-row DataFrame
        df = pd.DataFrame([latest_values])

        # Overwrite CLEANED.csv with just this row, no header, no index
        df.to_csv(cleaned_output_path, mode='w', header=False, index=False)
        print(f"Wrote latest cleaned data to {cleaned_output_path}")

    except Exception as e:
        print(f"Error in cleaning the log: {e}")


# Main async function
async def main():
    # Parse arguments
    args = parse_args()
    validate_nmea_sentences(args.gpnmea)
    if not args.com_port or not args.raw_output_path or not args.cleaned_output_path:
        print("Error: Missing required arguments.")
        return    # Read serial data and save to RAW file
    print("Starting...")
    data_queue = asyncio.Queue(maxsize=1000)
    # start the serial reading task
    # read_task = asyncio.create_task(read_from_file(file_path="INCOMING.csv",data_queue=data_queue))
    read_task = asyncio.create_task(read_serial(
        args.com_port, args.baud_rate, data_queue))
    # start the raw log saving task
    save_task = asyncio.create_task(
        save_raw_log(args.raw_output_path, data_queue))

    try:
        # Periodically clean the raw data and save it to CLEANED file
        while True:
            # Wait for the clean interval
            await asyncio.sleep(args.clean_interval)
            print(f"Cleaning data every {args.clean_interval} seconds...")
            await clean_raw_log(args.raw_output_path, args.cleaned_output_path, args.gpnmea)
    except asyncio.CancelledError:
        print("\nShutting down tasks...")
        read_task.cancel()
        save_task.cancel()
        print("\nExiting...")
        await asyncio.gather(read_task, save_task, return_exceptions=True)


def cli():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


# Entry point of the script
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
