
import json

def check_consulting_email(client, latest_reply: str):
    prompt = f"""
    EMAIL: {latest_reply}
    ---

    Above is an email about Job offer / consulting; Your goal is identify if all information above is mentioned:
    1. What's the problem the prospect is trying to solve? 
    2. Their budget

    If all info above is collected, return YES, otherwise, return NO; (Return ONLY YES or NO)

    ANSWER: 
    """

    all_needs_collected_result = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    all_needs_collected = all_needs_collected_result.choices[0].message.content

    return all_needs_collected

def check_collab_email(client, latest_reply: str):
    prompt = f"""
    EMAIL: {latest_reply}
    ---

    You are a company enrichment AI Agent with good knowledge of the web.
    Above is an email about Collaboration / Sponsorship; Your goal is to do a deep search about the company on the respective platforms to get the following information:

    Name
    Website
    Description
    Linkedin Url
    Facebook
    Twitter / X
    Instagram
    Revenue
    Employees
    Industry

    (Return JSON)

    JSON: 
    """

    company_info = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    company_info = company_info.choices[0].message.content
    return company_info
   
def check_company_in_email(client, latest_reply):
    prompt = f"""
    EMAIL: {latest_reply}
    ---

    You are an intelligent AI agent that can help extract the name of a company from a text.
    
    If company name is in email, return YES, otherwise, return NO; (Return ONLY YES or NO)

    ANSWER: 
    """

    name_in_email = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    ans = name_in_email.choices[0].message.content
    return ans   
    
def categorise_email(client, latest_reply: str):
    categorise_prompt = f"""
    EMAIL: {latest_reply}
    ---

    Your goal is to categorise the email based on categories below:

    1. COLLABORATION/SPONSORSHIP: These are emails where companies or individuals are reaching out to propose a collaboration or sponsorship opportunity with Synergize AI. They often include details about their product or service and how they envision the partnership.

    2. JOB_OFFER/CONSULTING: These emails involve individuals or companies reaching out to Synergize AI with a specific job or project they want the team to work on. This could range from developing an AI application to leading a specific activity.

    3. QUESTIONS: These emails involve individuals reaching out to Synergize AI with specific questions or inquiries. This could be about our videos, our knowledge on a specific topic, or our thoughts on a specific AI tool or technology.
    
    4. MEETING/AVAILABILITY: These emails involve individuals or company reaching out to Synergize AI with proposing a meeting, asking for availability or want to discuss their project or get more information about the tool.

    4. NON_REPLY: These are auto emails that don't need any response or involve companies or individuals reaching out to Synergize AI to offer their services. This could be a marketing agency offering to help us find sponsorship opportunities or a company offering a specific tool or service they think we might find useful.

    5. OTHER: These are emails that don't fit into any of the above categories.

    CATEGORY (Return ONLY the category name in capital):
    """

    category_result = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": categorise_prompt}
        ]
    )

    category = category_result.choices[0].message.content
    print(f'Category is - {category}')
    
    if category == "JOB_OFFER/CONSULTING":
        all_needs_collected = check_consulting_email(client, latest_reply)
        if all_needs_collected == "YES":
            return {
                "Category": "JOB_OFFER/CONSULTING",
                "Step 1": """Generate a summary of the following 1.What's the problem the prospect is trying to solve?  2.Their budget""",
                "all_needs_collected": all_needs_collected,
            }
        else:
            return {
                "Category": "JOB_OFFER/CONSULTING",
                "Step 1": """Generate email response to the prospect to collect further info based on the following - 
                            1. What's the problem the prospect is trying to solve? 
                            2. Their budget""",
                "Step 2": "Send generated email response to prospect",
                "all_needs_collected": all_needs_collected,
            }
    
    elif category == "COLLABORATION/SPONSORSHIP":
        is_company = check_company_in_email(client, latest_reply)
        if 'YES' in is_company:
            company_info = check_collab_email(client, latest_reply)
        else:
            company_info = '{"error": "No company name in email"}'
        return {
            "Category": "COLLABORATION/SPONSORSHIP",
            "Step 1": "Research about the prospect & company",
            "Step 2": "Forward the email to jason.zhou.design@gmail.com, with the research results included",
            'company_info': json.loads(company_info),
            "is_company": is_company,
        }
        
    elif category == "QUESTIONS":
        return {
            "Category": "QUESTIONS",
            "Step 1": "Generate email response based on guidelines",
            "Step 2": "Create email draft with the generated response",
        }
        
    elif category == "MEETING/AVAILABILITY":
        return {
            'Category': 'MEETING/AVAILABILITY',
            "Step 1": "Generate email response with the link to the meeting booking page",
            "Step 2": "Send the email to the prospect"
            
        }    
        
    elif category == 'NON_REPLY':
        return {
            'Category': 'NON_REPLY'
        }
        
    elif category == 'OTHER':
        return {
            'Category': 'OTHER'
        }
        
    else:
        pass
