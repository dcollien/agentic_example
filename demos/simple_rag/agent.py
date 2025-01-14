import re
from agent import Agent
from ai import request_ai_response
from demos.simple_rag.search import digest_book, search
from demos.simple_rag.structured_outputs import Excerpts

# Example RAG using BM25 search and a simple state machine

agent = Agent()

SYSTEM_PROMPT = (
    "You are an AI agent performing tasks relating to the book Alice in Wonderland."
)


@agent.add_action
def start(state, input):
    print("Agent Thoughts: Ingesting Alice in Wonderland")

    search_engine, chapters, mapping = digest_book()

    state["search_engine"] = search_engine
    state["chapters"] = chapters
    state["mapping"] = mapping

    return "ask_question", None


@agent.add_action
def ask_question(state, _inputs):
    print("Agent Thoughts: The user needs to ask a question")

    print("Ask a question about Alice in Wonderland:\n")
    print("e.g. - ask for quotes, summaries, or questions about characters")

    question = input("Your question: ")

    return "fabricate_excerpts", question


@agent.add_action
def fabricate_excerpts(state, question):
    print(
        "Agent Thoughts: The user asked a question, I'm going to imagine what some relevant excerpts might look like"
    )

    prompt = "Consider the following question about the book Alice in Wonderland.\n"
    prompt += "Question:\n"
    prompt += question
    prompt += "\n\n"
    prompt += "Come up with all excerpts that may exist in the text that could be relevant to this question. If you're not sure, just make something up."
    prompt += "\n"

    response = request_ai_response(
        user=prompt,
        system=SYSTEM_PROMPT,
        response_format=Excerpts,
    )

    excerpts = "\n".join(response.parsed.excerpts)

    print("Agent Thoughts: Generated excerpts:")
    print(excerpts)
    print()

    return "search_text", (excerpts, question)


@agent.add_action
def search_text(state, query_question):
    query, question = query_question

    print(f"Agent Thoughts: Searching for relevant information in the text")

    mapping = state["mapping"]
    search_engine = state["search_engine"]
    chapters = state["chapters"]

    top_n = search(search_engine, query)

    print("Agent Thoughts: Found relevant information in the text")
    for index, score in top_n:
        chapter_index, paragraph_index = mapping[index]
        print(
            f"                - Chapter {chapter_index + 1}, Paragraph {paragraph_index + 1}: {score:.2f}"
        )

    excerpts = {}
    for index, score in top_n:
        chapter_index, paragraph_index = mapping[index]

        paragraph = chapters[chapter_index][paragraph_index]
        excerpts[f"chapter-{chapter_index+1}-p-{paragraph_index}"] = paragraph

    # Note: the agent could also evaluate the results and then
    # decide to search for more information here before answering the question

    return "answer_question", (question, excerpts)


@agent.add_action
def answer_question(state, question_context):
    print("Agent Thoughts: Generating an answer to the user's question")

    question, excerpts = question_context

    excerpts_formatted = ""
    for key, value in excerpts.items():
        excerpts_formatted += f'<excerpt location="#{key}">\n{value}\n</excerpt>\n\n'

    prompt = "Answer the following question about the book Alice in Wonderland based on the context provided.\n"
    prompt += "Your answer should include references to, or quotations from the given excerpts where relevant. "
    prompt += "You must reference excerpts in your answer by linking to the location of the excerpt using Markdown links using the format: [Text](#chapter-1-p-2)\n"
    prompt += "Note: #chapter-1-p-2 is an example, referring to the location attribute of the respective excerpt.\n"

    prompt += "\n"
    prompt += "Question:\n"
    prompt += question

    prompt += "\n\n"
    prompt += "Context:\n"
    prompt += excerpts_formatted

    response = request_ai_response(user=prompt, system=SYSTEM_PROMPT)

    answer = response.content

    print()
    print("-" * 50)
    print(answer)
    print("-" * 50)
    print("Excerpts:")

    references_regex = r"\(#([\w-]+)\)"
    references = re.findall(references_regex, answer)

    for reference in references:
        print("-" * 50)
        print(f"{reference}:")
        print("" * 50)
        print(excerpts[reference.strip("#")])
        print("" * 50)
        print("-" * 50)
        print()
    print()

    return "ask_question", None
