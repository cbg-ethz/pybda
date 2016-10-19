This parser reads all the aggregate files in:
```
/Users/simondi/PHD/data/data/target_infect_x/aggregates
```
and convertes them into a REASONABLE usable format and beautifies them.

Call the ``sh`` to automatically parse all the files. Then call the beautifier using:

```sh
python tix_beautify_columns.py -f INPUT_AGGREGATE
```

