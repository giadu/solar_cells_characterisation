1. put script on the same directory as the csv files you want to use for characterisation
2. make sure to remove any other csv files, including those create by the script if you wish to run it one more time
3. run as follows:
mac: python3 iv_characterisation.py *.csv
windows: python iv_characterisation.py (Get-ChildItem *.csv).Name
