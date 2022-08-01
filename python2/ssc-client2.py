import requests
import sys, getopt
from pprint import pprint

baseURL = "http://sscurl/ssc/api/v1/"
authURL = baseURL + "auth/obtain_token"
projectURL = baseURL + "projects?start=-1&limit=-1"


authHeaders = {
	'accept': "application/json, text/plain; */*",
	'content-type': "application/json;charset=UTF-8",
	'accept-encoding': "application/gzip",
	'cache-control': "no-cache",
	'authorization': "Basic <insert basic token>", ## insert the base64 token here fortify ssc creds like echo "user:pass" | base64
	}
#
# This function will get project information and return the assocaited project ID for the project
#
def getProject( projectHeaders, projectName, projectVersion, projectURL ):
	print "Performing Project Lookup....................\n"
	# Connect to Project Resource to get details on available projects
	print "Connecting to "  + projectURL +  " ...............................\n"

	try:
		projectResponse = requests.request("GET", projectURL, headers=projectHeaders, verify=False)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Project Response Status Code = "  + str(projectResponse.status_code) +   "\n"
		print "-------------------------------------- \n"
		sys.exit(1)

	if projectResponse.status_code == 200 :
		projectJSON = projectResponse.json()
		projectList = projectJSON['data']

		for projectDict in projectList :
			if projectDict['name'] == projectName :
				projectID = projectDict['id']
				print "Project ID Was located.........................................\n"
				print "\n--------------- Project ID from Lookup,  "  + str(projectID)  + "\n"
				print "Project ID " + str(projectID)
				versionID = getProjectVersion( projectHeaders, baseURL, projectID, projectVersion, projectName )
				return projectID;
				break
		else:
			print "Project ID was not found, creating new project...................................."
			
			returnedVersionID = createProject(projectName, projectVersion, projectHeaders )
			#print "Project ID after project creation "   str(versionID)   "\n"
			print "Project Version ID after project creation "  + str(returnedVersionID)  + "\n"
			updateProjectAttributes( projectHeaders, returnedVersionID, projectVersion, projectName)
			updateProject( projectHeaders, returnedVersionID, projectVersion, projectName )
			return returnedVersionID;

	else :
		print "Project Request experienced an error and returned response code "  + str(projectResponse.status_code) +   "\n"

#
# This function will get project version information and return the assocaited project ID for the project
#
def getProjectVersion( projectHeaders, baseURL, projectID, projectVersion, projectName ):
	#Get the Project Version data
	print "Looking up Project Version information.........................\n"
	projectVersionURL = baseURL + "projects/" + str(projectID) +  "/versions"
	print "\nConnecting to "  + projectVersionURL +   " ...............................\n"
	try:
		projectVersionResponse = requests.request("GET", projectVersionURL, headers=projectHeaders, verify=False)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Project Version Response Status Code = "  + str(projectVersionResponse.status_code)  + "\n"
		print "-------------------------------------- \n"
		sys.exit(1)

	if projectVersionResponse.status_code == 200 :
		projectVersionJSON = projectVersionResponse.json()
		#pprint(projectVersionJSON)
		# Grab the Data Dictionariy from the JSON
		projectVersionList = projectVersionJSON['data']
		#pprint( projectVersionList )
		# The project version call returns a list of dictionaries.  Loop through the list to get individual dictionaries
		# After obtaining the individial dictionaries look through each one to see if any of them have a projectVersion that matches
		# out project version.
		for projectVersionDict in projectVersionList :
			if projectVersionDict['name'] == projectVersion :
				lookupVersionID = projectVersionDict['id']
				print "Project Version ID Was located.........................................\n"
				print "\n--------------- Project Version ID is: "  + str(lookupVersionID) +  "\n"
				return lookupVersionID;
				break
		else:
			print "Project Version was not found, We need to create a new project ..............................\n"
			createVersion( projectHeaders, projectID, projectVersion, projectName )
	return;

def createProject (projectName, projectVersion, projectHeaders ):
	print "\n................................."
	print "\n Creating new project................................................"

	url = "http://sscurl/ssc/api/v1/projectVersions"

	payload = "{\"project\":{\"name\":\"" + projectName + "\",\"description\":\"Created with SSC Client\",\"issueTemplateId\":\"Prioritized-HighRisk-Project-Template\",\"committed\": \"true\"},\"masterAttrGuid\":\"87f2364f-dcd4-49e6-861d-f8d3f351686b\",\"name\":\"" + projectVersion + "\",\"description\":\"Created with SSC Client\",\"issueTemplateId\":\"Prioritized-HighRisk-Project-Template\",\"owner\": \"SSC Client\",\"active\": \"true\",\"committed\": \"false\"}"
	try:
		response = requests.request("POST", url, data=payload, headers=projectHeaders, verify=False)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Response Status Code = "  + str(response.status_code) +  "\n"
		print "-------------------------------------- \n"
		sys.exit(1)
	print "\n--------------- Project Creation JSON --------------- \n"
	print(response.text)
	if response.status_code == 201 :
		projectJSON = response.json()
		projectData = projectJSON['data']
		versionID = projectData['id']
		print "\n.............................. Project Version ID after Project Creation .............................. \n"
		print "ProjectVersionID = "  + str(versionID)
		print "\n....................................................................................................... \n"
		return versionID;
	else:
		return;
		
def createVersion( projectHeaders, projectID, projectVersion, projectName ):
	print "Creating new Project Version.............................................\n"
	print "Creating project Version "   + projectVersion +  " with project ID of " +  str(projectID)  + "\n"
	url = "http://sscurl/ssc/api/v1/projects/" + str(projectID) + "/versions"

	payload = "{\n\t\"masterAttrGuid\":\"87f2364f-dcd4-49e6-861d-f8d3f351686b\",\n\t\"name\":\"" + projectVersion + "\",\n\t\"description\":\"Created with SSC Client\",\n\t\"issueTemplateId\":\"Prioritized-HighRisk-Project-Template\",\n\t\"owner\": \"SSC Client\",\n\t\"active\": \"true\",\n\t\"committed\": \"true\"\n}"
	print "Creating project version by connecting to " +url
	try:
		response = requests.request("POST", url, data=payload, headers=projectHeaders, verify=False)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Response Status Code = "  + str(response.status_code) +  "\n"
		print "-------------------------------------- \n"
		sys.exit(1)
	print projectID
	print response.status_code
	if response.status_code == 201 :
		projectJSON = response.json()
		pprint( projectJSON )
		projectData = projectJSON['data']
		versionID = projectData['id']
		print "\n.............................. Project Version ID after Project Creation .............................. \n"
		print "ProjectVersionID = " + str(versionID)
		print "\n....................................................................................................... \n"
		updateProjectAttributes( projectHeaders, versionID, projectVersion, projectName )
		updateProject( projectHeaders, versionID, projectVersion, projectName )
		return;
	return;


def updateProjectAttributes( projectHeaders, projectID, projectVersion, projectName ):
	print "Updating Project Attributes ................................................\n"
	print "Updating project Attributes for project " +  projectName  + " with project id of, "  + str(projectID)  + "\n"
	url = "http://sscurl/ssc/api/v1/projectVersions/"  + str(projectID) +  "/attributes"
	

	payload = "[\n\t{\n\t  \"guid\":\"DevPhase\",\n\t  \"attributeDefinitionId\":\"5\",\n\t  \"values\": [ \n\t\t\t\t  {\"guid\":\"Active\"} \n\t\t\t    ]\n\t},\n\t\t{\n\t\t\"guid\":\"Accessibility\",\n\t\t\"attributeDefinitionId\":\"7\",\n\t\t\"values\": [\n\t\t\t\t\t{\"guid\":\"externalpublicnetwork\"}\n\t\t\t\t  ]\n\t},\n\t{\n\t\t\"guid\":\"DevStrategy\",\n\t\t\"attributeDefinitionId\":\"6\",\n\t\t\"values\": [\n\t\t\t\t\t{\"guid\":\"Internal\"}\n\t\t\t\t  ]\n\t}\n\n]\n\t\n\t\n\t"

	try:
		response = requests.request("PUT", url, data=payload, headers=projectHeaders, verify=False)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Response Status Code = "  + str(response.status_code) +  "\n"
		print "-------------------------------------- \n"
		sys.exit(1)

	print "Project Attribute Update Completed................................\n"
	return;

def updateProject( projectHeaders, projectID, projectVersion, projectName ):
	print "Updating Project Version Status to Committed ................................................\n"
	print "Changing Project Version Status to Committed for project " +  projectName +  " with with project id of, "  + str(projectID) +  "\n"
	
	url = "http://sscurl/ssc/api/v1/projectVersions/" + str(projectID)+ "/"
	print "Connecting to " + url
	
	payload = "{\"project\":{\"name\":\"" + projectName + "\",\"description\":\"Created with SSC Client\",\"issueTemplateId\":\"Prioritized-HighRisk-Project-Template\",\"committed\": \"true\"},\"masterAttrGuid\":\"87f2364f-dcd4-49e6-861d-f8d3f351686b\",\"name\":\"" + projectVersion + "\",\"description\":\"Created with SSC Client\",\"issueTemplateId\":\"Prioritized-HighRisk-Project-Template\",\"owner\": \"SSC CLIENT\",\"active\": \"true\",\"committed\": \"true\"}"
	print payload
	try:
		response = requests.request("PUT", url, data=payload, headers=projectHeaders)
		print(response.text)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Response Status Code = " +  str(response.status_code)  +  "\n"
		print "-------------------------------------- \n"
		sys.exit(1)
	return;
	
def main(argv):

	projectName = ''
	projectVersion = ''
	
	try:
		opts, args = getopt.getopt(argv, "hn:v:d", ["help", "projectName=", "projectVersion="])
	except getopt.GetoptError:
		print 'ssc-client.py -n <projectName> -v <projectVersion>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'ssc-client.py -n <projectName> -v <projectVersion>'
			sys.exit()
		elif opt in ("-n", "--projectName"):
			projectName = arg
		elif opt in ("-v", "--projectVersion"):
			projectVersion = arg
	print "\nProject Name entered is: " + projectName
	print "\nProject Version entered is: " + projectVersion
	print "\nPerforming Initial Authentication................................."
	print "\nConnecting to " +  authURL  + "\n"

	try:
		authResponse = requests.request("POST", authURL, headers=authHeaders, verify=False)
	except requests.exceptions.RequestException as e:
		print e
		print "-------------------------------------- \n"
		print "Auth Response Status Code = "  + str(authResponse.status_code)  +"\n"
		print "-------------------------------------- \n"
		sys.exit(1)

	if authResponse.status_code == 200 :

		authJSON = authResponse.json()
		data = authJSON['data']
		sscToken = data['token']
		print "SSC Token: " + sscToken + "\n"

		projectHeaders = {
			'accept': "application/json, text/plain, */*",
			'cache-control': "no-cache",
			'authorization': "FortifyToken " + sscToken,
			'content-type': "application/json; charset=utf-8",
			'accept-encoding': "gzip, deflate",
			}

		#projectID = getProject( projectHeaders, projectName, projectVersion, projectURL )
		getProject( projectHeaders, projectName, projectVersion, projectURL )

	else :
		print "Auth Request experienced an error and returned response code " + str(authResponse.status_code) + "\n"

if __name__ == "__main__":
	main(sys.argv[1:])