
# downloads all run files of the run with the id <run_id>
# into the outdir/ directory, with the original dir structure

import bsc
from BaseSpacePy.api.BaseSpaceAPI import BaseSpaceAPI

api = BaseSpaceAPI(profile='DEFAULT')
run_files = bsc.list_runfiles({'api': api, 'run_id': '<run_id>', 'query_limit': 'all'})
for r in run_files:
	print("downloading file "+r['file_id']+" "+r['file_path'])
	bsc.download_file({'api': api, 'file_id': r['file_id'], 'out_dir': 'outdir', 'dir_struct': True, 'no_download': True})

