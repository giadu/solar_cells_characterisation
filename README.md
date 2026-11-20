## instructions
1. put script on the same directory as the csv files you want to use for characterisation
2. make sure to remove any other csv files, including those create by the script if you wish to run it one more time

## output files
the script creates these files in the same directory:
- summary.csv: one row per measurement with Jsc, Voc, Fill Factor, Efficiency and Rs (fs and bs)
- jsc.csv, voc.csv, fill_factor.csv, efficiency.csv: one metric per file, one fs/bs pair per csv file
- iv_curves.csv: J1 (fs) and J2 (bs) of each measurement, one row per voltage point

## how to run
- mac: python3 iv_characterisation.py *.csv
- windows: python iv_characterisation.py (Get-ChildItem *.csv).Name
