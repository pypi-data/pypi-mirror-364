import openai

def generate_ai_test_status(comments, labels):
    prompt = (
        "Analyze the labels to determine the testing status of this JIRA issue. "
        "Provide a short status: Tested if the label contains 'ST_Tested', "
        "Tested and Resolved if both 'ST_Tested' and 'Resolved' are present, "
        "or test data not available."
        f" Comments: {comments}\nLabels: {labels}"
    )
    system_prompt = "Summarize the testing status of a JIRA issue in one or two simple words."
    return chat_with_gpt(prompt, system_prompt)

def generate_ai_summary(clone):
    # Filter comments to exclude AI-generated ones
    filtered_comments = [
        comment for comment in clone['Comments']
        if 'AI GENERATED' not in comment['body']
    ]

    # Prepare the prompt with adjusted instructions
    prompt = (
        f"Create a concise summary of JIRA issue {clone['Clone_JIRA_Key']} without using its title or summary. "
        f"Focus on the resolution details, filtered comments, testing process, and devices used. "
        f"Include any Gerrit links if available. "
        f"{'No developer comments available.' if not filtered_comments else ''} "
        f"Resolution: {clone['Resolution_Type']}, "
        f"Comments: {filtered_comments}, "
        f"Gerrit Links: {clone.get('Gerrit_Links', 'None')}"
    )

    system_prompt = "Provide a concise summary of a JIRA issue in one or two simple sentences without using its title or summary."
    return chat_with_gpt(prompt, system_prompt)
def chat_with_gpt(prompt, system_prompt):
    openai.api_key ='100BwZRwGcebmeB7PDHQC2ThO69jGdI3438iZ6HSrzCgXnBtRlGWJQQJ99BCACREanaXJ3w3AAABACOG48bP'
    
    openai.api_type = "azure"
    openai.api_base = 'https://emc-bsp-team-openai.openai.azure.com/'
    openai.api_version = '2024-10-21'
    
    deployment_name = "gpt-4o"
    
    response = openai.ChatCompletion.create(
        engine=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
    )
    
    return response.choices[0].message.content.strip()
