import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional
import re

@dataclass
class CourseDetails:
    semester: int
    course_name: str
    course_code: str
    course_type: str
    credits: str
    faculty: Optional[str]
    registration_date: Optional[str]
    attendance: Optional[str]
    section: Optional[str]
    marks: Dict[str, str]
    grade: Optional[str]
    result: str

class ERPClient:
    def __init__(self, base_url: str = "https://erp.iiita.ac.in"):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, credentials: Dict[str, str]):
        try:
            response = self.session.post(
                self.base_url,
                data=credentials,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            # If the login form is still present, login failed
            if 'name="pwd"' in response.text:
                return False, '{"message": "Invalid ERP credentials", "status": "fail"}'
            return True, '{"message": "Valid ERP credentials", "status": "success"}'
        except requests.RequestException as e:
            return False, f'{{"message": "Login failed: {e}", "status": "fail"}}'

    def get_all_courses(self, html_content: str) -> bool:
        soup = BeautifulSoup(html_content, 'html.parser')
        semester_sections = soup.find_all('fieldset')
        for section in semester_sections:
            legend = section.find('legend')
            if not legend or 'Semester' not in legend.text:
                continue
            table = section.find('table', {'class': 'interface2'})
            if not table:
                continue
            rows = table.find_all('tr')[1:]
            if rows:
                return True
        return False

    def get_semester_summary(self, html_content: str) -> Dict[str, Dict[str, str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        summaries = {}
        semester_sections = soup.find_all('fieldset')
        for section in semester_sections:
            legend = section.find('legend')
            if not legend or 'Semester' not in legend.text:
                continue
            sem_match = re.search(r'Semester \[ (\d+) \]', legend.text)
            if not sem_match:
                continue
            semester = sem_match.group(1)
            table = section.find('table', {'class': 'interface2'})
            if not table:
                continue
            summary_row = table.find_all('tr')[-1]
            if 'Summary' not in summary_row.text:
                continue
            cols = summary_row.find_all('th')
            summaries[semester] = {
                'credits': cols[4].text.strip() if len(cols) > 4 else 'N/A',
                'sgpa': cols[-3].text.strip() if len(cols) > 3 else 'N/A',
                'cgpa': cols[-1].text.strip() if len(cols) > 1 else 'N/A'
            }
        return summaries 