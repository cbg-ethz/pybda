## Setup

Check out `pipeline.md`, too.

Initialize everything, setup the database and so on.

* `aggregate parser` is for handling aggregate files.

Install `rnaiutilities` first and download the files from the `openBIS` instance.
Create a `config.yml` like this:

```yaml
  layout_file: "/../data/tix/plate_layout_meta_files/target_infect_x_library_layouts_beautified.tsv"
  plate_folder: "/../data/tix/screening_data/"
  output_path: "/../data/tix/screening_data/"
  plate_id_file: "/../data/tix/experiment_meta_files/experiment_meta_file.tsv"
  multiprocessing: False
```

Then run in succession: 

```bash
  rnai-parse checkdownloads config.yml
  rnai-parse parse config.yml
  rnai-parse report config.yml
  rnai-parse featuresets config.yml
```

This does the following: 

* checks if everything all files are downloaded,
* parses the files, 
* creates a parsing report,
* creates overlapping featuresets

Then call:

```bash
  rnai-query insert --db /path/to/db PATH
```

where `PATH` is the path to the downloaded files (the folder, not the files).