from aiogram.fsm.state import StatesGroup, State


class UploadStates(StatesGroup):
    waiting_for_video = State()
    waiting_for_act = State()
