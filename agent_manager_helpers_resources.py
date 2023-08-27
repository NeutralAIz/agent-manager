import os
import boto3
from botocore.exceptions import NoCredentialsError

from superagi.config.config import get_config
from superagi.models.agent import Agent
from superagi.models.resource import Resource
from superagi.worker import summarize_resource
from superagi.types.storage_types import StorageType
from superagi.helper.resource_helper import ResourceHelper
from superagi.lib.logger import logger

class ResourceManager:
    """
    Manager handling the resources associated with an agent. This includes uploading, downloading
    and retrieving all resources.

    Args:
        agent_id (int): ID of the agent.
        db_session (Session): The session to make changes to the database.
    """

    s3 = boto3.client(
        's3',
        aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
    )

    def __init__(self, agent_id, db_session):
        self.agent_id = agent_id
        self.db_session = db_session
        self.agent = db_session.query(Agent).filter(Agent.id == agent_id).first()

    @staticmethod
    def get_formatted_agent_level_path(agent, path, agent_execution_id=None):
        """
        Formats the path with the agent ID and agent execution ID.

        Args:
            agent (Agent): The agent instance.
            path (str): The path to be formatted.
            agent_execution_id (int, optional): The ID of the agent execution.

        Returns:
            str: Formatted path.
        """
        formatted_path = path.replace("{agent_id}", str(agent.id))
        if agent_execution_id is not None:
            formatted_path = formatted_path.replace("{agent_execution_id}", str(agent_execution_id))
        return formatted_path

    def upload(self, file, name, size, type, agent_execution_id=None):
        """
        Uploads a file as a resource for an agent.

        Args:
            file (File): The file to be uploaded.
            name (str): The name of the file.
            size (int): The size of the file.
            type (str): The type of the file.
            agent_execution_id (int, optional): The ID of the agent execution.

        Returns:
            Resource: The uploaded resource.

        Raises:
            ValueError: If the agent does not exist or file type is not supported.
        """

        if self.agent is None:
            raise ValueError("Agent does not exist.")

        # accepted_file_types is a tuple because endswith() expects a tuple
        accepted_file_types = (".pdf", ".docx", ".pptx", ".csv", ".txt", ".epub")
        if not name.endswith(accepted_file_types):
            raise ValueError("File type not supported!")

        storage_type = StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value))
        save_directory = ResourceHelper.get_root_input_dir()
        save_directory = ResourceHelper.get_formatted_agent_level_path(agent=self.agent,
                                                                       path=save_directory,
                                                                       agent_execution_id=agent_execution_id)
        file_path = os.path.join(save_directory, file.filename)
        if storage_type == StorageType.FILE:
            with open(file_path, "wb") as f:
                contents = file.read()
                f.write(contents)
        elif storage_type == StorageType.S3:
            bucket_name = get_config("BUCKET_NAME")
            file_path = 'resources' + file_path
            try:
                s3.upload_fileobj(file, bucket_name, file_path)
                logger.info("File uploaded successfully!")
            except NoCredentialsError:
                raise ValueError("AWS credentials not found. Check your configuration.")

        resource = Resource(name=name, path=file_path, storage_type=storage_type.value, size=size, type=type, channel="INPUT",
                            agent_id=self.agent.id, agent_execution_id=agent_execution_id)
        self.db_session.add(resource)
        self.db_session.commit()
        self.db_session.flush()

        summarize_resource.delay(self.agent_id, resource.id)
        logger.info(resource)

    def download(self, resource_id):
        """
        Downloads a particular resource by resource_id.

        Args:
            resource_id (int): The ID of the resource that is to be downloaded.

        Returns:
            File: The downloaded resource.

        Raises:
            ValueError: If the resource does not exist or if the file does not exist.
        """

        resource = self.db_session.query(Resource).filter(Resource.id == resource_id).first()
        download_file_path = resource.path
        file_name = resource.name

        if not resource:
            raise ValueError("Resource Not found!")

        if resource.storage_type == StorageType.S3.value:
            bucket_name = get_config("BUCKET_NAME")
            file_key = resource.path
            return self.s3.get_object(Bucket=bucket_name, Key=file_key)["Body"]
        else:
            abs_file_path = Path(download_file_path).resolve()
            if not abs_file_path.is_file():
                raise ValueError("File not found")
            return open(str(abs_file_path), "rb")

    def get_all_resources(self, agent_execution_id=None):
        """
        Gets all resources for the agent or agent execution.

        Args:
            agent_execution_id (int, optional): The ID of the agent execution.

        Returns:
            List[Resources]: A list of resources associated with the agent or agent execution.
        """

        if agent_execution_id:
            resources = self.db_session.query(Resource).filter(
                                        Resource.agent_id == self.agent_id,
                                        Resource.agent_execution_id == agent_execution_id).all()
        else:
            resources = self.db_session.query(Resource).filter(Resource.agent_id == self.agent_id).all()

        return resources