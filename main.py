from fastapi import FastAPI, Query
from typing import List
from email_app import EmailGenerator
import json

email_gen = EmailGenerator()

app = FastAPI()

@app.get("/generate_email/")
def get_generated_email_response(q: List[str] = Query(None)):
    email = q[0]
    prospect_email = q[1]
    subject = q[2]
    email_info = email_gen.get_email_category(email)
    if email_info:
        if 'QUESTIONS' in email_info['Category']:
            generated_email = email_gen.question_get_chain(email, prospect_email, subject)
            return {
                'drafted_email': generated_email,
                'category': email_info['Category']
            }
        
        elif 'JOB_OFFER/CONSULTING' in email_info['Category']:
            email_summary = email_gen.consulting_chain(email, prospect_email, subject, needs_collected=email_info['all_needs_collected'])
            return {
                'drafted_email': email_summary,
                'category': email_info['Category'],
                'needs_collected': email_info['all_needs_collected']
            }
        
        elif ('NON_REPLY' in email_info['Category']) or ('OTHER' in email_info['Category']):
            return {
                'email': email,
                'category': email_info['Category']
            }
            
        elif 'COLLABORATION/SPONSORSHIP' in email_info['Category']:
            company_summary = email_gen.collab_chain(email, prospect_email, subject, company_info=email_info['company_info'])
            return {
                'company_summary': company_summary,
                'category': email_info['Category'],
                'company_info': email_info['company_info']
            }      
        
        elif "MEETING/AVAILABILITY" in email_info['Category']:
            generated_email = email_gen.meeting_chain(email, prospect_email, subject)
            return {
                'drafted_email': generated_email,
                'category': email_info['Category']
            }
    else:
        return {
            'email': email,
            'category': 'OTHER'
        }
