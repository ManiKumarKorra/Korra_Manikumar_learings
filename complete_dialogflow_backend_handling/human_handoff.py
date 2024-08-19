from inputimeout import inputimeout, TimeoutOccurred

def handle_human_handoff(payload):
    customer_says = payload['queryResult']['queryText']

    print(customer_says)

    try:
        fulfillment_text = inputimeout(prompt="Enter your reply: ", timeout=3)
    except TimeoutOccurred:
        fulfillment_text = "Connected with operator but it's been more than 3 seconds, so returning a static reply."

    return fulfillment_text
