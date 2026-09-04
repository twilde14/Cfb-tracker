"""
Pulls the upcoming week of college football games (FBS + FCS) from ESPN's
public scoreboard API and writes them to data.json for the planner site.

This uses an UNDOCUMENTED ESPN endpoint. It's the same data ESPN's own
scoreboard page uses, but ESPN could change its shape at any time without
notice -- if this script starts failing, that's the most likely reason.

No API key required.
"""

import json
import sys
from datetime import datetime, timedelta, timezone

import requests

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
# ESPN "groups" params: 80 = FBS, 81 = FCS
GROUPS = ["80", "81"]
DAYS_AHEAD = 7          # how many days forward (from today) to pull
REQUEST_TIMEOUT = 15


def fetch_day(date_str, group):
    """Fetch one calendar day (YYYYMMDD) for one division group."""
    params = {"dates": date_str, "groups": group, "limit": 400}
    try:
        resp = requests.get(SCOREBOARD_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json().get("events", [])
    except requests.RequestException as e:
        print(f"  ! request failed for {date_str} group {group}: {e}", file=sys.stderr)
        return []


def extract_game(event):
    try:
        comp = event["competitions"][0]
        competitors = comp["competitors"]
        home = next(c for c in competitors if c["homeAway"] == "home")
        away = next(c for c in competitors if c["homeAway"] == "away")

        def team_name(c):
            return c["team"].get("shortDisplayName") or c["team"].get("displayName", "TBD")

        def rank(c):
            r = c.get("curatedRank", {}).get("current")
            return r if isinstance(r, int) and 1 <= r <= 25 else None

        # Broadcast network(s)
        broadcasts = comp.get("broadcasts", [])
        if broadcasts and broadcasts[0].get("names"):
            network = "/".join(broadcasts[0]["names"])
        else:
            network = "TBA"

        # Odds / spread (not always present, especially far out or small games)
        spread = None
        odds_list = comp.get("odds", [])
        if odds_list:
            details = odds_list[0].get("details")
            if details and details.lower() != "even":
                spread = details

        note = None
        if comp.get("neutralSite"):
            venue = comp.get("venue", {}).get("fullName")
            note = f"Neutral site{f' — {venue}' if venue else ''}"

        return {
            "id": event["id"],
            "start_utc": event["date"],  # ISO 8601, UTC
            "away": team_name(away),
            "home": team_name(home),
            "away_rank": rank(away),
            "home_rank": rank(home),
            "network": network,
            "spread": spread,
            "note": note,
        }
    except (KeyError, StopIteration, IndexError) as e:
        print(f"  ! skipped a game, unexpected shape: {e}", file=sys.stderr)
        return None


def main():
    today = datetime.now(timezone.utc).date()
    dates = [today + timedelta(days=i) for i in range(DAYS_AHEAD)]

    games_by_id = {}
    for d in dates:
        date_str = d.strftime("%Y%m%d")
        for group in GROUPS:
            events = fetch_day(date_str, group)
            for event in events:
                game = extract_game(event)
                if game:
                    games_by_id[game["id"]] = game  # de-dupe across group pulls

    games = sorted(games_by_id.values(), key=lambda g: g["start_utc"])

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        "range_start": dates[0].isoformat(),
        "range_end": dates[-1].isoformat(),
        "games": games,
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(games)} games to data.json ({dates[0]} to {dates[-1]})")


if __name__ == "__main__":
    main()
