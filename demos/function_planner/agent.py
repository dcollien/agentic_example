import json

from agent import Agent
from ai import request_ai_response
from demos.function_planner.structured_outputs import (
    ConsolidatedInformation,
    MenuDecision,
    NextAction,
    Questions,
    Venue,
)

agent = Agent()

""" And example agent for planning a function """

SYSTEM_PROMPT = "You are an AI agent planning a function."
REQUIRED_INFORMATION = ["date", "guests", "city", "venue", "weather", "menu"]


@agent.add_action
def start(state, input_data):
    # Starting state of the agent

    print("Agent Thoughts: Starting the function planning agent")

    # Initialize the state with each value as None
    for info in REQUIRED_INFORMATION:
        if info not in state:
            state[info] = None

    # Add another key to store the information gathered by asking questions
    state["information_gathered"] = []

    return "gather_information", None


@agent.add_action
def gather_information(state, input_data):
    """Identify the requirements for the function"""

    print("Agent Thoughts: Gathering information for the function")

    prompt = "Gather some information from the user to plan the event by asking a few brief questions, e.g. type of function."
    prompt += "\nDo not ask very specific questions about the exact venue or exact menu items, as these will be decided later."
    prompt += "\nThe weather forecast will be checked automatically later in the planning process."

    if input_data is not None:
        prompt += f"\n\nSpecifically ask about: {input_data}"

    prompt += "\n\nEvent details:\n"
    prompt += json.dumps(state, indent=2)
    prompt += "\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=Questions,
    )

    response_data = response.parsed

    questions_to_ask = response_data.questions

    return "ask_questions", questions_to_ask


@agent.add_action
def ask_questions(state, input_data):
    # This action doesn't use the AI model, it directly asks the user the questions

    print("Agent Thoughts: Asking the user some questions.\n")

    for question in input_data:
        answer = input(question + " > ")
        state["information_gathered"].append({question: answer})

    return "consolidate_information", None


@agent.add_action
def consolidate_information(state, input_data):
    """Consolidate the information gathered"""

    # This action takes all the information gathered and consolidates it into structured state data

    print("Agent Thoughts: Consolidating the information gathered")

    prompt = "Consolidate the information gathered from the user.\n"

    prompt += "\n\nEvent details:\n"
    prompt += json.dumps(state, indent=2)

    prompt += "\nReview the information gathered and identify any missing details that need to be filled or corrected."
    prompt += "\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=ConsolidatedInformation,
    )

    response_data = response.parsed

    response_dict = response_data.model_dump()

    print("Agent Thoughts: Consolidated Information", response_dict, "\n")

    for key, value in response_dict.items():
        if value is not None:
            state[key] = value

    return "choose_next_step", None


@agent.add_action
def choose_next_step(state, input_data):
    """Decide on the next planning step"""

    # This action is a decision point based on the current state of the function planning
    # The AI model is used to decide on the next step based on the current state

    print("Agent Thoughts: Choosing the next planning step")
    if input_data is not None:
        print("   Specific input data:", input_data)
    print()

    prompt = "Given the requirements for the function, choose one of the following actions to perform next:\n"
    prompt += "1. Gather more information (gather_information)\n"
    prompt += "2. Find out the weather forecast (get_weather), requires the date and city of the function.\n"
    prompt += "3. Decide on the venue (decide_venue), requires the date and weather\n"
    prompt += "4. Decide on the menu (decide_menu), requires the date and venue\n"
    prompt += "5. Send invitations (send_invitations)\n"

    prompt += "\n\nEvent details:\n"
    prompt += json.dumps(state, indent=2)
    prompt += "\n"

    prompt += "Use the 'next_action' key to specify one of: 'gather_information', 'get_weather', 'decide_venue', 'decide_menu', 'send_invitations'."
    prompt += "\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=NextAction,
    )

    response_data = response.parsed

    print("Agent Thoughts: Next Action", response_data.next_action, "\n")

    next_action = response_data.next_action

    return next_action, None


@agent.add_action
def get_weather(state, input_data):
    """Get the weather forecast for the date of the function"""

    # This action demonstrates calling an external API to get the weather forecast
    # Agents can interact with external services to gather information

    print("Agent Thoughts: Getting the weather forecast")

    import random

    if state["date"] is None or state["city"] is None:
        print("Agent Thoughts: Missing information to get the weather forecast")
        return "gather_information", "date, city"

    # TODO call an API to get the weather forecast for the date and city
    state["weather"] = random.choice(["sunny", "rainy", "cloudy", "snowy"])

    print("Agent Thoughts: Weather Forecast is", state["weather"], "\n")

    return "choose_next_step", None


@agent.add_action
def decide_venue(state, input_data):
    print("Agent Thoughts: Deciding on the venue for the function")

    """Decide on the venue for the function"""

    # TODO you can call an API to get a list of available venues based on the date and city
    # pass this information to the AI model to decide on the venue

    prompt = "Give a list of recommended venues (restaurants, event venues, bbq areas, other locations) for the function, for the user to choose from."
    prompt += "\n\nEvent details:\n"
    prompt += json.dumps(state, indent=2)
    prompt += "\n"

    prompt += "Respond with 'null' venues if there is not enough information to decide on the venue.\n"
    prompt += "Describe the missing information in 'missing_information'\n"
    prompt += "If there is enough information to decide on the venue, 'missing_information' should be null.\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=Venue,
    )

    response_data = response.parsed

    if response_data.missing_information:
        print(
            "Agent Thoughts: Missing information to decide the venue",
            response_data.missing_information,
            "\n",
        )

        return "gather_information", response_data.missing_information
    else:
        print("Agent Thoughts: Listing Recommended Venues")
        print("\n")

        for venue_index, venue in enumerate(response_data.venues):
            print(f"{venue_index + 1}. {venue}")

        print(f"{len(response_data.venues) + 1}. None of the above")

        venue_choice = int(input("Choose a venue (number)> "))

        if venue_choice <= len(response_data.venues):
            state["venue"] = response_data.venues[venue_choice - 1]
            return "choose_next_step", None
        else:
            state["venue"] = None
            return "gather_information", "how to choose a venue"


@agent.add_action
def decide_menu(state, input_data):
    print("Agent Thoughts: Deciding on the menu for the function")

    """Decide on the menu for the function"""

    prompt = "Give a list of recommended menus for the event. "
    prompt += "Each menu should have a couple of different options for appetizers, mains, and desserts. "
    prompt += "What type of food should be served at the function? Ensure to consider the preferences and dietary requirements of the guests."

    prompt += "\n\nEvent details:\n"
    prompt += json.dumps(state, indent=2)
    prompt += "\n"

    prompt += "Respond with 'null' menus if there is not enough information to decide on a menu.\n"
    prompt += "Describe the missing information in 'missing_information'\n"
    prompt += "If there is enough information to decide on a menu, 'missing_information' should be null.\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=MenuDecision,
    )

    response_data = response.parsed

    if response_data.missing_information:
        print(
            "Agent Thoughts: Missing information to decide the menu",
            response_data.missing_information,
            "\n",
        )
        return "gather_information", response_data.missing_information
    else:
        print("Agent Thoughts: Listing Menu Options\n")
        for menu_index, menu in enumerate(response_data.menus):
            print(f"{menu_index + 1}.\n{menu}\n\n")

        print(f"{len(response_data.menus) + 1}. None of the above")

        menu_choice = int(input("Choose a menu (number)> "))

        if menu_choice <= len(response_data.menus):
            state["menu"] = response_data.menus[menu_choice - 1].model_dump()
            return "choose_next_step", None
        else:
            state["menu"] = None
            return "gather_information", "how to choose a menu"


@agent.add_action
def send_invitations(state, input_data):
    print("Agent Thoughts: Sending invitations to the guests\n\n")

    """Send invitations to the guests"""

    prompt = "Write an invitation message to send to the guests for the function. Include the date, time, venue, and any other relevant details."
    prompt += "\n\nEvent details:\n"
    prompt += json.dumps(state, indent=2)

    # Note: The AI model is used to generate text here, not a structured output
    response = request_ai_response(user=prompt, system=SYSTEM_PROMPT)

    print(response.content)

    return "end", None
