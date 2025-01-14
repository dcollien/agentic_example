from pydantic import BaseModel


class Questions(BaseModel):
    questions: list[str]


class ConsolidatedInformation(BaseModel):
    date: str
    guests: int
    city: str


class NextAction(BaseModel):
    next_action: str


class Menu(BaseModel):
    appetizer: list[str] = None
    main_course: list[str] = None
    dessert: list[str] = None

    def __str__(self):
        menu_str = ""
        if self.appetizer:
            menu_str += f"Appetizer: {', '.join(self.appetizer)}\n"
        if self.main_course:
            menu_str += f"Main Course: {', '.join(self.main_course)}\n"
        if self.dessert:
            menu_str += f"Dessert: {', '.join(self.dessert)}\n"
        return menu_str


class MenuDecision(BaseModel):
    menus: list[Menu] = None
    missing_information: str = None


class Venue(BaseModel):
    venues: list[str] = None
    missing_information: str = None
