#!/usr/bin/env python3
"""
Command-line interface for WikiRaces.
"""
import argparse
import sys
from wikiraces import WikiBot


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered Wikipedia navigation using semantic similarity"
    )
    parser.add_argument(
        "source",
        help="Source Wikipedia article title"
    )
    parser.add_argument(
        "destination", 
        help="Destination Wikipedia article title"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="Maximum number of candidate links to consider at each step (default: 15)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"🏁 WikiRaces: Finding path from '{args.source}' to '{args.destination}'")
        print("=" * 60)
        
        bot = WikiBot(args.source, args.destination, limit=args.limit)
        success = bot.run()
        
        print("\n" + "=" * 60)
        if success:
            print(f"✅ Success! Found path in {len(bot.path) - 1} steps")
        else:
            print("❌ Could not find a path to the destination")
            
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Navigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
