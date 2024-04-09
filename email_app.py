from openai import OpenAI
import config
from email_categorizer import categorise_email
from langchain_openai import ChatOpenAI
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from operator import itemgetter

#QUESTIONS
QUESTION_PROMPT_TEMPLATE = """
You are an email inbox manager for Synergize AI Team; Your goal is to help draft email response for the team.

KNOWLEDGE: {faq}

===
New email to reply:
NEW PROSPECT EMAIL: {email_address}
SUBJECT: {subject}
EMAIL: ''' {email} '''

===
GENERATE RESPONSE:
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

    def get_email_category(self, email):
        email_obj = categorise_email(self.client, email)
        return email_obj
    
    def load_faq(self):
        faq_df = pd.read_csv('faq.csv')
        faq_str = [faq for faq in faq_df['Answer']]
        faq_str = '\n'.join(faq_str)
        return faq_str
    
    def question_get_chain(self, email, prospect_email, subject):
        PROMPT = ChatPromptTemplate.from_template(QUESTION_PROMPT_TEMPLATE)
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
        return email_response
    


