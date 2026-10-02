from src.base.base_repository import BaseRepository
from src.core.exceptions import RepositoryException


class WorkflowErrorRepository(BaseRepository):
    """
    Repository responsible for storing
    workflow execution errors.

    Used for debugging and monitoring.
    """

    def __init__(self):

        super().__init__(
            repository_name="Workflow Error Repository",
            table_name="workflow_error_logs"
        )

    # -------------------------------------------------
    # Logging
    # -------------------------------------------------

    def log_error(
        self,
        data
    ):
        """
        Store a workflow error.

        NOTE: intentionally does not re-raise a RepositoryException,
        since this method is itself the error-logging path — if it
        fails, callers should not crash while trying to log a crash.
        """
        try:
            return self.provider.execute(
                operation="insert",
                table=self.table_name,
                data=data
            )
        except Exception as error:
            from src.core.logging import logger
            logger.error(f"Failed to log workflow error to DB: {error}")
            return None

    # -------------------------------------------------
    # Read
    # -------------------------------------------------

    def find_all(self):
        """
        Retrieve all workflow errors.
        """
        try:
            return self.provider.execute(
                operation="select",
                table=self.table_name
            )
        except Exception as error:
            raise RepositoryException(
                f"Failed to fetch workflow errors: {error}"
            )

    def find_by_execution_id(
        self,
        execution_id
    ):
        """
        Retrieve errors for a
        workflow execution.
        """
        try:
            return self.provider.execute(
                operation="select",
                table=self.table_name,
                filters={
                    "execution_id": execution_id
                }
            )
        except Exception as error:
            raise RepositoryException(
                f"Failed to fetch workflow errors for execution '{execution_id}': {error}"
            )