import os
import requests
import json
from datetime import datetime, date
from typing import Union, Literal, Optional, List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .employee import Employee
from .salary import Salary
from .contract import Contract
from .address import Address
from .position import Position
from .family import Family
from .absence import Absence
from .leave import Leave
from .service import Service
from .department import Department
from .bank_info import BankInfo
from .company import Company
from .insurance import Insurance
from .employee_insurance import EmployeeInsurance
from brynq_sdk_functions import Functions
import pandas as pd
import pandera as pa
import math
import numpy as np

class Sage100France:

    def __init__(self, subdomain: str = None, api_token: str = None, staging: str = 'prod', connection_string: str = None):
        self.subdomain = os.getenv("BRYNQ_SUBDOMAIN", subdomain)
        self.api_token = os.getenv("BRYNQ_API_TOKEN", api_token)
        self.connection_string = os.getenv("SAGE100_CONNECTION_STRING", connection_string)

        if any([self.subdomain is None, self.api_token is None, self.connection_string is None]):
            raise ValueError("Set the subdomain, api_token, connection_string either in your .env file or provide them as parameters")

        self.agent_url = 'https://agent.app.brynq.com/brynq-agent/'

        # Initialize file content buffer for import operations
        self.file_content_buffer = []

        # Initialize session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=0.5,  # wait 0.5s * (2 ** (retry - 1)) between retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(self._get_headers())

        self.employees = Employee(self)
        self.salary = Salary(self)
        self.contract = Contract(self)
        self.address = Address(self)
        self.position = Position(self)
        self.family = Family(self)
        self.absence = Absence(self)
        self.leave = Leave(self)
        self.service = Service(self)
        self.department = Department(self)
        self.bank_info = BankInfo(self)
        self.company = Company(self)
        self.insurance = Insurance(self)
        self.employee_insurance = EmployeeInsurance(self)

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Domain': self.subdomain,
            'connection-string': self.connection_string
        }

    def execute_query(self, queries: List[str]) -> Dict[str, Any]:
        """
        Execute one or multiple SQL queries against the Sage 100 France database

        Args:
            queries: List of SQL query strings to execute

        Returns:
            Dict containing query results or error messages
        """
        if not queries:
            raise ValueError("At least one query must be provided")

        endpoint = f"{self.agent_url}execute-query"

        payload = {
            "queries": queries
        }

        try:
            response = self.session.post(
                endpoint,
                headers=self._get_headers(),
                json=payload
            )

            response.raise_for_status()  # Raise exception for 4XX/5XX responses

            return response.json()
        except requests.exceptions.RequestException as e:
            # Log error and re-raise
            print(f"Error executing query: {str(e)}")
            raise

    def get(self, table_name: str, columns: Optional[List[str]] = None, where_clause: Optional[str] = None) -> Dict[str, Any]:
        """
        Simple SELECT query builder and executor for Sage 100 France tables

        Args:
            table_name: Name of the table to query
            columns: List of column names to select (None for all columns)
            where_clause: Optional WHERE clause (without the 'WHERE' keyword)

        Returns:
            Dict containing query results
        """
        # Build the query
        if columns and isinstance(columns, list) and len(columns) > 0:
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table_name}"
        else:
            query = f"SELECT * FROM {table_name}"

        # Add WHERE clause if provided
        if where_clause:
            query += f" WHERE {where_clause}"

        # Execute the query
        response = self.execute_query([query])
        if "message" in response:
            return response["message"]
        return response

    def _get_field_specs(self, schema):
        field_specs = {
            (col[1].original_name):col[1].metadata
            for name, col in schema.__fields__.items()
        }

        return field_specs

    def prepare_formatted_rows(self, df: pd.DataFrame, schema) -> List[str]:
        if df.empty:
            raise ValueError("Provided DataFrame is empty; nothing to convert.")

        field_specs = self._get_field_specs(schema)

        if not field_specs:
            raise ValueError("No columns with 'position' and 'length' metadata found in schema.")

        ordered = sorted(((c, s["position"] - 1, s["length"]) for c, s in field_specs.items()),
                         key=lambda x: x[1])

        total_length = max(pos + ln for _, pos, ln in ordered)

        formatted_rows = []
        for _, row in df.iterrows():
            row_chars = [" "] * total_length
            for col, pos, ln in ordered:
                val = row.get(col, "")
                formatted = "" if pd.isna(val) else self._format_value(val)
                row_chars[pos:pos + ln] = formatted.ljust(ln)[:ln]
            formatted_rows.append("".join(row_chars))

        return formatted_rows

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format individual values according to project rules."""
        # Handle NaN/NaT/None values first
        if value is None or pd.isna(value):
            return ""

        if isinstance(value, (datetime, date)):
            return value.strftime("%d/%m/%y")  # Changed from %Y to %y for 2-digit year
        if isinstance(value, float):
            # Four decimal places, comma as decimal separator
            return f"{value:.3f}".replace(".", ",")
        if isinstance(value, int):
            return str(value)
        if isinstance(value, str):
            # Convert date strings formatted with '-' to '/'
            if "-" in value and all(part.isdigit() for part in value.split("-")):
                return value.replace("-", "/")
            # Convert existing dd/mm/yyyy dates to dd/mm/yy
            if "/" in value and len(value.split("/")) == 3:
                day, month, year = value.split("/")
                if len(year) == 4:
                    year = year[-2:]  # Take last 2 digits
                return f"{day}/{month}/{year}"
            return value
        # Default fallback
        return str(value)

    def add_rows_to_buffer(self, rows: List[str]):
        """
        Add formatted rows to the file content buffer

        Args:
            rows: List of formatted row strings to add to buffer
        """
        self.file_content_buffer.extend(rows)

    def export_buffer_to_file(self, file_name: str):
        """
        Export all buffered rows to a file

        Args:
            file_name: Name of the output file
        """
        with open(file_name, 'w', encoding='utf-8') as file:
            for row in self.file_content_buffer:
                file.write(row + '\n')

    def clear_buffer(self):
        """
        Clear the file content buffer
        """
        self.file_content_buffer = []

    def get_buffer_content(self) -> List[str]:
        """
        Get current buffer content

        Returns:
            List of buffered row strings
        """
        return self.file_content_buffer.copy()
