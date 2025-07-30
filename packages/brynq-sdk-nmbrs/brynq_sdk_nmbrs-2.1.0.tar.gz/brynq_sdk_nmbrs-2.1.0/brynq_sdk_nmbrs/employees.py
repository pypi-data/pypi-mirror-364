import pandas as pd
import requests
from pydantic import BaseModel

from brynq_sdk_functions import Functions
from typing import Dict, Any, Optional

from .document import Payslip
from .address import Address
from .contract import Contract
from .costcenter import EmployeeCostcenter
from .department import EmployeeDepartment
from .employment import Employment
from .function import EmployeeFunction
from .hours import VariableHours, FixedHours
from .schedules import Schedule
from .salaries import Salaries
from .bank import Bank
from .wagecomponents import EmployeeVariableWageComponents, EmployeeFixedWageComponents
from .schemas.employees import (
    EmployeeGet, EmployeeCreate, EmployeeUpdate, EmployeeDelete,
    BasicInfo, BirthInfo, ContactInfo, PartnerInfo, Period, AdditionalEmployeeInfo,
    CreateEmployeePersonalInfo, UpdateEmployeePersonalInfo
)


class Employees:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.address = Address(nmbrs)
        self.functions = EmployeeFunction(nmbrs)
        self.contracts = Contract(nmbrs)
        self.departments = EmployeeDepartment(nmbrs)
        self.costcenter = EmployeeCostcenter(nmbrs)
        self.schedule = Schedule(nmbrs)
        self.employment = Employment(nmbrs)
        self.variable_hours = VariableHours(nmbrs)
        self.fixed_hours = FixedHours(nmbrs)
        self.salaries = Salaries(nmbrs)
        self.variable_wagecomponents = EmployeeVariableWageComponents(nmbrs)
        self.fixed_wagecomponents = EmployeeFixedWageComponents(nmbrs)
        self.banks = Bank(nmbrs)
        self.payslips = Payslip(nmbrs)

    def get(self,
            employee_type: str = None
            ) -> (pd.DataFrame, pd.DataFrame):
        employees = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            employees = pd.concat([employees, self._get(company, employee_type)])

        valid_employees, invalid_employees = Functions.validate_data(df=employees, schema=EmployeeGet, debug=True)

        return valid_employees, invalid_employees

    def _get(self,
            company_id: str,
            employee_type: str = None) -> pd.DataFrame:
        params = {} if employee_type is None else {'employeeType': employee_type}
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/personalinfo",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='info',
            meta=['employeeId']
        )
        df['companyId'] = company_id

        df['createdAt'] = pd.to_datetime(df['createdAt'])
        df = df.loc[df.groupby('employeeId')['createdAt'].idxmax()]
        df = df.reset_index(drop=True)

        return df

    def create(self, company_id: str, data: Dict[str, Any]):
        """
        Create a new employee using Pydantic validation.

        Args:
            company_id: The ID of the company
            data: Dictionary structured according to the EmployeeCreate schema with:
                 - PersonalInfo: containing basicInfo, birthInfo, contactInfo, etc.
                 - AdditionalEmployeeInfo: containing service date, etc.

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        def nest_dict(flat_dict, model):
            nested = {}
            for name, field in model.model_fields.items():
                key_in_input = name  # Original model field name as key in flat_dict
                alias = field.alias or name
                if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
                    nested[alias] = nest_dict(flat_dict, field.annotation)
                else:
                    if key_in_input in flat_dict:
                        nested[alias] = flat_dict[key_in_input]
            return nested

        nested_data = nest_dict(data, EmployeeCreate)
        employee_model = EmployeeCreate(**nested_data)

        if self.nmbrs.mock_mode:
            return employee_model

        # Convert validated model to dict for API payload
        payload = employee_model.model_dump(exclude_none=True, by_alias=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}companies/{company_id}/employees",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary structured according to the EmployeeUpdate schema with:
                 - employeeId: The ID of the employee to update
                 - personalInfo: containing any of basicInfo, birthInfo, contactInfo, etc.

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        employee_model = EmployeeUpdate(**data)

        if self.nmbrs.mock_mode:
            return employee_model

        # Convert validated model to dict for API payload
        payload = employee_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/personalInfo",
            json=payload,
            timeout=self.nmbrs.timeout
        )

        # Handle social security number update if present
        if 'socialSecurityNumber' in data:
            social_security_payload = {
                "socialSecurityNumber": data['socialSecurityNumber']
            }
            resp = self.nmbrs.session.put(
                url=f"{self.nmbrs.base_url}employees/{employee_id}/social_security_number",
                json=social_security_payload,
                timeout=self.nmbrs.timeout
            )

        return resp
