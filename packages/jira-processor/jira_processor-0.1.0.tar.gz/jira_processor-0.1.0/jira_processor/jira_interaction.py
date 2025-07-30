from jira import JIRA
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables for JIRA server, username, and password
JIRA_SERVER = os.getenv('JIRA_SERVER')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_PASSWORD = os.getenv('JIRA_PASSWORD')

# Initialize JIRA connection using server URL and basic authentication
jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))

def extract_parent_issue(issue_key):
    try:
        issue = jira.issue(issue_key)
        description = issue.fields.description

        if description:
            first_line = description.splitlines()[0]
            colon_index = first_line.find(':')
            if colon_index != -1:
                parent_issue_key = first_line[:colon_index].strip().split()[0].strip().split('{')[0].strip()
                return parent_issue_key

        return None
    except Exception as e:
        print(f"Error extracting parent issue for {issue_key}: {str(e).splitlines()[0]}")
        return None

def scan_for_cloned_jiras_with_sprt(parent_issue_key):
    try:
        issue = jira.issue(parent_issue_key)
        cloned_data = []

        for link in issue.fields.issuelinks:
            if hasattr(link, 'inwardIssue'):
                inward_issue = link.inwardIssue
                link_type = link.type.name

                if '_SPRT' in inward_issue.fields.summary and link_type == 'Mention':
                    try:
                        cloned_issue = jira.issue(inward_issue.key, fields='summary,comment,resolution,status,labels,components')
                        platform_type, dessert = extract_platform_and_desset(cloned_issue.fields.summary)
                        
                        comments = [{"author": comment.author.displayName, "body": comment.body} for comment in cloned_issue.fields.comment.comments or []]
                        resolution_name = cloned_issue.fields.resolution.name if cloned_issue.fields.resolution else "Unresolved"
                        resolution_status = cloned_issue.fields.status.name if cloned_issue.fields.status else "Unknown"
                        components = [component.name for component in cloned_issue.fields.components]

                        cloned_data.append({
                            "Clone_JIRA_Key": cloned_issue.key,
                            "Summary": cloned_issue.fields.summary,
                            "Resolution_Type": resolution_name,
                            "Resolution_Status": resolution_status,
                            "Comments": comments,
                            "Labels": cloned_issue.fields.labels,
                            "Platform_Type": platform_type,
                            "Desset": dessert,
                            "Components": components
                        })
                        print(f"Cloned JIRA {inward_issue.key} accessed successfully.")
                    except Exception as e:
                        print(f"Skipping inaccessible cloned issue {inward_issue.key}: {str(e).splitlines()[0]}")
                        continue

        return cloned_data
    except Exception as e:
        print(f"Error accessing parent issue {parent_issue_key}: {str(e).splitlines()[0]}")
        return []

def extract_platform_and_desset(summary):
    try:
        parts = summary.split()
        if len(parts) > 0:
            platform_desset = parts[0]
            platform_type, dessert = platform_desset.split('_')[:2]
            return platform_type, dessert
        else:
            return None, None
    except Exception as e:
        print(f"Error extracting platform and dessert: {str(e).splitlines()[0]}")
        return None, None
