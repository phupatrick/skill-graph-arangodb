"""Sprint92 offline audit; verify parent bytes, SHA, references, topic counts. No network."""
import json,hashlib,pathlib
from prepare_arangodb import preflight
ROOT=pathlib.Path(__file__).resolve().parents[1]
def rows(c,k): return [json.loads(z) for z in (ROOT/'release'/k/(c+'.jsonl')).read_text(encoding='utf8').splitlines() if z.strip()]
def check():
 mf,counts,_=preflight(); assert (mf['version'],mf['sprint'])==('v3.55',92)
 pb=(ROOT/mf['parent_manifest_file']).read_bytes();assert hashlib.sha256(pb).hexdigest()==mf['parent_manifest_sha256']
 pm=json.loads(pb)
 for rel,size in mf['parent_release_sizes'].items():
  raw=(ROOT/rel).read_bytes();assert hashlib.sha256(raw[:size]).hexdigest()==mf['parent_release_sha256'][rel]
  assert mf['parent_release_sha256'][rel]==pm['release_sha256'][rel]
 req=[r for r in rows('requires_skill','edges') if str(r.get('requirement_type','')).lower()=='essential']
 teach=rows('teaches','edges');cov={x['_to'] for x in teach if x.get('evidence_scope')=='direct_topic'}
 covered=sum(r['_to'] in cov for r in req)
 assert (len(req),covered,len(req)-covered)==(343,323,20)
 new=[r for r in teach if r['_key'].startswith('s92_teach_')];assert len(new)==7
 assert all(r['recommendation_role']=='topic_candidate_only' and r['v3_12_auto_recommendation_allowed'] is False and r['target_level'] is None and r['proficiency_gain_unverified'] is True for r in new)
 courses=rows('courses','vertices');assert len({r['canonical_url'] for r in courses})==len(courses)
 ids={'careers':{x['_key'] for x in rows('careers','vertices')},'courses':{x['_key'] for x in courses},'providers':{x['_key'] for x in rows('providers','vertices')},'skills':{x['_key'] for x in rows('skills','vertices')},'users':{x['_key'] for x in rows('users','vertices')},'skill_groups':{x['_key'] for x in rows('skill_groups','vertices')}}
 for p in (ROOT/'release'/'edges').glob('*.jsonl'):
  for l in p.read_text('utf8').splitlines():
   if not l.strip():continue
   e=json.loads(l)
   for side in ('_from','_to'):
    col,key=e[side].split('/',1);assert col in ids and key in ids[col],(p.name,e['_key'],side)
 assert counts['prerequisite']==0 and sum(counts.values())==mf['records']
 return {'result':'PASS','version':mf['version'],'collections':len(counts),'records':mf['records'],'parent_exact_byte_prefix':True,'edge_integrity':'PASS','essential_total':343,'essential_direct':covered,'essential_missing':20,'topic_coverage_pct':round(covered/343*100,2),'new_courses':7,'new_teaches':7,'auto_approved_new':0,'prerequisite_edges':0,'no_network_or_writes':True}
