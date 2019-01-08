import asana
import csv
import sys

outputdir = ''
outputfilename = 'asana-export.csv'

personal_access_token = sys.argv[1] #taken from command line
client = asana.Client.access_token(personal_access_token) #start session
me = client.users.me() #get user info
workspace = me['workspaces'][0] #set main workspace
print('Initialising Asana session for ' + me['name'] + ' in workspace: ' + workspace['name'])
projects = client.projects.find_by_workspace(workspace['gid'], iterator_type=None) #find projects within workspace
tasklist = []

print('\nLooping through all the tasks within the projects...\n')
for project in projects:
    print(project['name'])
    #opt_expand delivers all attributes (not a compact view) for each field    
    tasks = client.tasks.find_by_project(project['gid'], {"opt_expand":"name, \
        projects, workspace, gid, due_on, created_at, modified_at, completed, \
        completed_at, assignee, parent, notes, tags"}, iterator_type=None)
    
    for task in tasks:
        if task['completed'] == False: #build list of only open tasks
            #Truncate notes if needed
            #if len(task['notes']) > 80:
                #task['notes'] = task['notes'][:79]

            #Loop through tags applied to each task, extract from json and turn into comma separated string
            tags = task['tags']         
            if task['tags'] is not None:
                tagname=''
                i=0
                for tag in tags:
                    if i==0:
                        tagname = tag['name']
                    else:
                        tagname = tagname + ', ' + tag['name']
                    i=i+1        
            
            #deal with assignee being blank
            assignee = task['assignee']['name'] if task['assignee'] is not None else ''

            #cleaning up the dates so they're readable
            created_at = task['created_at'][0:10] + ' ' + task['created_at'][11:16] if \
                    task['created_at'] is not None else None
            modified_at = task['modified_at'][0:10] + ' ' + task['modified_at'][11:16] if \
                    task['modified_at'] is not None else None
            completed_at = task['completed_at'][0:10] + ' ' + task['completed_at'][11:16] if \
                task['completed_at'] is not None else None
            #build row
            row = [task['name'], project['name'], task['due_on'], created_at, \
                modified_at, task['completed'], completed_at, assignee, \
                task['parent'], task['notes'], task['gid'], tagname]
            row = ['' if s is None else s for s in row]
            tasklist.append(row)

print('\nExporting to csv file: ' + outputdir + outputfilename + '...') 
csvheader = ['Task', 'Projects', 'DueDate', 'CreatedAt', \
    'ModifiedAt', 'Completed', 'CompletedAt', 'Assignee', \
    'Parent', 'Notes', 'TaskId', 'Tags']
with open(outputdir + outputfilename, 'w', encoding='utf8') as csvfile:
    csvwriter = csv.writer(csvfile, lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(csvheader)
    for item in tasklist:
        csvwriter.writerow(item)

print('\nFinished!')
