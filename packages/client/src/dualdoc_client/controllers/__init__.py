from dualdoc_client.controllers.document_controller import DocumentController

try:
    from dualdoc_client.controllers.project_controller import ProjectController

    __all__ = ["DocumentController", "ProjectController"]
except ImportError:
    __all__ = ["DocumentController"]
