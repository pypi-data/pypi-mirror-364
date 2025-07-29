import re
import argparse

def test_regex(pattern, test_string):
    try:
        matches = re.findall(pattern, test_string)
        return matches
    except re.error as e:
        return f"Invalid regex: {e}"

def main():
    parser = argparse.ArgumentParser(description="Regex Tester CLI")
    parser.add_argument("pattern", help="Regex pattern")
    parser.add_argument("string", help="String to test the regex on")

    args = parser.parse_args()
    result = test_regex(args.pattern, args.string)
    print("Matches:", result)

if __name__ == "__main__":
    main()
