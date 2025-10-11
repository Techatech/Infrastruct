# Temporarily commented out due to nova_act installation issues on Windows
# Will need to install Visual Studio Build Tools or use alternative deployment method

from strands import Agent, tool
# from nova_act import NovaAct

# @tool
# def deploy_infrastructure(public_url: str, stack_name: str) -> str:
#         """
#         With public_url(s3_iac_url) and stack_name(env_name), automates tasks in browser based on instructions provided to deploy a cloudformation IaC .

#         Args:
#             public_url (str): public S3 bUcket url obtained from the gen_template tool
#             stack_name (str): the stack name for the template obtained from the gen_template tool

#         Returns:
#             str: The result of the action performed.
#         """
#         starting_url = "https://console.aws.amazon.com/cloudformation/home"
#         instr = f"""
#          You have to act on the following instructions:

#         1. if the login page comes up, wait for user to login then check every 10 seconds
#            whether the browser has navigated away from login to a cloudformation url page then
#            proceed to instruction 2, Else if no login page comes up then procced to instruction 2.
#         2. Click on the "Create Stack" button or the "Create Stack" Link on the web page and wait for page load
#            then proceed to instruction 3.
#         3. If current browser page is displaying a "Create Stack" header and
#            the page title  contains "CloudFormation - Create Stack" proceed to instruction 4,
#            else if the current browser page is not displaying a "Create Stack" header and
#            the page title does not  contain "CloudFormation - Create Stack" then
#            redirect to the following url: "https://console.aws.amazon.com/cloudformation/home"
#            and repeat these instructions starting from Instruction 1.
#         4. On the "Create Stack" page, under the heading "Prerequisite - Prepare template"
#            and the sub-heading "Prepare template" select "Choose an existing template" option
#            then proceed to instruction 5.
#         5. On the same "Create Stack" page, under the heading "Specify template"
#            and the sub-heading "Template source" select "Amazon S3 URL" option
#            then proceed to instruction 6.
#         6. On the same "Create Stack" page, under the heading "Specify template"
#            and the sub-heading "Amazon S3 URL" enter the following url :"{public_url}" ih the textfield
#            then proceed to instruction 7.
#         7. On the same "Create Stack" page, navigate to the bottom right corner where there are two buttons or links
#            named "Cancel" and "Next". Click on the "Next" Button or the "Next" link, wait for page load
#            then proceed to instruction 8.
#         8. On the "Specify stack details" page, under the heading "Provide a stack name"
#            enter the stack name : "{stack_name}" in the text field
#            then proceed to instruction 9.
#         9. On the same "Specify stack details" page, navigate to the bottom right corner where there are three buttons or links
#            named "Cancel", "Previous" and "Next". Click on the "Next" Button or the "Next" link, wait for page load
#            then proceed to instruction 10.
#         10. On the "Configure stack options" page, leave all settings as they are, then navigate to the bottom right corner
#             where there are three buttons or links named "Cancel", "Previous" and "Next". Click on the "Next" Button or 
#             the "Next" link, wait for page load then proceed to instruction 11.
#         11. On the "Review and create" page, leave all settings as they are, then navigate to the bottom right corner
#             where there are three buttons or links named "Cancel", "Previous" and "Submit". Click on the "Submit" Button or 
#             the "Submit" link, wait for page load then proceed to instruction 12.
#         12. On the current page with page title:"CloudFormation - Stack {stack_name}", under the heading :"{stack_name}"
#             navigate to "Stack Info" tab and click it. Within the same tab, under the heading:"Overview", identify 
#             a label with the name "Status" and wait for its value to read or update to "CREATE_COMPLETE" before
#             proceeding to instruction 13.
#         13. Send back a response in the following format:" Deployment for Environment: {stack_name} was successful. Please sign out of your AWS ACCOUNT"
#         """
#         with NovaAct(
#                 starting_page=starting_url
#         ) as browser:
#             try:
#                 result = browser.act(instr, max_steps=15)
#                 return result.response

#             except Exception as e:
#                 error_msg = f"Error processing instruction: {instr}. Error: {str(e)}"
#                 print(error_msg)
#                 return error_msg

# Placeholder function until nova_act is properly installed
@tool
def deploy_infrastructure(public_url: str, stack_name: str) -> str:
    """
    Placeholder deployment function - nova_act currently unavailable.
    
    Args:
        public_url (str): public S3 bucket url obtained from the gen_template tool
        stack_name (str): the stack name for the template obtained from the gen_template tool
    
    Returns:
        str: Instructions for manual deployment
    """
    return f"""
    DEPLOYMENT STEPS:
    1. Go to AWS CloudFormation Console
    2. Create Stack → Use S3 URL: {public_url}
    3. Stack name: {stack_name}
    4. Review and deploy
    
    Status: Ready for manual deployment
    """


