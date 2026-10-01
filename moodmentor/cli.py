import argparse


def main():
    parser = argparse.ArgumentParser(
        description="MoodMentor - AI Employee Wellness Platform"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="MoodMentor 1.0.0"
    )

    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze an emotional text"
    )

    args = parser.parse_args()

    if args.analyze:
        print("MoodMentor Emotion Analysis")
        print("----------------------------")
        print("Input:", args.analyze)
        print("Status: Analysis request received")
        print("MoodMentor CLI executed successfully.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()