# Copyright 2016 Daniel Pesch
# No License - any unauthorized use is a copyright violation.

import os.path
import sys, getopt
import socket
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

def downloadfile( sourceurl, targetfname ):
    mem_file = ""
    good_read = False
    xbrlfile = None
    if os.path.isfile( targetfname ):
        print( "Local copy already exists" )
        return True
    else:
        print( "Downloading:", sourceurl )
        try:
            xbrlfile = urlopen( sourceurl )
            try:
                mem_file = xbrlfile.read()
                good_read = True
            finally:
                xbrlfile.close()
        except HTTPError as e:
            print( "HTTP Error:", e.code )
        except URLError as e:
            print( "URL Error:", e.reason )
        except TimeoutError as e:
            print( "Timeout Error:", e.reason )
        except socket.timeout:
            print( "Socket Timeout Error" )
        if good_read:
            output = open( targetfname, 'wb' )
            output.write( mem_file )
            output.close()
        return good_read

def downloadAllFilingsForCompany( query, download ):
    edgarRootURLResult = None
    edgarRootURLData = None
    start = 0
    end = 0
    pageNumber = 1
    limitNotReached = True
    skippedC = 0
    filingId = ""

    while limitNotReached:
        try:
            investegatePage = 'http://www.investegate.co.uk/Index.aspx?searchtype=2&words='+query+'&pno='+str(pageNumber)
            investegatePageResult = urlopen( investegatePage )
            try:
                investegatePageData = str(investegatePageResult.read())
                investegatePageData = investegatePageData[investegatePageData.index('<table id="announcementList'):investegatePageData.index('id="bottomNavList"')]
                while limitNotReached:
                    try:
                        if investegatePageData.index('tr') > 0:
                            start = int(investegatePageData.index('<tr>')) + len('<tr>')
                            end = int(investegatePageData.index('</tr>', start))
                            filingRow = investegatePageData[start:end]
                            # Feature Calculations
                            try:
                                # Date
                                dateStart = int(filingRow.index('<td class="noBreak">')) + len('<td class="noBreak">')
                                dateEnd = int(filingRow.index('</td>', dateStart))
                                dateEntry = filingRow[dateStart:dateEnd]
                                if dateEntry == "&nbsp;":
                                    dateEntry = '""'

                                # Time
                                timeStart = int(filingRow.index('<td class="time">')) + len('<td class="time">')
                                timeEnd = int(filingRow.index('</td>', timeStart))
                                timeEntry = filingRow[timeStart:timeEnd]

                                # Source
                                sourceStart = int(filingRow.index('title="supplier: ')) + len('title="supplier: ')
                                sourceEnd = int(filingRow.index('">', sourceStart))
                                sourceEntry = filingRow[sourceStart:sourceEnd]

                                # Company
                                companyStart = int(filingRow.index('<strong>')) + len('<strong>')
                                companyEnd = int(filingRow.index('</strong>', companyStart))
                                companyEntry = filingRow[companyStart:companyEnd]

                                # Link
                                linkStart = int(filingRow.index('<a class="annmt" href="')) + len('<a class="annmt" href="')
                                linkEnd = int(filingRow.index('">', linkStart))
                                linkEntry = 'http://www.investegate.co.uk' + filingRow[linkStart:linkEnd]

                                filingRow = filingRow[linkEnd:len(filingRow)]

                                # Type
                                typeStart = 2
                                typeEnd = int(filingRow.index('</a>', typeStart))
                                typeEntry = filingRow[typeStart:typeEnd]

                                # print ("Date: "+ dateEntry )
                                # print ("Time: "+ timeEntry )
                                # print ("Source: "+ sourceEntry )
                                # print ("Company: "+ companyEntry )
                                # print ("Link: "+ linkEntry )
                                # print ("Type: "+ typeEntry )

                                # Append ratios to a CSV file for further analysis
                                with open("investegate.csv", "a") as ratiofile:
                                    ratiofile.write( dateEntry + ',"' + timeEntry + '",' + sourceEntry + "," + companyEntry + "," + linkEntry + "," + typeEntry + "\n" )
                                    ratiofile.close()

                                if download == "Y":
                                    # Attempt a download of the filing
                                    filingId = linkEntry.split("/")[-2]
                                    if not os.path.exists( "./investegate/"+companyEntry):
                                        os.makedirs( "./investegate/"+companyEntry )
                                    downloadfile("http://www.investegate.co.uk/ArticlePrint.aspx?id="+filingId+".html", "./investegate/"+companyEntry+"/"+filingId+".html")

                                skippedC = 0
                            except Exception as e:
                                if skippedC > 2:
                                    limitNotReached = False
                                else:
                                    skippedC = skippedC + 1
                            investegatePageData = investegatePageData[end:len(investegatePageData)]
                    except ValueError:
                        pageNumber = pageNumber + 1
                        break
            finally:
                investegatePageResult.close()
        except HTTPError as e:
            print( "HTTP Error:", e.code )
        except URLError as e:
            print( "URL Error:", e.reason )
        except TimeoutError as e:
            print( "Timeout Error:", e.reason )
        except socket.timeout:
            print( "Socket Timeout Error" )

def main(argv):
    if not os.path.exists( "sec" ):
        os.makedirs( "sec" )
    socket.setdefaulttimeout(100)
    query = ""
    download = "Y"
    try:
        opts, args = getopt.getopt(argv,"q:d:",["query=", "download="])
    except getopt.GetoptError:
        print( 'investegate -q <query> -d <download> | -h <help>' )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print( 'investegate -q <query> -d <download> | -h <help>' )
            sys.exit()
        elif opt in ("-q", "--query"):
            query = arg
        elif opt in ("-d", "--download"):
            download = arg
    if query != "":
        # Create output CSV file if it doesn't exist yet
        if not os.path.isfile( "investegate.csv" ):
            with open("investegate.csv", "a") as ratiofile:
                ratiofile.write( "Date,Time,Source,Company,Link,Type\n" )
                ratiofile.close()
        downloadAllFilingsForCompany ( query, download )

if __name__ == "__main__":
    main(sys.argv[1:])
