from .jira_interaction import extract_parent_issue, scan_for_cloned_jiras_with_sprt
from .ai_integration import generate_ai_test_status, generate_ai_summary
from .utils import convert_dataframe_to_markdown, post_comment_to_jira
import pandas as pd
import jira
def process_single_issue(issue_key):
    try:
        issue = jira.issue(issue_key)
        parent_issue_key = extract_parent_issue(issue.key)
        if parent_issue_key:
            cloned_data = scan_for_cloned_jiras_with_sprt(parent_issue_key)
            if cloned_data:
                all_data = {parent_issue_key: {"JIRAs_in_Filter": issue.key, "Clones": cloned_data}}
                generate_summary_table(all_data)
            else:
                print(f"Parent issue {parent_issue_key} is not accessible or has no clones.")
        else:
            print(f"No parent issue key found for issue {issue.key}.")
    except Exception as e:
        print(f"Error processing issue {issue_key}: {e}")

def generate_summary_table(all_data):
    for parent_key, data in all_data.items():
        if not data['Clones']:
            continue

        serial_no = 1
        clones_info = []

        for clone in data['Clones']:
            resolution_status = clone["Resolution_Status"]
            resolution_type = clone["Resolution_Type"]

            ai_test_status = generate_ai_test_status(clone["Comments"], clone["Labels"])
            ai_summary = generate_ai_summary(clone)

            clones_info.append({
                "Serial No": serial_no,
                "Previous SPRT issue": clone["Clone_JIRA_Key"],
                "Platform Name": clone["Platform_Type"],
                "Desset": clone["Desset"],
                "Component": ', '.join(clone["Components"]), 
                "Resolution Status": resolution_status,
                "Resolution Reason": resolution_type,
                "Test data(AI in use)": ai_test_status,
                "AI Summary": ai_summary
            })
            serial_no += 1

        summary_df = pd.DataFrame(clones_info)
        if not summary_df.empty:
            comment_text = convert_dataframe_to_markdown(summary_df)
            post_comment_to_jira(data['JIRAs_in_Filter'], comment_text)
