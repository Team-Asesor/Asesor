# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, CardAction, SuggestedActions, ActionTypes
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from botbuilder.ai.luis import LuisApplication, LuisRecognizer
from botbuilder.core import Recognizer, RecognizerResult, TurnContext

from config import DefaultConfig


class IntentRecognizer(Recognizer):
    def __init__(self):
        configuration=DefaultConfig()
        self._recognizer = None
        if configuration.LUIS_APP_ID and configuration.LUIS_API_KEY and configuration.LUIS_API_HOST_NAME:
            luis_application = LuisApplication(configuration.LUIS_APP_ID, configuration.LUIS_API_KEY, "https://" + configuration.LUIS_API_HOST_NAME)
            self._recognizer = LuisRecognizer(luis_application)

    @property
    def is_configured(self) -> bool:
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)

class Result():
    def __init__(self):
        self.data={}
        self.data['AddSymptom']={}
        self.data['AddSymptom']['Status'] = ""
        self.data['AddSymptom']['Onslaught'] = ""
        self.data['AddSymptom']['Symptoms'] = ""
        self.data['AddSymptom']['Severity'] = ""

        self.data['AddHistory']= {}
        self.data['AddHistory']['History'] = ""
        self.data['AddHistory']['Status'] = ""
        self.data['AddHistory']['Onslaught'] = ""

        self.data['AddMedication'] = {}
        self.data['AddMedication']['Medication'] = ""
        self.data['AddMedication']['Dosage'] = ""

        self.data['AddAllergy']= {}
        self.data['AddAllergy']['Status'] = ""
        self.data['AddAllergy']['Onslaught'] = ""
        self.data['AddAllergy']['Allergy'] = ""
        self.data['AddAllergy']['Severity'] = ""


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    def authenticate_client(self):
        ta_credential = AzureKeyCredential(self.key)
        text_analytics_client = TextAnalyticsClient(
                endpoint=self.endpoint, credential=ta_credential)
        return text_analytics_client
    
    def sentiment_analysis_example(self, client, documents):
        #documents = ["I had the worst day of my life"]
        response = client.analyze_sentiment(documents = [documents])[0]
        print("Document Sentiment: {}".format(response.sentiment))
        print("Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
            response.confidence_scores.positive,
            response.confidence_scores.neutral,
            response.confidence_scores.negative,
        ))
        for idx, sentence in enumerate(response.sentences):
            print("[Length: {}]".format(sentence.grapheme_length))
            print("Sentence {} sentiment: {}".format(idx+1, sentence.sentiment))
            print("Sentence score:\nPositive={0:.2f}\nNeutral={1:.2f}\nNegative={2:.2f}\n".format(
                sentence.confidence_scores.positive,
                sentence.confidence_scores.neutral,
                sentence.confidence_scores.negative,
            ))
        return response.sentiment

    def parse_json(self, recognizer_result):
        intent = (
            sorted(
                recognizer_result.intents,
                key=recognizer_result.intents.get,
                reverse=True,
            )[:1][0]
            if recognizer_result.intents
            else None
        )
        intent=str(intent)
        print("intent is: "+intent)
        return self.parse(recognizer_result, intent)

    def parse(self, dict_response, intent):
        output_dict=Result()
        if intent in output_dict.data:
            entities = dict_response.entities['$instance'].keys()
            print("entities are: ")
            print(type(entities))
            print(entities)
            for entity in entities:
                if entity in output_dict.data[intent].keys():
                    print(entity)
                    val=dict_response.entities['$instance'][entity]
                    output_dict.data[intent][entity]=val[0]['text']

            print("returning the following dictionary: ")
            print(output_dict.data[intent])
            return intent, output_dict.data[intent]
        print("returning the following dictionary: ")
        print({'val':'empty'})
        return intent, {'val':'empty'}

    def __init__(self):
        self.cur_q_id=0
        self.prev_q_id=-1
        self.key="0ccf217ddc3642eba4a838cb54b7fd29"
        self.endpoint="https://asesorsa.cognitiveservices.azure.com/"
        self.recognizer = IntentRecognizer()
        self.ques_list = [
            'Greetings!!',
            'What brings you in today? Would you like to follow up on a previous visit or start a new one?',
            'What are the symptoms that you are experiencing? Please give a brief description. (You may want to mention severity, when it started happening and how often it happens.)',
            'Are there any medications that you’re taking currently? Please briefly mention why you take them, dosage and how long you’ve been taking them.',
            'From the previous reports we have listed below, please select which visit you are following-up on.',
            'Would you say your condition has improved?',
            'Please mention the symptoms and side-effects that you’re experiencing now. Please give a brief description. (You may want to mention severity, when it started happening and how often it happens.)',
            'Antibiotics and Cough Syrup have been prescribed in your previous visit(s). Are you taking those medications or any other medications currently? Please also mention dosage and how long you’ve been taking them.',
            'I see that you have had Asthma in the past. Is there anything else you would like to add to your medical history?',
            'Please describe any other the problems you would like to add. Please touch on when it happened, if it is still ongoing, and its severity.',
            'You have reported that you are allergic to Peanut and Pollen. Are there any new allergies you would like to report?',
            'Please describe any new allergies you would like to add. Please touch on when it started and its severity.',
            'Please describe your history of drug and substance abuse',
            'Please describe your sexual history',
            'Please describe your menstrual history',
            'Please describe your pregnancy history',
            'Is there any more information you think is important for the doctor to know at a first glance? Please feel free to speak your mind.',
            'Thank you for using Asesor!! I am still being constructed. When I am completed, I will be able to redirect you to the self scheduling page.',
            'We have compiled the information we received into a nice report below. Please review it and modify/add/correct anything necessary.'
        ]

        self.cur_q_id=1

    async def on_message_activity(self, turn_context: TurnContext):
        #await turn_context.send_activity(f"You said 3 '{ turn_context.activity.text }'")
        
        #print("previous: "+str(self.prev_q_id))
        res= await self.recognizer.recognize(turn_context)
        intent, parsed_result=self.parse_json(res)
        client = self.authenticate_client()
        response=self.sentiment_analysis_example(client, str(turn_context.activity.text).lower())
        prefix=""
        if response=="positive":
            prefix="Good to hear it! "
        elif response=="negative":
            prefix="Sorry to hear it! "
        else:
            prefix=""
        if self.prev_q_id == -1:
            self.cur_q_id = 1

        elif self.prev_q_id == 1:
            if "new" in str(turn_context.activity.text).lower():
                self.cur_q_id = 2
            else:
                self.cur_q_id = 4

        elif self.prev_q_id == 3:
            self.cur_q_id = 8

        elif self.prev_q_id == 8:
            if "yes" in str(turn_context.activity.text).lower():
                self.cur_q_id = 9
            else:
                self.cur_q_id = 10

        elif self.prev_q_id == 10:
            if "yes" in str(turn_context.activity.text).lower():
                self.cur_q_id = 11
            else:
                self.cur_q_id = 16

        elif self.prev_q_id == 11:
            self.cur_q_id = 16

        elif self.prev_q_id==17:
            self.cur_q_id = 0
            self.prev_q_id = -1

        else:
            self.cur_q_id = self.prev_q_id + 1
        #print("current: "+str(self.cur_q_id))

        if self.cur_q_id >= 0: 
            ques = self.ques_list[self.cur_q_id]
        else: ques=None


        if self.cur_q_id==4:
            ques = MessageFactory.text(ques)
            ques.suggested_actions = SuggestedActions(
                actions=[
                    CardAction(title="1. Asthma Treatment Jan 15", type=ActionTypes.im_back, value="1. Asthma Treatment Jan 15"),
                    CardAction(title="2. Skin Infection Feb 12", type=ActionTypes.im_back, value="2. Skin Infection Feb 12"),
                    CardAction(title="3. Bipolar Syndrome March 21", type=ActionTypes.im_back, value="3. Bipolar Syndrome March 21"),
                ]
            )

        if self.cur_q_id!=4:
            await turn_context.send_activity("Your Intention is this: "+str(intent))
            await turn_context.send_activity("I also got the following info: " + str(parsed_result))
            await turn_context.send_activity(prefix+ques)
        else:
            await turn_context.send_activity(ques)

        self.prev_q_id = self.cur_q_id

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Welcome user!! Ready to test Asesor chatbot feature?")
            else:
                self.cur_q_id = 0
                self.prev_q_id = -1
