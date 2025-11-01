from app.core.ports.output.porta_campus_repository import ICampusRepository

class GetCampusByIdUseCase:
    def __init__(self, repo: ICampusRepository):
        self.repo = repo

    def execute(self, campus_id: int) -> dict:
        return self.repo.get_by_id(campus_id)