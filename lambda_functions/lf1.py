import boto3
from botocore.exceptions import ClientError
import time
import os
import datetime
import logging

"""Send SQS"""

def sqs_send_message(message):
    sqs = boto3.client('sqs')
    url = 'https://sqs.us-east-1.amazonaws.com/082937965214/RestaurantQueue'
    msg_body = 'Message from LF1.'
    msg_attr = {
        'Location': {
            'DataType': 'String',
            'StringValue': message['Location']
        },
        'Cuisine': {
            'DataType': 'String',
            'StringValue': message['Cuisine']
        },
        'Date': {
            'DataType': 'String',
            'StringValue': message['Date']
        },
        'Time': {
            'DataType': 'String',
            'StringValue': message['Time']
        },
        'NumPeople': {
            'DataType': 'String',
            'StringValue': message['NumPeople']
        },
        'Email': {
            'DataType': 'String',
            'StringValue': message['Email']
        },
    }
    
    try:
        response = sqs.send_message(QueueUrl=url, MessageAttributes=msg_attr, MessageBody=msg_body)
        return 
    except ClientError as e:
        logging.error(e)

"""Intents"""

def greet(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi! How can I help you?'})

def thanks(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You\'re welcome!'})

def suggest(intent_request):
    cuisine = intent_request['currentIntent']['slots']['Cuisine']
    location = intent_request['currentIntent']['slots']['Location']
    num_people = intent_request['currentIntent']['slots']['NumPeople']
    email = intent_request['currentIntent']['slots']['Email']
    date = intent_request['currentIntent']['slots']['Date']
    time = intent_request['currentIntent']['slots']['Time']
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        slots = intent_request['currentIntent']['slots']
        
        validation_result = validate_suggest(cuisine, location, num_people, email, date, time)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
        
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        
        return delegate(output_session_attributes, intent_request['currentIntent']['slots'])
    
    sqs_send_message(intent_request['currentIntent']['slots'])

    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Great, you\'re all set. You can expect my suggestions shortly. Have a good day!'})

"""Helper Functions"""

def validate_suggest(cuisine, location, num_people, email, date, time):
    cuisine_types = ['chinese', 'indian', 'italian', 'japanese', 'mexican', 'korean']
    locations = ['new york', 'manhattan']
    now = datetime.date.today()
    
    if cuisine is not None and cuisine.lower() not in cuisine_types:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We currently do not support {}, would you like a different type of cuisine?'.format(cuisine))
    
    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'Location',
                                       'We currently do not support {}, would you like a different location?'.format(location))
    
    if num_people is not None:
        try:
            num_people = int(num_people)
            if num_people < 1 or num_people > 15:
                return build_validation_result(False,
                                               'NumPeople',
                                               'The maximum number of people is 15, would you like to book for a smaller group?')
        except ValueError:
            return build_validation_result(False,
                                           'NumPeople',
                                           'Please enter a valid number of people.')
    
    if date is not None:
        if len(date) != 10:
            return build_validation_result(False,
                                           'Date',
                                           'Please enter a valid date in the format YYYY/MM/DD.')
        conv_date = datetime.date.fromisoformat(date)
        if conv_date < now:
            return build_validation_result(False,
                                           'Date',
                                           'Please enter a valid date.')
        
    if time is not None:
        if len(time) != 5:
            return build_validation_result(False,
                                           'Time',
                                           'Please enter a valid time in the format HH:MM.')
    
    return build_validation_result(True, None, None)

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            'isValid': is_valid,
            'violatedSlot': violated_slot
        }
    
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def elicit_intent(session_attributes, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitIntent',
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

"""Dispatch"""

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingsIntent':
        return greet(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thanks(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return suggest(intent_request)
    
    raise Exception('Intent with name ' + intent_name + ' not supported')

"""Lambda Handler"""

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    return dispatch(event)