# Documentation of the Investegate crawler
*Written and tested with Python 3.4 under OS X El Capitan.*

### Invocation
i.e. `python3 investegate.py -q "Goldman+Sachs+(EPT)" -d "N"`

The parameter -q or --query specifies the company name that will be searched for.<br>
Investegate does not use equals search but LIKE search, so -q "Apple" will yield results for Apple Inc., 	Red Apple Investmnts and Apple Oil & Gas Ltd.<br>
If the search String contains whitespaces (" "), you will have to replace them with a dividing plus "+".

The parameter -d or --download specifies weither the script should download all filings.<br>
Downloaded filings appear in ./investegate/company/filingId.html.

### Logic
1. Query
2. Loop Pages
3. Loop Rows
4. Append to CSV
5. Download (optional)

### Legal Notice
Do not use this script to download the entirety of Investegate, as this might break their ToS and/or violate local cybercrime policies.
