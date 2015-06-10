
# bsc - basespace command-line utility

bsc provides a command line interface to common requests
on the Illumina's BaseSpace cloud API.

## Installing

1. Install the [python sdk](http://github.com/basespace/basespace-python-sdk).
2. Fill in your credentials on the ~/.basespacepy.cfg file (more details on the link above).

## Usage

The script can be used by itself as a command line program, (try --help)
 or as a module, check out the as_module_example.py file.

## Common Patterns

### list all projects
```
$ ./bsc.py -a list_projects
proj_name                                                proj_id 
NextSeq 500: TruSeq PCR Free WGS_RTA2.1.3.0 (NA12878)    8705697 
NextSeq 500 v2: Nextera Rapid Capture Exome (CEPH Trio)  19559545
```

### list samples of a project
```
$ ./bsc.py -a list_samples -p 19559545
experiment_name      sample_name   sample_id
NextSeq 500 v2: NRC  NA12878_Rep1  21472706 
NextSeq 500 v2: NRC  NA12892_Rep1  21472707 
NextSeq 500 v2: NRC  NA12891_Rep1  21472708
```

### list files of a sample
```
$ ./bsc.py -a list_samplefiles -s 21472706 -l all
file_size  file_path                             file_id   
672601396  NA12878-Rep1_S1_L001_R1_001.fastq.gz  1411485021
687038064  NA12878-Rep1_S1_L001_R2_001.fastq.gz  1411485022
674214209  NA12878-Rep1_S1_L002_R1_001.fastq.gz  1411485023
686805446  NA12878-Rep1_S1_L002_R2_001.fastq.gz  1411485024
661133853  NA12878-Rep1_S1_L003_R1_001.fastq.gz  1411485025
672065598  NA12878-Rep1_S1_L003_R2_001.fastq.gz  1411485026
686304285  NA12878-Rep1_S1_L004_R1_001.fastq.gz  1411485027
697163335  NA12878-Rep1_S1_L004_R2_001.fastq.gz  1411485028
```

