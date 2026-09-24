from pydantic import BaseModel


class ReportRead(BaseModel):
    id: int
    report_title: str
    incident_id: int | None = None
    generated_by_user_id: int | None = None
    export_format: str
    file_path: str | None = None
