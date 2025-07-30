import pandas as pd
import jira
def convert_dataframe_to_markdown(df):
    markdown = "*AI GENERATED SUMMARY TABLE*\n\n"
    markdown += "| " + " | ".join(df.columns) + " |\n"

    for index, row in df.iterrows():
        row_content = [str(val).replace('*', '') for val in row]
        markdown += "| " + " | ".join(row_content) + " |\n"
    
    return markdown

def post_comment_to_jira(issue_key, comment):
    try:
        jira.add_comment(issue_key, comment)
        print(f"Comment posted to issue {issue_key}.")
    except Exception as e:
        print(f"Failed to post comment to issue {issue_key}: {str(e)}")
