
def check_consulting_email(client, lates_reply: str):
    prompt = f"""
    EMAIL: {lates_reply}
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

def categorise_email(client, latest_reply: str):
    categorise_prompt = f"""
    EMAIL: {latest_reply}
    ---

    Your goal is to categorise the email based on categories below:

    1. COLLABORATION/SPONSORSHIP: These are emails where companies or individuals are reaching out to propose a collaboration or sponsorship opportunity with Synergize AI. They often include details about their product or service and how they envision the partnership.

    2. JOB_OFFER/CONSULTING: These emails involve individuals or companies reaching out to Synergize AI with a specific job or project they want the team to work on. This could range from developing an AI application to leading a specific activity.

    3. QUESTIONS: These emails involve individuals reaching out to Synergize AI with specific questions or inquiries. This could be about our videos, our knowledge on a specific topic, or our thoughts on a specific AI tool or technology.

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
        all_needs_collected = check_consulting_email(latest_reply)
        if all_needs_collected == "YES":
            return {
                "Category": "JOB_OFFER/CONSULTING",
                "Step 1": """Forward the email to jason.zhou.design@gmail.com, with summary of 1.What's the problem the prospect is trying to solve?  2.Their budget"""
            }
        else:
            return {
                "Category": "JOB_OFFER/CONSULTING",
                "Step 1": "Generate email response to the prospect to collect further info based on guidelines",
                "Step 2": "Send generated email response to prospect",
            }
    elif category == "COLLABORATION/SPONSORSHIP":
        return {
            "Category": "COLLABORATION/SPONSORSHIP",
            "Step 1": "Research about the prospect & company",
            "Step 2": "Forward the email to jason.zhou.design@gmail.com, with the research results included"
        }
    elif category == "QUESTIONS":
        return {
            "Category": "QUESTIONS",
            "Step 1": "Generate email response based on guidelines",
            "Step 2": "Create email draft with the generated response",
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