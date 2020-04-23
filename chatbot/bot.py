# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, CardAction, SuggestedActions, ActionTypes


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    
    def __init__(self):
        self.cur_q_id=0
        self.prev_q_id=-1

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
            'Thank you for using Asesor!! I am still being contructed. When I am completed, I will be able to redirect you to the self scheduling page.',
            'We have compiled the information we received into a nice report below. Please review it and modify/add/correct anything necessary.'
        ]

        self.cur_q_id=1

    async def on_message_activity(self, turn_context: TurnContext):
        #await turn_context.send_activity(f"You said 3 '{ turn_context.activity.text }'")
        
        #print("previous: "+str(self.prev_q_id))
        
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

        if self.cur_q_id >= 0: ques = self.ques_list[self.cur_q_id]
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
