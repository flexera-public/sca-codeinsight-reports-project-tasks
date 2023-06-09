'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Sep 22 2021
File : report_artifacts.py
'''

import logging
import os
from datetime import datetime
import base64
import re
#import xlsxwriter


logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------------#
def create_report_artifacts(reportData):
    logger.info("Entering create_report_artifacts")

    # Dict to hold the complete list of reports
    reports = {}

    htmlFile = generate_html_report(reportData)
    #xlsxFile = generate_xlsx_report(reportData)

    reports["viewable"] = htmlFile
    reports["allFormats"] = [htmlFile]

    logger.info("Exiting create_report_artifacts")
    
    return reports 



#------------------------------------------------------------------#
def generate_html_report(reportData):
    logger.info("    Entering generate_html_report")

    reportName = reportData["reportName"]
    projectName = reportData["projectName"] 
    projectID = reportData["projectID"] 
    fileNameTimeStamp = reportData["fileNameTimeStamp"] 
    projectList = reportData["projectList"]
    projectData = reportData["projectData"]

    scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    cssFile =  os.path.join(scriptDirectory, "html-assets/css/revenera_common.css")
    logoImageFile =  os.path.join(scriptDirectory, "html-assets/images/logo_reversed.svg")
    iconFile =  os.path.join(scriptDirectory, "html-assets/images/favicon-revenera.ico")

    logger.debug("cssFile: %s" %cssFile)

    # Grab the current date/time for report date stamp
    now = datetime.now().strftime("%B %d, %Y at %H:%M:%S")


    #########################################################
    #  Encode the image files
    encodedLogoImage = encodeImage(logoImageFile)
    encodedfaviconImage = encodeImage(iconFile)

    projectNameForFile = re.sub(r"[^a-zA-Z0-9]+", '-', projectName )

    if len(projectList)==1:
        htmlFile = projectNameForFile + "-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".html"
    else:
        htmlFile = projectNameForFile + "-with-children-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".html" 

    logger.debug("htmlFile: %s" %htmlFile)

    #---------------------------------------------------------------------------------------------------
    # Create a simple HTML file to display
    #---------------------------------------------------------------------------------------------------
    try:
        html_ptr = open(htmlFile,"w")
    except:
        logger.error("Failed to open htmlfile %s:" %htmlFile)
        raise

    html_ptr.write("<html>\n") 
    html_ptr.write("    <head>\n")

    html_ptr.write("        <!-- Required meta tags --> \n")
    html_ptr.write("        <meta charset='utf-8'>  \n")
    html_ptr.write("        <meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'> \n")

    html_ptr.write(''' 
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.1/css/bootstrap.min.css" integrity="sha384-VCmXjywReHh4PwowAiWNagnWcLhlEJLA5buUprzK8rxFgeH0kww/aWY76TfkUoSX" crossorigin="anonymous">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/themes/default/style.min.css">
    ''')


    html_ptr.write("        <style>\n")

    # Add the contents of the css file to the head block
    try:
        f_ptr = open(cssFile)
        logger.debug("Adding css file details")
        for line in f_ptr:
            html_ptr.write("            %s" %line)
        f_ptr.close()
    except:
        logger.error("Unable to open %s" %cssFile)
        print("Unable to open %s" %cssFile)


    html_ptr.write("        </style>\n")  

    html_ptr.write("    	<link rel='icon' type='image/png' href='data:image/png;base64, {}'>\n".format(encodedfaviconImage.decode('utf-8')))
    html_ptr.write("        <title>%s</title>\n" %(reportName.upper()))
    html_ptr.write("    </head>\n") 

    html_ptr.write("<body>\n")
    html_ptr.write("<div class=\"container-fluid\">\n")

    #---------------------------------------------------------------------------------------------------
    # Report Header
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN HEADER -->\n")
    html_ptr.write("<div class='header'>\n")
    html_ptr.write("  <div class='logo'>\n")
    html_ptr.write("    <img src='data:image/svg+xml;base64,{}' style='width: 400px;'>\n".format(encodedLogoImage.decode('utf-8')))
    html_ptr.write("  </div>\n")
    html_ptr.write("<div class='report-title'>%s</div>\n" %reportName)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END HEADER -->\n")

    #---------------------------------------------------------------------------------------------------
    # Body of Report
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN BODY -->\n")  


    html_ptr.write("<table id='taskData' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='9' class='text-center'><h4>Tasks</h4></th>\n") 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n")
    if len(projectList) > 1: 
        html_ptr.write("            <th style='width: 15%' class='text-center'>PROJECT</th>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center text-nowrap'>TASK SUMMARY</th>\n")
    html_ptr.write("            <th style='width: 10%' class='text-center'>TASK OWNER</th>\n") 
    html_ptr.write("            <th style='width: 10%' class='text-center'>TASK CREATOR</th>\n") 
    html_ptr.write("            <th style='width: 10%' class='text-center'>TASK TYPE</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>TASK PRIORITY</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>TASK STATUS</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>CREATED DATE</th>\n")
    html_ptr.write("            <th style='width: 15%' class='text-center'>EXTERNAL ISSUES</th>\n")


    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")  



    for project in projectList:

        projectName = project["projectName"]
        projectLink = project["projectLink"]
        inventoryLinkBase = project["inventoryLinkBase"]

        taskData = projectData[projectName]["projectTaskData"]

        for task in taskData:

            inventoryItemId = task["inventoryId"]
            inventoryItemLink = inventoryLinkBase + str(inventoryItemId)
            taskType = task["taskType"]
            priority = task["priority"]
            createdDate = task["createdDate"]
            summary = task["summary"]
            taskStatus = task["taskStatus"]
            almIssues = task["almIssues"]


            html_ptr.write("        <tr> \n")
            if len(projectList) > 1:
                html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(projectLink, projectName))
            html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(inventoryItemLink, summary))
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(task["taskOwner"]))
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(task["taskCreator"]))
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(taskType))
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(priority))
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(taskStatus))
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(createdDate))

            html_ptr.write("            <td class='text-left'>")
            
            for issue in almIssues:
                 html_ptr.write(" <a href='%s' target='_blank'>%s</a><br>\n" %(issue["externalUrl"], issue["externalKey"])  )

            html_ptr.write(" </td\n>")




        html_ptr.write("        </tr>\n") 
    html_ptr.write("    </tbody>\n")


    html_ptr.write("</table>\n") 




    html_ptr.write("<!-- END BODY -->\n")  

    #---------------------------------------------------------------------------------------------------
    # Report Footer
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN FOOTER -->\n")
    html_ptr.write("<div class='report-footer'>\n")
    html_ptr.write("  <div style='float:left'>&copy; %s Flexera</div>\n" %fileNameTimeStamp[0:4])
    html_ptr.write("  <div style='float:right'>Generated on %s</div>\n" %now)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END FOOTER -->\n")   

    html_ptr.write("</div>\n")

    #---------------------------------------------------------------------------------------------------
    # Add javascript 
    #---------------------------------------------------------------------------------------------------

    html_ptr.write('''

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>  
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>

 
    ''')

    html_ptr.write("<script>\n")
    html_ptr.write('''

            $(document).ready(function (){
                var table = $('#taskData').DataTable({
                    "order": [[ 2, "desc" ]],
                    "lengthMenu": [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
                });
            });
        ''')    

    html_ptr.write("</script>\n")

    html_ptr.write("</body>\n") 
    html_ptr.write("</html>\n") 
    html_ptr.close() 

    logger.info("    Exiting generate_html_report")
    return htmlFile


####################################################################
def encodeImage(imageFile):

    #############################################
    # Create base64 variable for branding image
    try:
        with open(imageFile,"rb") as image:
            logger.debug("Encoding image: %s" %imageFile)
            encodedImage = base64.b64encode(image.read())
            return encodedImage
    except:
        logger.error("Unable to open %s" %imageFile)
        raise