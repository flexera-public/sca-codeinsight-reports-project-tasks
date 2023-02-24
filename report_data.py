'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Sep 22 2021
File : report_data.py.py
'''

import logging
import CodeInsight_RESTAPIs.project.get_child_projects
import CodeInsight_RESTAPIs.task.search_tasks
import CodeInsight_RESTAPIs.users.search_users



logger = logging.getLogger(__name__)

#-------------------------------------------------------------------#
def gather_data_for_report(baseURL, projectID, authToken, reportName, reportOptions):
    logger.info("Entering gather_data_for_report")

    # Parse report options
    includeChildProjects = reportOptions["includeChildProjects"]  # True/False


    projectList = [] # List to hold parent/child details for report
    projectData = {} # Create a dictionary containing the project level summary data using project names as keys
    userData = {} # Dict to map user ID to names
    projectTaskData = {}

    # Get the list of parent/child projects start at the base project
    projectHierarchy = CodeInsight_RESTAPIs.project.get_child_projects.get_child_projects_recursively(baseURL, projectID, authToken)

    # Create a list of project data sorted by the project name at each level for report display  
    # Add details for the parent node
    nodeDetails = {}
    nodeDetails["parent"] = "#"  # The root node
    nodeDetails["projectName"] = projectHierarchy["name"]
    nodeDetails["projectID"] = projectHierarchy["id"]
    nodeDetails["projectLink"] = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectHierarchy["id"]) + "&tab=projectInventory"
    nodeDetails["inventoryLinkBase"] = nodeDetails["projectLink"]  + "&pinv="

    projectList.append(nodeDetails)

    if includeChildProjects == "true":
        projectList = create_project_hierarchy(projectHierarchy, projectHierarchy["id"], projectList, baseURL)
    else:
        logger.debug("Child hierarchy disabled")


    for project in projectList:
        projectID = project["projectID"]
        projectName = project["projectName"]
        projectLink = project["projectLink"]

        # Create empty dictionary for project level data for this project
        projectData[projectName] = {}
        projectData[projectName]["projectID"] = projectID
        projectData[projectName]["projectLink"] = projectLink
        projectData[projectName]["projectTaskData"] = []

        # Get project task data
        try:
            taskDataResponse = CodeInsight_RESTAPIs.task.search_tasks.get_all_tasks_for_project(baseURL, authToken, projectID)
        except:
            logger.error("    No Task Information Returned!")
            print("No Task Information Returned.")
   

        for task in taskDataResponse:
            projectTaskData = {}
            print(task)
           
            taskOwner = task["ownerId"]
            taskCreator = task["createdById"]
            createdDate = task["createdDate"]
            taskClosed = task["closed"]
            taskType = task["taskName"].split(" ")[0]

            createdDate, createdTime = createdDate.split(" ")
 
            if taskOwner not in userData:      
                userDetails = CodeInsight_RESTAPIs.users.search_users.get_user_details_by_id(baseURL, authToken, taskOwner)
                userFullName = userDetails[0]["firstName"] + " " + userDetails[0]["lastName"]
                userData[taskOwner] = userFullName

            if taskCreator not in userData:
                userDetails = CodeInsight_RESTAPIs.users.search_users.get_user_details_by_id(baseURL, authToken, taskCreator) 
                userFullName = userDetails[0]["firstName"] + " " + userDetails[0]["lastName"]
                userData[taskCreator] = userFullName

            if taskClosed:
                taskStatus = "Closed"
            else:
                taskStatus = "Open"

            projectTaskData["inventoryId"] = task["inventoryId"]
            projectTaskData["summary"] = task["summary"]
            projectTaskData["priority"] = task["priority"]
            projectTaskData["almIssues"] = []

            projectTaskData["taskCreator"] = userData[taskCreator]
            projectTaskData["taskOwner"] = userData[taskOwner]
            projectTaskData["createdDate"] = createdDate
            projectTaskData["createdTime"] = createdTime
            projectTaskData["taskStatus"] = taskStatus
            projectTaskData["taskType"] = taskType

    

            projectData[projectName]["projectTaskData"].append(projectTaskData)
            
        print(projectData[projectName]["projectTaskData"])

        

    # for project in projectData:
    #     print(projectData[project])


    # Build up the data to return for the
    reportData = {}
    reportData["reportName"] = reportName
    reportData["projectHierarchy"] = projectHierarchy
    reportData["projectName"] = projectHierarchy["name"]
    reportData["projectID"] = projectHierarchy["id"]
    reportData["projectList"] = projectList
    reportData["projectData"] = projectData


    logger.info("Exiting gather_data_for_report")

    return reportData


#----------------------------------------------#
def create_project_hierarchy(project, parentID, projectList, baseURL):
    logger.debug("Entering create_project_hierarchy")

    # Are there more child projects for this project?
    if len(project["childProject"]):

        # Sort by project name of child projects
        for childProject in sorted(project["childProject"], key = lambda i: i['name'] ) :

            nodeDetails = {}
            nodeDetails["projectID"] = childProject["id"]
            nodeDetails["parent"] = parentID
            nodeDetails["projectName"] = childProject["name"]
            nodeDetails["projectLink"] = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(childProject["id"]) + "&tab=projectInventory"
            nodeDetails["inventoryLinkBase"] = nodeDetails["projectLink"]  + "&pinv="

            projectList.append( nodeDetails )

            create_project_hierarchy(childProject, childProject["id"], projectList, baseURL)

    return projectList
    