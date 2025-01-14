from demos.function_planner.agent import agent as planner_agent
from demos.simple_rag.agent import agent as book_agent

print("Choose a demo to run:")

print("1. A Function Planner Agent")
print("2. Ask a Question about a Book (Alice in Wonderland)")

demo = input("Enter the number of the demo you would like to run: ")

if demo == "1":
    planner_agent.run()
elif demo == "2":
    book_agent.run()
else:
    print("Invalid choice. Please enter 1 or 2.")
