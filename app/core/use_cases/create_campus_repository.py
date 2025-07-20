from app.core.models.campus import Campus
from app.core.ports.output.porta_campus_repository import ICampusRepository

class CreateCampusUseCase:
    def __init__(self, repo: ICampusRepository):
        self.repo = repo

    def execute(self, campus: Campus) -> int:
        return self.repo.create(campus)