from pydantic import BaseModel
from typing import Literal

class CreateTicket(BaseModel):
    c_id : int
    t_title : str
    t_description : str
    priority : Literal['Low', 'Medium', 'High', 'Critical']
    t_status : Literal['Open', 'Close', 'In_progree', 'Resolved'] = 'Open'

# class DeleteTicket(CreateTicket):
