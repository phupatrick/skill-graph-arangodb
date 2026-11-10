"""SAFE BY DEFAULT: dry-run plan. Only --apply --acknowledge-new-database writes to ArangoDB.

Reads the immutable Skill Graph JSONL. Creates a NEW dedicated demo database,
imports 24 collections, and registers the named graph. Never touches other databases.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import sys
import urllib.parse
from arango_s23_common import ROOT, ArangoHTTP, ArangoError, release_counts

CURRENT_RELEASE='CURRENT_RELEASE.json'
VERTICES=('careers','courses','providers','skill_groups','skills','users')
DOCUMENTS=('course_offers','course_prerequisite_evidence','course_url_access_observations','data_sources','learning_plans','skill_assessments')
EDGES={
  'completed':(['users'],['courses']),
  'course_entry_skill':(['courses'],['skills']),
  'esco_group_broader':(['skill_groups'],['skill_groups']),
  'esco_skill_broader':(['skills'],['skills']),
  'esco_skill_group':(['skills'],['skill_groups']),
  'esco_skill_knowledge':(['skills'],['skills']),
  'has_skill':(['users'],['skills']),
  'offered_by':(['courses'],['providers']),
  'prerequisite':(['courses'],['courses']),
  'requires_skill':(['careers'],['skills']),
  'targets_career':(['users'],['careers']),
  'teaches':(['courses'],['skills'])
}


def preflight():
    pointer=json.loads((ROOT/CURRENT_RELEASE).read_text(encoding='utf8'))
    manifest_bytes=(ROOT/pointer['manifest_file']).read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest()==pointer['manifest_sha256'],'Current manifest pointer mismatch'
    m=json.loads(manifest_bytes)
    assert m['version']==pointer['version'] and m['sprint']==pointer['sprint'],'Version pointer mismatch'
    files=sorted((ROOT/'release').rglob('*.jsonl'))
    assert len(files)==24
    vertex_ids=set();counts={}
    by_name={p.stem:p for p in files}
    for p in files:
        rel=p.relative_to(ROOT).as_posix()
        data=p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==m['release_sha256'][rel],f'Corrupt: {rel}'
        records=[json.loads(line) for line in data.splitlines() if line]
        assert len({row['_key'] for row in records})==len(records)
        counts[p.stem]=len(records)
        if p.stem in VERTICES:vertex_ids.update(f'{p.stem}/{r["_key"]}' for r in records)
    for collection in EDGES:
        with by_name[collection].open(encoding='utf8') as stream:
            for line in stream:
                if not line.strip():continue
                row=json.loads(line)
                assert row['_from'] in vertex_ids and row['_to'] in vertex_ids, f'Invalid edge in {collection}'
                assert row['_from'].split('/')[0] in EDGES[collection][0] and row['_to'].split('/')[0] in EDGES[collection][1], f'Wrong graph endpoints {collection}'
    assert set(counts)==set(VERTICES)|set(EDGES)|set(DOCUMENTS)
    assert sum(counts.values())==m['records'] and sum(counts.values())==pointer['records']
    return m,counts,by_name


def main(argv=None):
    ap=argparse.ArgumentParser(description='Plan or create a NEW ArangoDB demo database; no writes unless explicitly opted in.')
    ap.add_argument('--apply',action='store_true',help='CREATE a new database and import records; never overwrite existing database.')
    ap.add_argument('--acknowledge-new-database',action='store_true',help='Second confirmation required with --apply.')
    ap.add_argument('--host',default='http://127.0.0.1:8529')
    ap.add_argument('--username',default='root')
    ap.add_argument('--database',default='skill_graph_sprint92_demo')
    args=ap.parse_args(argv)
    if not args.database.replace('_','').isalnum() or args.database.startswith('_'):
        ap.error('--database may contain letters, digits, and internal underscores only')
    m,counts,paths=preflight()
    print(f'OFFLINE PREFLIGHT PASS — 24 JSONL / {sum(counts.values()):,} records / SHA-256 verified / release {m["version"]}')
    print(json.dumps({'mode':'new-database import' if args.apply else 'dry_run_no_network','database':args.database,'graph':'skill_graph','collections':counts,'records':sum(counts.values())},ensure_ascii=False,indent=2))
    if not args.apply:
        print('DRY RUN ONLY: no network request, no ArangoDB writes. Add --apply --acknowledge-new-database to import.');return 0
    if not args.acknowledge_new_database:
        ap.error('To write, pass BOTH --apply and --acknowledge-new-database. New database only.')
    client=ArangoHTTP(args.host,args.username)
    try:
        known=client.request('GET','/_db/_system/_api/database').get('result',[])
        if args.database in known:
            raise ArangoError(f'REFUSED: database {args.database!r} already exists; no updates/deletion/overwrite. Choose a fresh name.')
        client.request('POST','/_db/_system/_api/database',{'name':args.database})
        print('NEW DATABASE CREATED:',args.database)
        # Import vertices first so all referenced vertices exist before edge import.
        doc_names=[name for name in counts if name not in VERTICES and name not in EDGES]
        ordering=list(VERTICES)+doc_names+list(EDGES)
        for name in ordering:
            typ=3 if name in EDGES else 2
            client.request('POST',client.dbpath(args.database,'/_api/collection'),{'name':name,'type':typ})
            if counts[name]:
                query=urllib.parse.urlencode({'collection':name,'type':'documents','complete':'true','onDuplicate':'error'})
                result=client.request('POST',client.dbpath(args.database,'/_api/import?'+query),paths[name].read_bytes(),content_type='text/plain; charset=utf-8')
                if result.get('errors',0)>0 or result.get('created')!=counts[name]:
                    raise ArangoError(f'Failed import count for {name}: {result}')
            print('IMPORTED',name,counts[name])
        definitions=[{'collection':name,'from':endpoints[0],'to':endpoints[1]} for name,endpoints in EDGES.items()]
        client.request('POST',client.dbpath(args.database,'/_api/gharial'),{'name':'skill_graph','edgeDefinitions':definitions,'orphanCollections':[]})
        print('REGISTERED named graph: skill_graph')
        total=sum(client.aql(args.database,f'FOR d IN {name} COLLECT WITH COUNT INTO n RETURN n')[0] for name in counts)
        if total != sum(counts.values()):raise ArangoError(f'Post-import COUNT mismatch: {total}')
        print(f'LIVE IMPORT OK: {total} records, 24 collections. Next: python tools\\verify_arangodb.py --database {args.database}')
        return 0
    except (ArangoError,ValueError) as e:
        print('IMPORT FAILED:',e,file=sys.stderr)
        print('A new partially populated demo database MAY exist. Script never auto-deletes it; inspect manually before retrying with a different database name.',file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())
