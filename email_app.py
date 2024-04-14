from openai import OpenAI
import config
from email_categorizer import categorise_email
from langchain_openai import ChatOpenAI
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from operator import itemgetter
from googlesearch import search

#QUESTIONS
QUESTION = """
Booking Page Link: "https://tidycal.com/synergizeai/agent-test"

You are an email inbox manager for Synergize AI Team; Your goal is to help draft email response for the team.
If the client propose a meeting or ask for availability, send the link to the booking page with the email response so that they can book the meeting whenever they are available

KNOWLEDGE: {faq}

===
New email to reply:
NEW PROSPECT EMAIL: {email_address}
SUBJECT: {subject}
EMAIL: ''' {email} '''
FROM NAME: Synergize AI Team

===
GENERATE RESPONSE (Return ONLY the Body of the email. NO SUBJECT, RECEIPIENT NAME):
"""

#JOB_OFFER/CONSULTING2
CONSULTING = """
Booking Page Link: "https://tidycal.com/synergizeai/agent-test"

ALL NEEDS COLLECTED: {needs_collected}

You are an email inbox manager for Synergize AI Team; Your goal is to help with emais that are about Job offer or Consulting based on whether ALL NEEDS COLLECTED is YES or NO.

If ALL NEEDS COLLECTED is YES, send the link to the booking page with the email response so that they can book the meeting whenever they are available so that we can discuss the project further.

If ALL NEEDS COLLECTED is NO, then you must generate email response to the prospect to collect further info based on the following - 
1. What's the problem the prospect is trying to solve? 
2. Their budget?

If the client propose a meeting or ask for availability, send the link to the booking page with the email response so that they can book the meeting whenever they are available

===
Info about email:
NEW PROSPECT EMAIL: {email_address}
SUBJECT: {subject}
EMAIL: ''' {email} '''
FROM NAME: Synergize AI Team

===
GENERATE SUMMARY or RESPONSE (Return ONLY the Body of the email. NO SUBJECT, RECEIPIENT NAME):
"""

#COLLABORATION
COLLAB_COMPANY = """
Booking Page Link: "https://tidycal.com/synergizeai/agent-test"

COMPANY RESEARCH RESULT: {summary}

You are an email inbox manager for Synergize AI Team; Your goal is to forward the email to Diego (Synergize AI Team Manager) with the COMPANY RESEARCH RESULT.

If the client propose a meeting or ask for availability, send the link to the booking page with the email response so that they can book the meeting whenever they are available.

Return only the email sent to Diego.
===
Info about email:
NEW PROSPECT EMAIL: {email_address}
SUBJECT: {subject}
EMAIL: ''' {email} '''

===
FORWARDED EMAIL (Return ONLY the Body of the email. NO SUBJECT, RECEIPIENT NAME).
"""

#COLLABORATION
COLLAB_NO_COMPANY = """
Booking Page Link: "https://tidycal.com/synergizeai/agent-test"

You are an email inbox manager for Synergize AI Team; Your goal is to send an email back to the prospect for more information about their company.
You can also send the link to the booking page with the email response so that they can book the meeting whenever they are available.

===
Info about email:
NEW PROSPECT EMAIL: {email_address}
SUBJECT: {subject}
EMAIL: ''' {email} '''

===
RESPONSE (Return ONLY the Body of the email. NO SUBJECT, RECEIPIENT NAME).
"""

#Meeting
MEETING = """ 
Booking Page Link: "https://tidycal.com/synergizeai/agent-test"

You are an email inbox manager for Synergize AI Team;

Your goal is to help generate email response for the team and send them the link to the booking page above, so that they can book the meeting whenever they are available.

===
New email to reply:
NEW PROSPECT EMAIL: {email_address}
SUBJECT: {subject}
EMAIL: ''' {email} '''
FROM NAME: Synergize AI Team

===
GENERATE RESPONSE (Return ONLY the Body of the email. NO SUBJECT, RECEIPIENT NAME):
"""


class EmailGenerator:
    def __init__(self):
        openai_api_key = config.openai_key
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=openai_api_key
        )
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4", api_key=config.openai_key)
        self.faq = self.load_faq()

    def get_leads(self, company_name):
        company_info = list(search(f'{company_name}', advanced=True, num_results=1))
        company_info = company_info[0]
        url = company_info.url
        description = company_info.description
        summary = {
            'name': company_name,
            'url': url,
            'description': description 
        }
        return summary

    def get_email_category(self, email):
        email_obj = categorise_email(self.client, email)
        return email_obj
    
    def load_faq(self):
        faq_df = pd.read_csv('faq.csv')
        faq_str = [faq for faq in faq_df['Answer']]
        faq_str = '\n'.join(faq_str)
        return faq_str
    
    def question_get_chain(self, email, prospect_email, subject):
        PROMPT = ChatPromptTemplate.from_template(QUESTION)
        chain = (
            {
                "faq": itemgetter('faq'),
                'email_address': itemgetter('email_address'),
                'subject': itemgetter('subject'),
                'email': itemgetter('email'),
            }
            | PROMPT
            | self.llm
        )
        email_response = chain.invoke({
            'faq': self.faq,
            'email_address': prospect_email,
            'subject': subject,
            'email': email,
        })
        return email_response.content.replace('[Your Name]', 'Synergize AI Team')
    
    def consulting_chain(self, email, prospect_email, subject, needs_collected):
        prompt = ChatPromptTemplate.from_template(CONSULTING)
        chain = (
            {
                "needs_collected": itemgetter('needs_collected'),
                'email_address': itemgetter('email_address'),
                'subject': itemgetter('subject'),
                'email': itemgetter('email'),
            }
            | prompt
            | self.llm
        )
        email_response = chain.invoke({
            "needs_collected": needs_collected,
            'email_address': prospect_email,
            'subject': subject,
            'email': email,
        })
        return email_response.content.replace('[Your Name]', 'Synergize AI Team')
            
    def collab_chain(self, email, prospect_email, subject, company_info):
        print(company_info)
        if company_info['is_company'] == 'YES':
            prompt = ChatPromptTemplate.from_template(COLLAB_COMPANY)
        else:
            prompt = ChatPromptTemplate.from_template(COLLAB_NO_COMPANY)
        chain = (
            {
                "summary": itemgetter('summary'),
                'email_address': itemgetter('email_address'),
                'subject': itemgetter('subject'),
                'email': itemgetter('email'),
            }
            | prompt
            | self.llm
        )
        email_summary = chain.invoke({
            "summary": company_info['company_info'],
            'email_address': prospect_email,
            'subject': subject,
            'email': email,
        })
        return email_summary.content.replace('[Your Name]', 'Synergize AI Team')

    def meeting_chain(self, email, prospect_email, subject):
        PROMPT = ChatPromptTemplate.from_template(MEETING)
        chain = (
            {
                'email_address': itemgetter('email_address'),
                'subject': itemgetter('subject'),
                'email': itemgetter('email'),
            }
            | PROMPT
            | self.llm
        )
        email_response = chain.invoke({

            'email_address': prospect_email,
            'subject': subject,
            'email': email,
        })
        return email_response.content.replace('[Your Name]', 'Synergize AI Team')
