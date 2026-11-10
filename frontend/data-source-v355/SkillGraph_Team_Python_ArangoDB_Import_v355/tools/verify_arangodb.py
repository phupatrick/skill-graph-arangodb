"""Explicit read-only LIVE verification. A server is REQUIRED to run this tool."""
import argparse,json,sys
from arango_s23_common import ArangoHTTP,ArangoError
from prepare_arangodb import preflight

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--host',default='http://127.0.0.1:8529')
    ap.add_argument('--username',default='root')
    ap.add_argument('--database',default='skill_graph_sprint92_demo')
    args=ap.parse_args()
    _,expected,_=preflight()
    client=ArangoHTTP(args.host,args.username)
    try:
        graph=client.request('GET',client.dbpath(args.database,'/_api/gharial/skill_graph'))
        assert graph['graph']['name']=='skill_graph'
        report={}
        for name,n in expected.items():
            actual=client.aql(args.database,f'FOR d IN {name} COLLECT WITH COUNT INTO n RETURN n')[0]
            report[name]={'expected':n,'actual':actual,'pass':actual==n}
        print(json.dumps(report,ensure_ascii=False,indent=2))
        if not all(v['pass'] for v in report.values()):raise ArangoError('One or more collection counts differ')
        print('LIVE VERIFIED: 24 collections,',sum(v['actual'] for v in report.values()),'records, named graph skill_graph')
        return 0
    except (ArangoError,AssertionError,IndexError,KeyError) as e:
        print('LIVE VERIFICATION FAILED:',e,file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
