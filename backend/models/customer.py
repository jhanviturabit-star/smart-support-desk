from pydantic import BaseModel, EmailStr
# from sqlalchemy import Column, Integer, String, Enum
# from sqlalchemy.orm import declarative_base

# Base = declarative_base()

class CreateCustomer(BaseModel):
    c_name : str
    c_email : EmailStr
    phone : str
    #c0d_at :

class CustomerRespone(CreateCustomer):
    c_id : int

# class CreateTicket(BaseModel):
#     t_id : int
#     t_title : str
#     t_description : str
#     priority : list["Low", "Medium", "High", "Critical"]