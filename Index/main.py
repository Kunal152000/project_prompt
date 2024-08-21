from flask import  Flask,request, jsonify
from openai import OpenAI
import os
import requests

app = Flask(__name__)

openAiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/",methods=["POST"])
def get_data():
    try:
        req_body= request.get_json()
        team_id= req_body.get('team_id')
        sheet_url=req_body.get('sheet_url')
        range=req_body.get('range')
        col_name=req_body.get('col_name')
        question=req_body.get('question')
        # print("after body",sheet_url)
        api_url = 'https://us-central1-udhyam-tech.cloudfunctions.net/googleSheetApiCall'
        # print("after url ",api_url)
        payload = {
            "spreadsheetUrl":sheet_url,
             "range":range,
             "columnName":col_name,
             "value":team_id
        }
        response = requests.post(api_url,json=payload)
        response_json = response.json()
        # print("response",response_json)

        if 'result' in response_json:
            summary = response_json['result']['0']['Summary v7 (100w)']
            result = chatGpt_response(summary, question)
            return jsonify({"Result": result, "summary": summary})
        elif 'Error' in response_json:
            return jsonify({"error": "Please provide correct team_id"})
        else:
            return jsonify({"error": "Unexpected response format"})

    except Exception as e:
        return jsonify({"error":f"An error occured in get_data {e}"})

def chatGpt_response(summary,question):
    try:
        prompt =  f"""You are an assistant for the SBIC (Societal and Business Innovation Challenge) educational program. This program involves 11th graders from government schools in Madhya Pradesh, India, working on business projects in two phases.
        Phase 1 (Pre-seed Money Phase):
        Students form teams, brainstorm business ideas, conduct market surveys, and create business plans.
        Each team submits a business plan and a pitch for their business idea.
        Selected teams move to Phase 2.
        Phase 2 (Post-seed Money Phase):
        Selected teams receive Rs. 2000 per student as seed money.
        Teams must complete 5 specific goals and submit their progress via WhatsApp by typing SUBMIT to     9513477756.
        Your Role:
        Answer queries from students or teachers related to their projects.
        Use simple language and short sentences.
        Use the same language as the question to provide the response.
        Keep responses under 100 words.
        Focus on actionable advice directly related to the project details.
         Project Details:
        Remember to keep responses concise, focused on actionable steps, and directly related to the students'      
        project goals.{summary}"""
        result =  openAiClient.chat.completions.create(model='gpt-4o',messages=[{'role':'system','content':prompt},{
         'role':'user','content':question
     }],temperature=0,max_tokens=1500,top_p=1,presence_penalty=0,frequency_penalty=0)
        response = result.choices[0].message.content
        return response
    except Exception as e:
        error_message = f'An error occurred in chatgpt_call: {str(e)}'
        return {'error': error_message}

# if __name__ == '__main__':
#     app.run(host="127.0.0.1",port=8080)
