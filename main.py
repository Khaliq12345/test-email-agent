from fastapi import FastAPI, Query
from typing import List
from email_app import EmailGenerator
import json

email_gen = EmailGenerator()

app = FastAPI()

@app.get("/generate_email/")
def get_generated_email_response(q: List[str] = Query(None)):
    query_json = {
        'email': q[0],
        'prospect_email': q[1],
        'subject': q[2]
    }
    email_info = email_gen.get_email_category(q[0])
    if email_info:
        if 'QUESTIONS' in email_info['Category']:
            generated_email = email_gen.question_get_chain(q[0], q[1], q[2])
            return {
                'drafted_email': generated_email,
                'category': email_info['Category']
            }
    else:
        return None
