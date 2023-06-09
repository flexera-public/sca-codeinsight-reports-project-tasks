'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Sep 22 2021
File : create_report.py
'''
import sys
import logging
import argparse
import zipfile
import os
import json
from datetime import datetime
import re

import _version
import report_data
import report_artifacts
import report_errors

import CodeInsight_RESTAPIs.project.upload_reports

###################################################################################
# Test the version of python to make sure it's at least the version the script
# was tested on, otherwise there could be unexpected results
if sys.version_info <= (3, 5):
    raise Exception("The current version of Python is less than 3.5 which is unsupported.\n Script created/tested against python version 3.8.1. ")
else:
    pass

logfileName = os.path.dirname(os.path.realpath(__file__)) + "/_project_task_report.log"

###################################################################################
#  Set up logging handler to allow for different levels of logging to be capture
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S', filename=logfileName, filemode='w',level=logging.DEBUG)
logger = logging.getLogger(__name__)


####################################################################################
# Create command line argument options
parser = argparse.ArgumentParser()
parser.add_argument('-pid', "--projectID", help="Project ID")
parser.add_argument("-rid", "--reportID", help="Report ID")
parser.add_argument("-authToken", "--authToken", help="Code Insight Authorization Token")
parser.add_argument("-baseURL", "--baseURL", help="Code Insight Core Server Protocol/Domain Name/Port.  i.e. http://localhost:8888 or https://sca.codeinsight.com:8443")
parser.add_argument("-reportOpts", "--reportOptions", help="Options for report content")

#----------------------------------------------------------------------#
def main():

	reportName = "Project Task Report"

	logger.info("Creating %s - %s" %(reportName, _version.__version__))
	print("Creating %s - %s" %(reportName, _version.__version__))

	# See what if any arguments were provided
	args = parser.parse_args()
	projectID = args.projectID
	reportID = args.reportID
	authToken = args.authToken
	baseURL = args.baseURL
	reportOptions = args.reportOptions

	# Based on how the shell pass the arguemnts clean up the options if on a linux system:w
	if sys.platform.startswith('linux'):
		reportOptions = reportOptions.replace('""', '"')[1:-1]

	reportOptions = json.loads(reportOptions)
	reportOptions = verifyOptions(reportOptions) 

	logger.debug("Custom Report Provided Arguments:")	
	logger.debug("    projectID:  %s" %projectID)	
	logger.debug("    reportID:   %s" %reportID)	
	logger.debug("    baseURL:  %s" %baseURL)	
	logger.debug("    reportOptions:  %s" %reportOptions)	

	fileNameTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")

	# Did we fail the options validation?
	if "errorMsg" in reportOptions.keys():
		reportOptions["reportName"] = reportName
		reportOptions["fileNameTimeStamp"] = fileNameTimeStamp
		reportOptions["projectID"] = projectID
		projectName = "Report_Creation_Error"
		numProjects = 0  # No project information gathered
		reports = report_errors.create_error_report(reportOptions)
		print("    *** ERROR  ***  Error found validating report options")
	else:
		reportData = report_data.gather_data_for_report(baseURL, projectID, authToken, reportName, reportOptions)
		print("    Report data has been collected")
		reportData["fileNameTimeStamp"] = fileNameTimeStamp
		projectName = reportData["projectName"]
		numProjects = len(reportData["projectList"])

		if "errorMsg" in reportData.keys():
			reports = report_errors.create_error_report(reportData)
			print("    Error report artifacts have been created")
		else:
			reports = report_artifacts.create_report_artifacts(reportData)
			print("    Report artifacts have been created")

	print("    Create report archive for upload")
	uploadZipfile = create_report_zipfile(reports, reportName, projectName, projectID, numProjects, fileNameTimeStamp)
	print("    Upload zip file creation completed")
	CodeInsight_RESTAPIs.project.upload_reports.upload_project_report_data(baseURL, projectID, reportID, authToken, uploadZipfile)
	print("    Report uploaded to Code Insight")


	#########################################################
	# Remove the file since it has been uploaded to Code Insight
	try:
		os.remove(uploadZipfile)
	except OSError:
		logger.error("Error removing %s" %uploadZipfile)
		print("Error removing %s" %uploadZipfile)

	logger.info("Completed creating %s" %reportName)
	print("Completed creating %s" %reportName)





#----------------------------------------------------------------------# 
def verifyOptions(reportOptions):
	'''
	Expected Options for report:
		includeChildProjects - True/False
	'''
	reportOptions["errorMsg"] = []
	trueOptions = ["true", "t", "yes", "y"]
	falseOptions = ["false", "f", "no", "n"]

	includeChildProjects = reportOptions["includeChildProjects"]


	if includeChildProjects.lower() in trueOptions:
		reportOptions["includeChildProjects"] = "true"
	elif includeChildProjects.lower() in falseOptions:
		reportOptions["includeChildProjects"] = "false"
	else:
		reportOptions["errorMsg"].append("Invalid option for including child projects: <b>%s</b>.  Valid options are <b>True/False</b>" %includeChildProjects)
    

	if not reportOptions["errorMsg"]:
		reportOptions.pop('errorMsg', None)

	return reportOptions



#---------------------------------------------------------------------#
def create_report_zipfile(reportOutputs, reportName, projectName, projectID, numProjects, fileNameTimeStamp):
	logger.info("Entering create_report_zipfile")

	projectNameForFile = re.sub(r"[^a-zA-Z0-9]+", '-', projectName )

	# create a ZipFile object
	if numProjects <= 1 :
		allFormatZipFile = projectNameForFile + "-" + projectID + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".zip"
	else: 
		allFormatZipFile = projectNameForFile + "-with-children-"  + projectID + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".zip"

	# create a ZipFile object
	allFormatsZip = zipfile.ZipFile(allFormatZipFile, 'w', zipfile.ZIP_DEFLATED)


	logger.debug("    Create downloadable archive: %s" %allFormatZipFile)
	print("        Create downloadable archive: %s" %allFormatZipFile)
	for format in reportOutputs["allFormats"]:
		print("            Adding %s to zip" %format)
		logger.debug("    Adding %s to zip" %format)
		allFormatsZip.write(format)

	allFormatsZip.close()
	logger.debug(    "Downloadable archive created")
	print("        Downloadable archive created")

	# Now create a temp zipfile of the zipfile along with the viewable file itself
	uploadZipflle = allFormatZipFile.replace(".zip", "_upload.zip")
	print("        Create zip archive containing viewable and downloadable archive for upload: %s" %uploadZipflle)
	logger.debug("    Create zip archive containing viewable and downloadable archive for upload: %s" %uploadZipflle)
	zipToUpload = zipfile.ZipFile(uploadZipflle, 'w', zipfile.ZIP_DEFLATED)
	zipToUpload.write(reportOutputs["viewable"])
	zipToUpload.write(allFormatZipFile)
	zipToUpload.close()
	logger.debug("    Archive zip file for upload has been created")
	print("        Archive zip file for upload has been created")

	# Clean up the items that were added to the zipfile
	try:
		os.remove(allFormatZipFile)
	except OSError:
		logger.error("Error removing %s" %allFormatZipFile)
		print("Error removing %s" %allFormatZipFile)
		return -1

	for fileName in reportOutputs["allFormats"]:
		try:
			os.remove(fileName)
		except OSError:
			logger.error("Error removing %s" %fileName)
			print("Error removing %s" %fileName)
			return -1    

	logger.info("Exiting create_report_zipfile")
	return uploadZipflle



#----------------------------------------------------------------------#    
if __name__ == "__main__":
    main()  