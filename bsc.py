#!/usr/bin/python2
import json
import sys
import inspect
import datetime
from optparse import OptionParser, OptionGroup
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI
from BaseSpacePy.model.QueryParameters import QueryParameters as qp

progname = 'bsc'
version = 'version 2015.04.13'
help_text = '''{0} - basespace command-line utility. {1}

      Usage: {0} [options] -a <action>
  Actions:
    list_projects        - list all projects
    list_samples         - list all samples in a project
    list_samplefiles     - list all files for a sample
    list_runs            - list all runs
    list_runfiles        - list all files for a run
    list_runsamples      - list all samples for a run
    download_file        - download a file
  Options:
    -a,--action <action> - The action to be executed.
    -l,--limit     <int> - limit the lists results, default 10
    -n,--no-download     - Dont actually download anything
    -o,--out-dir   <dir> - Output dir for downloaded files, default cwd
    -d,--dir-struct      - Preserve original directory struct
    -j,--json            - Print listings as json
    -t,--table           - Print listings as table (tab separated)
    -s,--sample-id  <id> - Sample id
    -p,--project-id <id> - Project id
    -r,--run-id     <id> - Run id
    -f,--file-id    <id> - File id
'''.format(progname, version)

def json_handler(obj):
	if hasattr(obj, 'isoformat'):
		return obj.isoformat()
	else:
		json.JSONEncoder().default(obj)

def as_json(h):
	print(json.dumps(h, sort_keys=True,indent=2, separators=(',', ': '), default=json_handler))

def as_table(h):
	if h == None or len(h) == 0: return

	keys = h[0].keys()
	print("\t".join(keys))

	for r in h:
		print("\t".join(map(lambda k:str(r[k]), keys)))

def as_pretty(h):
	if h == None or len(h) == 0: return

	keys = h[0].keys()
	max_size = {}
	for i in keys:
		max_size[i] = len(i)
		for r in h:
			max_size[i] = max(max_size[i], len(str(r[i])))
	
	a = []
	for k in keys:
		f = "%-"+str(max_size[k])+"s"
		a.append(f % k)
	print("  ".join(a))
	
	for r in h:
		a = []
		for k in keys:
			f = "%-"+str(max_size[k])+"s"
			a.append(f % r[k])
		print("  ".join(a))

# api limits the number of items to 1000 per call
# so we need to do multiple requests to get everything, if necessary
def _bulk_request(api_func, id_param, query_limit):
	offset = 0
	api_batch_limit = 1000
	batch_num = api_batch_limit
	got_all = False
	if query_limit == 'all':
		will_get_all = True
	else:
		will_get_all = False
		query_limit = int(query_limit)
		if query_limit < api_batch_limit:
			batch_num = query_limit
	
	while got_all == False:
		if id_param == None:
			result = api_func(queryPars=qp({'Offset': offset, 'Limit': batch_num}))
		else:
			result = api_func(id_param, queryPars=qp({'Offset': offset, 'Limit': batch_num}))
		for r in result:
			yield r
			offset += 1
			if offset >= query_limit:
				got_all = True
				break

		if query_limit != 'all' and offset >= query_limit:
			got_all = True
		elif len(result) < batch_num:
			got_all = True

# error out if the required id is not defined
def require_id(xid, args):
	names = {
		'run_id': "Run id", "sample_id": "Sample id",
		'proj_id': "Project id", "file_id": "File id"
	}
	if xid not in args or args[xid] == None:
		sys.stderr.write("%s: %s: %s argument is required.\n" % (progname,inspect.currentframe().f_back.f_code.co_name, names[xid]))
		sys.exit(1)

def list_runsamples(args):
	require_id("run_id", args)

	a = []
	samples = _bulk_request(args['api'].getRunSamplesById, args['run_id'], args['query_limit'])
	for s in samples:
		a.append({'sample_id': s.Id, 'sample_name': s.Name})
	return a

def list_runfiles(args):
	require_id("run_id", args)

	a = []
	files = _bulk_request(args['api'].getRunFilesById, args['run_id'], args['query_limit'])
	for f in files:
		a.append({'file_id': f.Id, 'file_path': f.Path, 'file_size': f.Size})
	return a

def list_samples(args):
	require_id("proj_id", args)

	a = []
	samples = _bulk_request(args['api'].getSamplesByProject, args['proj_id'], args['query_limit'])
	for s in samples:
		if hasattr(s, "ExperimentName"):
			a.append({'sample_id': s.Id, 'sample_name': s.Name, 'experiment_name': s.ExperimentName})
		else:
			a.append({'sample_id': s.Id, 'sample_name': s.Name, 'experiment_name': None})
	return a

def list_samplefiles(args):
	require_id("sample_id", args)

	a = []
	files = _bulk_request(args['api'].getSampleFilesById, args['sample_id'], args['query_limit'])
	for f in files:
		a.append({'file_path': f.Path, 'file_id': f.Id, 'file_size': f.Size})
	return a

def list_projects(args):
	a = []
	projs = _bulk_request(args['api'].getProjectByUser, None, args['query_limit'])
	for p in projs:
		a.append({'proj_id': p.Id, 'proj_name': p.Name})
	return a

def list_runs(args):
	a = []
	runs = _bulk_request(args['api'].getAccessibleRunsByUser, None, args['query_limit'])
	for r in runs:
		a.append({'run_id': r.Id, 'run_name': r.ExperimentName, 'run_date': r.DateCreated})
	return a

def download_file(args):
	require_id("file_id", args)

	if 'no_download' in args and args['no_download']:
		print("pretending to download file_id: "+args['file_id'])
	else:
		args['api'].fileDownload(args['file_id'], args['out_dir'], createBsDir=args['dir_struct'])

def MAIN():
	actions = {
		'list_samples': list_samples,
		'list_projects': list_projects,
		'list_samplefiles': list_samplefiles,
		'list_runfiles': list_runfiles,
		'list_runs': list_runs,
		'list_runsamples': list_runsamples,
		'download_file': download_file,
	}

	parser = OptionParser(usage="%prog [options] -a <action>", add_help_option=False)
	parser.add_option('-v', '--version', dest='get_version', default=False, action="store_true")
	parser.add_option('-h', '--help', dest='get_help', default=False, action="store_true")
	parser.add_option('-l', '--limit', dest='query_limit', default='10')
	parser.add_option('-s', '--sample-id', dest='sample_id')
	parser.add_option('-p', '--project-id', dest='project_id')
	parser.add_option('-r', '--run-id', dest='run_id')
	parser.add_option('-f', '--file-id', dest='file_id')
	parser.add_option('-n', '--no-download', action="store_true", dest='no_download', default=False)
	parser.add_option('-o', '--out-dir', dest='out_dir', default='.')
	parser.add_option('-d', '--dir-struct', action="store_true", dest='dir_struct', default=False)
	parser.add_option('-j', '--json', action="store_true", dest='as_json', default=False)
	parser.add_option('-t', '--table', action="store_true", dest='as_table', default=False)
	parser.add_option('-a', '--action', type="choice", dest='action', choices=actions.keys(), default=None)
	options, args = parser.parse_args()

	if(options.get_help):
		print(help_text)
		sys.exit(0)

	if(options.get_version):
		print(progname+" "+version)
		sys.exit(0)

	if(options.action == None):
		sys.stderr.write("Error: Action argument is required.\n\n")
		sys.stderr.write(help_text)
		sys.exit(1)
	else:
		bs_api = BaseSpaceAPI(profile='DEFAULT')
		call_args = {
			'query_limit': options.query_limit,
			'api': bs_api,
			'proj_id': options.project_id,
			'sample_id': options.sample_id,
			'run_id': options.run_id,
			'file_id': options.file_id,
			'out_dir': options.out_dir,
			'dir_struct': options.dir_struct,
			'no_download': options.no_download
		}
		r = actions[options.action](call_args)
		if options.as_json:
			as_json(r)
		elif options.as_table:
			as_table(r)
		else:
			as_pretty(r)

if __name__ == '__main__':
	MAIN()

