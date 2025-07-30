# **SS12000 Python Client Library**

This is a Python client library designed to simplify interaction with the SS12000 API, a standard for information exchange between school administration processes based on OpenAPI 3. The library handles HTTP requests and Bearer Token authentication, providing a structured approach to interact with **all** the API's defined endpoints.

You can download your own personal copy of the SS12000 standard for free from here: [sis.se](https://www.sis.se/standarder/kpenstandard/forkopta-standarder/informationshantering-inom-utbildningssektorn/).

### **Important**

The SS12000 does not require the server to support all of the endpoints. You need to actually look at the server documentation to see which endpoints that are actually available with each service. Adding some sort of discovery service is beyond the scope of this small library in my humble opinion.

All dates are in the RFC 3339 format, we're not cavemen here. 

## **Table of Contents**

- [**SS12000 Python Client Library**](#ss12000-python-client-library)
    - [**Important**](#important)
  - [**Table of Contents**](#table-of-contents)
  - [**Installation**](#installation)
  - [**Usage**](#usage)
    - [**Initializing the Client**](#initializing-the-client)
    - [**Fetching Organizations**](#fetching-organizations)
    - [**Fetching Persons**](#fetching-persons)
    - [**Fetch ...**](#fetch-)
    - [**Webhooks (Subscriptions)**](#webhooks-subscriptions)
  - [**API Reference**](#api-reference)
  - [**Webhook Receiver (FastAPI Example)**](#webhook-receiver-fastapi-example)
  - [**Contributing**](#contributing)
  - [**License**](#license)

## **Installation**

1. **Save the Client:** Save the code from ss12000_client.py in your project directory.  
2. **Install Dependencies:** This library uses requests for making HTTP calls. If you plan to use the webhook receiver example, you will also need fastapi and uvicorn.  
```
pip install requests fastapi uvicorn
```

## **Usage**

### **Initializing the Client**

To start using the client, import it and create an instance with your API base URL and your JWT Bearer Token.  
```
from ss12000client import SS12000Client

base_url = "https://some.server.se/v2.0" # Replace with your test server URL  
auth_token = "YOUR_JWT_TOKEN_HERE" # Replace with your actual JWT token

client = SS12000Client(base_url, auth_token)
```
### **Fetching Organizations**

You can retrieve a list of organizations or a specific organization by its ID.  
```
async def get_organization_data():  
    try:  
        print("Fetching organizations...")  
        organizations = client.get_organisations(limit=2)  
        print("Fetched organizations:", json.dumps(organizations, indent=2))

        if organizations and organizations.get('data'):  
            first_org_id = organizations['data'][0]['id']  
            print(f"\nFetching organization with ID: {first_org_id}...")  
            org_by_id = client.get_organisation_by_id(first_org_id, expand_reference_names=True)  
            print("Fetched organization by ID:", json.dumps(org_by_id, indent=2))  
    except Exception as e:  
        print(f"Error fetching organization data: {e}")
```

### **Fetching Persons**

Similarly, you can fetch persons and expand related data such as duties.  
```
async def get_person_data():  
    try:  
        print("\nFetching persons...")  
        persons = client.get_persons(limit=2, expand=['duties'])  
        print("Fetched persons:", json.dumps(persons, indent=2))

        if persons and persons.get('data'):  
            first_person_id = persons['data'][0]['id']  
            print(f"\nFetching person with ID: {first_person_id}...")  
            person_by_id = client.get_person_by_id(first_person_id, expand=['duties', 'responsibleFor'], expand_reference_names=True)  
            print("Fetched person by ID:", json.dumps(person_by_id, indent=2))  
    except Exception as e:  
        print(f"Error fetching person data: {e}")
```
### **Fetch ...**

Check the API reference below to see all available nodes. 

### **Webhooks (Subscriptions)**

The client provides methods to manage subscriptions (webhooks).  
```
async def manage_subscriptions():  
    try:  
        print("\nFetching subscriptions...")  
        subscriptions = client.get_subscriptions()  
        print("Fetched subscriptions:", json.dumps(subscriptions, indent=2))

        # Example: Create a subscription (requires a publicly accessible webhook URL)  
        # print("\nCreating a subscription...")  
        # new_subscription = client.create_subscription(  
        #     name="My Python Test Subscription",  
        #     target="http://your-public-webhook-url.com/ss12000-webhook", # Replace with your public URL  
        #     resource_types=["Person", "Activity"]  
        # )  
        # print("Created subscription:", json.dumps(new_subscription, indent=2))

        # Example: Delete a subscription  
        # if subscriptions and subscriptions.get('data'):  
        #     sub_to_delete_id = subscriptions['data'][0]['id']  
        #     print(f"\nDeleting subscription with ID: {sub_to_delete_id}...")  
        #     client.delete_subscription(sub_to_delete_id)  
        #     print("Subscription deleted successfully.")

    except Exception as e:  
        print(f"Error managing subscriptions: {e}")
```

## **API Reference**

The SS12000Client class is designed to expose methods for all SS12000 API endpoints. Here is a list of the primary resource paths defined in the OpenAPI specification, along with their corresponding client methods:

* /organisations  
  * get\_organisations(\*\*params): Get a list of organizations.  
  * lookup\_organisations(ids, school\_unit\_codes, organisation\_codes, expand\_reference\_names): Get multiple organizations.  
  * get\_organisation\_by\_id(org\_id, expand\_reference\_names): Get a specific organization.  
* /persons  
  * get\_persons(\*\*params): Get a list of persons.  
  * lookup\_persons(ids, civic\_nos, expand, expand\_reference\_names): Get multiple persons.  
  * get\_person\_by\_id(person\_id, expand, expand\_reference\_names): Get a specific person.  
* /placements  
  * get\_placements(\*\*params): Get a list of placements.  
  * lookup\_placements(ids, expand, expand\_reference\_names): Get multiple placements.  
  * get\_placement\_by\_id(placement\_id, expand, expand\_reference\_names): Get a specific placement.  
* /duties  
  * get\_duties(\*\*params): Get a list of duties.  
  * lookup\_duties(ids, expand, expand\_reference\_names): Get multiple duties.  
  * get\_duty\_by\_id(duty\_id, expand, expand\_reference\_names): Get a specific duty.  
* /groups  
  * get\_groups(\*\*params): Get a list of groups.  
  * lookup\_groups(ids, expand, expand\_reference\_names): Get multiple groups.  
  * get\_group\_by\_id(group\_id, expand, expand\_reference\_names): Get a specific group.  
* /programmes  
  * get\_programmes(\*\*params): Get a list of programmes.  
  * lookup\_programmes(ids, expand, expand\_reference\_names): Get multiple programmes.  
  * get\_programme\_by\_id(programme\_id, expand, expand\_reference\_names): Get a specific programme.  
* /studyplans  
  * get\_study\_plans(\*\*params): Get a list of study plans.  
  * lookup\_study\_plans(ids, expand, expand\_reference\_names): Get multiple study plans.  
  * get\_study\_plan\_by\_id(study\_plan\_id, expand, expand\_reference\_names): Get a specific study plan.  
* /syllabuses  
  * get\_syllabuses(\*\*params): Get a list of syllabuses.  
  * lookup\_syllabuses(ids, expand\_reference\_names): Get multiple syllabuses.  
  * get\_syllabus\_by\_id(syllabus\_id, expand\_reference\_names): Get a specific syllabus.  
* /schoolUnitOfferings  
  * get\_school\_unit\_offerings(\*\*params): Get a list of school unit offerings.  
  * lookup\_school\_unit\_offerings(ids, expand, expand\_reference\_names): Get multiple school unit offerings.  
  * get\_school\_unit\_offering\_by\_id(offering\_id, expand, expand\_reference\_names): Get a specific school unit offering.  
* /activities  
  * get\_activities(\*\*params): Get a list of activities.  
  * lookup\_activities(ids, expand, expand\_reference\_names): Get multiple activities.  
  * get\_activity\_by\_id(activity\_id, expand, expand\_reference\_names): Get a specific activity.  
* /calendarEvents  
  * get\_calendar\_events(\*\*params): Get a list of calendar events.  
  * lookup\_calendar\_events(ids, expand, expand\_reference\_names): Get multiple calendar events.  
  * get\_calendar\_event\_by\_id(event\_id, expand, expand\_reference\_names): Get a specific calendar event.  
* /attendances  
  * get\_attendances(\*\*params): Get a list of attendances.  
  * lookup\_attendances(ids, expand, expand\_reference\_names): Get multiple attendances.  
  * get\_attendance\_by\_id(attendance\_id, expand, expand\_reference\_names): Get a specific attendance.  
  * delete\_attendance(attendance\_id): Delete an attendance.  
* /attendanceEvents  
  * get\_attendance\_events(\*\*params): Get a list of attendance events.  
  * lookup\_attendance\_events(ids, expand, expand\_reference\_names): Get multiple attendance events.  
  * get\_attendance\_event\_by\_id(event\_id, expand, expand\_reference\_names): Get a specific attendance event.  
* /attendanceSchedules  
  * get\_attendance\_schedules(\*\*params): Get a list of attendance schedules.  
  * lookup\_attendance\_schedules(ids, expand, expand\_reference\_names): Get multiple attendance schedules.  
  * get\_attendance\_schedule\_by\_id(schedule\_id, expand, expand\_reference\_names): Get a specific attendance schedule.  
* /grades  
  * get\_grades(\*\*params): Get a list of grades.  
  * lookup\_grades(ids, expand, expand\_reference\_names): Get multiple grades.  
  * get\_grade\_by\_id(grade\_id, expand, expand\_reference\_names): Get a specific grade.  
* /aggregatedAttendance  
  * get\_aggregated\_attendances(\*\*params): Get a list of aggregated attendances.  
  * lookup\_aggregated\_attendances(ids, expand, expand\_reference\_names): Get multiple aggregated attendances.  
  * get\_aggregated\_attendance\_by\_id(attendance\_id, expand, expand\_reference\_names): Get a specific aggregated attendance.  
* /resources  
  * get\_resources(\*\*params): Get a list of resources.  
  * lookup\_resources(ids, expand\_reference\_names): Get multiple resources.  
  * get\_resource\_by\_id(resource\_id, expand\_reference\_names): Get a specific resource.  
* /rooms  
  * get\_rooms(\*\*params): Get a list of rooms.  
  * lookup\_rooms(ids, expand\_reference\_names): Get multiple rooms.  
  * get\_room\_by\_id(room\_id, expand\_reference\_names): Get a specific room.  
* /subscriptions  
  * get\_subscriptions(\*\*params): Get a list of webhooks subscriptions.  
  * create\_subscription(name, target, resource\_types): Create a new webhooks subscription.  
  * delete\_subscription(subscription\_id): Delete a webhooks subscription.  
  * get\_subscription\_by\_id(subscription\_id): Get a specific webhooks subscription.  
  * update\_subscription(subscription\_id, expires): Update a webhooks subscription (e.g., expiry date).  
* /deletedEntities  
  * get\_deleted\_entities(entities, meta\_modified\_after): Get a list of deleted entities.  
* /log  
  * get\_log(\*\*params): Get a list of log entries.  
* /statistics  
  * get\_statistics(\*\*params): Get a list of statistics.

Each method accepts parameters corresponding to the API's query parameters and request bodies, as defined in the OpenAPI specification. Detailed information on available parameters can be found in the docstrings within ss12000_client.py.

The .yaml file can be downloaded from the SS12000 site over at [sis.se](https://www.sis.se/standardutveckling/tksidor/tk400499/sistk450/ss-12000/). 

## **Webhook Receiver (FastAPI Example)**

A separate FastAPI server can be used to receive notifications from the SS12000 API.This is just an example and is not part of the client library. It just shows how you could implement a receiver server for the webhooks. The code below is not production ready code, it's just a thought experiment that will point you in a direction toward a simple solution. 
```
Save this in a separate file, e.g., 'webhook_server.py'  
from fastapi import FastAPI, Request, HTTPException  
import uvicorn  
import json

webhook_app = FastAPI()

@webhook_app.post("/ss12000-webhook")  
async def ss12000_webhook(request: Request):  
     """  
     Webhook endpoint for SS12000 notifications.  
     """  
     print("Received a webhook from SS12000!")  
     print("Headers:", request.headers)

     try:  
         body = await request.json()  
         print("Body:", json.dumps(body, indent=2))

         # Implement your logic to handle the webhook message here.  
         # E.g., save the information to a database, trigger an update, etc.

         if body and body.get('modifiedEntites'):  
             for resource_type in body['modifiedEntites']:  
                 print(f"Changes for resource type: {resource_type}")  
                 # You can call the SS12000Client here to fetch updated information  
                 # depending on the resource type.  
                 # Example: if resource_type == 'Person': client.get_persons(...)  
         if body and body.get('deletedEntities'):  
             print("There are deleted entities to fetch from /deletedEntities.")  
             # Call client.get_deleted_entities(...) to fetch the deleted IDs.

         return {"message": "Webhook received successfully\!"}  
     except json.JSONDecodeError:  
         raise HTTPException(status_code=400, detail="Invalid JSON body")  
     except Exception as e:  
         print(f"Error processing webhook: {e}")  
         raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# To run the FastAPI webhook server:  
# Save the above code as e.g., 'webhook_server.py'  
# Then run from your terminal: 'uvicorn webhook_server:webhook_app --host 0.0.0.0 --port 3001'
```
To run the FastAPI webhook server, save the code above in a file (e.g., webhook_server.py) and execute it using:

```uvicorn webhook_server:webhook_app --host 0.0.0.0 --port 3001``` 

Remember that your webhook URL must be publicly accessible for the SS12000 API to send notifications to it.

## **Contributing**

Contributions are welcome! If you want to add, improve, optimize or just change things just send in a pull request and I will have a look. Found a bug and don't know how to fix it? Create an issue!

## **License**

This project is licensed under the MIT Licence.