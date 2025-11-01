from app.core.ports.output.porta_campus_repository import ICampusRepository
from app.core.models.campus import Campus

class UpdateCampusUseCase:
    def __init__(self, repo: ICampusRepository):
        self.repo = repo

    def execute(self, campus_id: int, campus: Campus) -> None:
        self.repo.update(campus_id, campus)
