from app.core.ports.output.porta_campus_repository import ICampusRepository

class DeleteCampusUseCase:
    def __init__(self, repo: ICampusRepository):
        self.repo = repo

    def execute(self, campus_id: int) -> None:
        self.repo.delete(campus_id)
