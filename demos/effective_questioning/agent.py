import re

from agent import Agent
from ai import request_ai_response
from demos.effective_questioning.structured_outputs import NextAction, TypeOfQuestioning

agent = Agent()

TAG_RE = re.compile("<.*?>")


def remove_tags(raw):
    cleantext = re.sub(TAG_RE, "", raw)
    return cleantext


SYSTEM_PROMPT = (
    "You are an AI agent helping a user to think more effectively by asking questions."
)


def state_summary(state):
    prompt = ""
    phase = state["phase"]
    if phase > 0:
        prompt += "A summary of each phase of the conversation so far:\n\n"
        for i, summary in enumerate(state["summary"]):
            prompt += '<phase number="' + str(i + 1) + '">\n' + summary + "\n</phase>\n"

    return prompt


def phase_description(phase):
    phase1_tense = "will use" if phase < 1 else "have used"
    phase2_tense = "will mostly use" if phase < 2 else "have mostly used"
    phase3_tense = "will mostly use" if phase < 3 else "have mostly used"
    phase4_tense = "will mostly use" if phase < 4 else "have mostly used"

    prompt = "The conversation is divided into several phases. Each phase has a specific goal and type of questioning to use.\n"
    prompt += f"In the first phase, you {phase1_tense} open questions and probing questions to gather information about the user's problem.\n"
    prompt += f"In the second phase, you {phase2_tense} hypothetical questions and reflective questions to encourage the user to think about their problem from different perspectives.\n"
    prompt += f"In the third phase, you {phase3_tense} leading questions to guide the user towards a solution.\n"
    prompt += f"In the fourth phase, you {phase4_tense} closing questions to bring agreement, commitment, and decide on actions.\n"
    prompt += f"Each phase should include no more than 8 questions.\n"

    return prompt


@agent.add_action
def start(state, _input):
    print("Agent Thoughts: Let's start")

    state["history"] = []
    state["summary"] = []
    state["phase"] = 0

    return "decide_questioning", None


@agent.add_action
def decide_questioning(state, _input):
    print("Agent Thoughts: Deciding on the type of questioning to use")

    phase = state["phase"]

    prompt = "Based on the information collected about the user's problem, decide on the type of questioning to use.\n"
    prompt += phase_description(phase)
    prompt += "If the user is dissatisfied, you will use deflective questions to improve the mood of the conversation and keep the conversation on track.\n"
    prompt += "\n"

    prompt += "As it is"
    if phase == 0:
        prompt += " the beginning of the conversation, "
    else:
        prompt += " phase " + str(phase) + ", "

    prompt += "use one the following types of questioning:\n"
    if phase <= 1:
        prompt += "- (open) Open questions: Gather information and encourage the user to talk about their problem.\n"
        prompt += "- (probing) Probing questions: Clarify and explore the user's problem, gaining more detail.\n"
    elif phase == 2:
        prompt += "- (hypothetical) Hypothetical questions: Encourage the user to think about alternative scenarios.\n"
        prompt += "- (reflective) Reflective questions: Encourage the user to think about their problem from a different perspective.\n"
    elif phase == 3:
        prompt += "- (reflective) Reflective questions: Encourage the user to think about their problem from a different perspective.\n"
        prompt += "- (leading) Leading questions: Guide the user towards a particular solution.\n"
    elif phase == 4:
        prompt += "- (leading) Leading questions: Guide the user towards a particular solution.\n"
        prompt += "- (closing) Closing questions: Bring agreement, commitment, and decide on actions.\n"

    prompt += "- (deflective) Deflective questions: Improve the mood of the conversation and alleviate dissatisfaction by keeping conversation on track.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=TypeOfQuestioning,
    )

    response_data = response.parsed

    type_of_questioning = response_data.type

    return f"ask_{type_of_questioning}_question", None


@agent.add_action
def ask_open_question(state, _input):
    print("Agent Thoughts: Asking an open question")

    prompt = "Ask an open question to gather information and encourage the user to talk about their problem.\n"
    prompt += "For example, ask 'What is the main issue you are facing?', 'Can you describe the problem you are experiencing?' or 'What are the concerns that you have?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def ask_probing_question(state, _input):
    print("Agent Thoughts: Asking a probing question")

    prompt = "Ask a probing question to clarify and explore the user's problem, gaining more detail.\n"
    prompt += "For example, ask 'Can you provide more information about that?', 'What happened next?', 'Why does that exactly matter?' or 'Can you explain that in more detail?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def ask_hypothetical_question(state, _input):
    print("Agent Thoughts: Asking a hypothetical question")

    prompt = "Ask a hypothetical question to encourage the user to think about alternative scenarios.\n"
    prompt += "For example, ask 'What would happen if...?', 'How would you handle...?', 'If there was a way to do that, what impact would it have?' or 'What could be the outcome if...?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def ask_reflective_question(state, _input):
    print("Agent Thoughts: Asking a reflective question")

    prompt = "Ask a reflective question to encourage the user to think about their problem from a different perspective, or to challenge their current thinking.\n"
    prompt += "For example, ask 'How do you feel/think about that?', 'What is the priority of...?', 'What would someone else say about that?' or 'What could be the reasons behind...?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def ask_leading_question(state, _input):
    print("Agent Thoughts: Asking a leading question")

    prompt = "Ask a leading question to guide the user towards a particular solution.\n"
    prompt += "For example, ask 'Have you considered...?', 'What do you think about...?', 'Would you agree that...?' or 'Could you imagine...?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def ask_closing_question(state, _input):
    print("Agent Thoughts: Asking a closing question")

    prompt = "Ask a closing question to bring agreement, commitment, and decide on actions.\n"
    prompt += "For example, ask 'What do you think we should do next?', 'How do you feel about the solution?', 'Can we agree on...?' or 'What are the next steps?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def ask_deflective_question(state, _input):
    print("Agent Thoughts: Asking a deflective question")

    prompt = "Ask a deflective question to improve the mood of the conversation and alleviate dissatisfaction by keeping the conversation on track.\n"
    prompt += "For example, ask 'How can we make this conversation more helpful?', 'What would you like to focus on?', 'What do you think we should do next?' or 'What are your thoughts on...?'\n"
    prompt += "Respond only with the question you would like to ask.\n"

    prompt += "\n" + state_summary(state)

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
    )

    question = response.content.strip()

    return "receive_answer", question


@agent.add_action
def receive_answer(state, question):
    print("Agent Thoughts: Receive input from the user")

    print()
    print(question)
    answer = input("> ")
    print()

    return "consolidate_information", (question, answer)


@agent.add_action
def consolidate_information(state, question_answer):
    print(
        "Agent Thoughts: Consolidating the information gathered (phase "
        + str(state["phase"])
        + ")"
    )

    if state["phase"] == 0:
        state["phase"] = 1

    state["history"].append(question_answer)

    phase = state["phase"]

    prompt = "Consolidate the information gathered from the user's response.\n"
    prompt += "Consider the following conversation history:\n"
    prompt += "<history>\n"
    for i, (question, answer) in enumerate(state["history"]):
        prompt += "<question>\n"
        prompt += "Question " + str(i + 1) + ":\n"
        prompt += question + "\n"
        prompt += "Answer:\n"
        prompt += answer + "\n"
        prompt += "</question>\n"
    prompt += "</history>\n"

    prompt += phase_description(phase)
    prompt += "\nIt is currently phase " + str(phase) + " of the conversation.\n"
    prompt += state_summary(state)
    prompt += "This summary does not include the latest question and answer.\n"

    prompt += "\nYou are to update the summary for phase " + str(phase) + ".\n"
    prompt += "Ensure the summary captures the key points of the conversation so far.\n"

    response = request_ai_response(
        user=prompt,
        system="You are an AI agent consolidating information gathered about a conversation. Only respond with the replacement summary for the current phase.\n",
    )

    summary = remove_tags(response.content).strip()

    print("Agent Thoughts: Summary for phase " + str(phase) + ":")
    print(summary)
    print()

    if len(state["summary"]) < phase:
        state["summary"].append(summary)
    else:
        state["summary"][phase - 1] = summary

    return "decide_next_action", None


@agent.add_action
def decide_next_action(state, _input):
    print("Agent Thoughts: Deciding on the next action")
    phase = state["phase"]

    prompt = "Based on the information collected and the type of questioning used, decide on the next action to take.\n"
    prompt += phase_description(phase)
    prompt += "\nIt is currently phase " + str(phase) + ".\n"
    prompt += state_summary(state)
    prompt += (
        str(len(state["history"]))
        + " total questions have been asked in the conversation so far.\n"
    )

    prompt += "\n"
    prompt += "Actions you can take:\n"
    prompt += "- (ask_question) Ask another question to gather more information.\n"
    prompt += "- (move_on) Move to the next phase of questioning.\n"
    prompt += "- (end_conversation) End the conversation.\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=NextAction,
    )

    next_action = response.parsed.next_action

    if next_action == "ask_question":
        return "decide_questioning", None
    elif next_action == "move_on":
        state["phase"] += 1
        return "decide_questioning", None
    elif next_action == "end_conversation":
        return "end_conversation", None


@agent.add_action
def end_conversation(state, _input):
    print("Agent Thoughts: Ending the conversation")

    print()
    print("The conversation has ended.")
    print("The following is a summary of the conversation:")
    print()
    print(state_summary(state))
    print()

    return "end", None
