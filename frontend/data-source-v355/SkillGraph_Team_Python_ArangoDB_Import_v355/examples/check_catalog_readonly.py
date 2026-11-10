"""Read-only Python catalog smoke test. Standard library only. Never hard-code credentials."""
import argparse
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from arango_s23_common import ArangoHTTP, ArangoError


def main():
    ap = argparse.ArgumentParser(description="Quick read-only check for a local Skill Graph ArangoDB")
    ap.add_argument("--host", default="http://127.0.0.1:8529")
    ap.add_argument("--database", default="skill_graph_team_preview_v355")
    ap.add_argument("--username", default="root")
    args = ap.parse_args()
    client = ArangoHTTP(args.host, args.username)
    try:
        careers = client.aql(args.database, "FOR c IN careers SORT c.name LIMIT 5 RETURN {id:c._id,name:c.name}")
        courses = client.aql(args.database, "FOR c IN courses COLLECT WITH COUNT INTO n RETURN n")[0]
        print("READ-ONLY CATALOG PASS | sample careers:", careers)
        print("READ-ONLY CATALOG PASS | resource count:", courses)
        return 0
    except (ArangoError, KeyError, ValueError, IndexError) as e:
        print("READ-ONLY CATALOG FAILED:", e, file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
