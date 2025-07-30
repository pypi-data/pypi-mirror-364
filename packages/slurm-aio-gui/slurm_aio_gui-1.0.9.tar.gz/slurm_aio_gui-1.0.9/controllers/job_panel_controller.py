from PyQt6.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from core.terminal_helper import SSHConnectionDetails, TerminalHelper
from models.project_model import JobsModel
from views.jobs_panel_view import JobsPanelView
from core.event_bus import get_event_bus, Events, Event
from core.slurm_api import *
from widgets.log_viewer_widget import LogViewerDialog
from widgets.toast_widget import show_error_toast, show_success_toast, show_warning_toast
from widgets.new_job_widget import JobCreationDialog

class JobsPanelController:
    def __init__(self, model: JobsModel, view: JobsPanelView):
        self.model = model
        self.view = view
        self.event_bus = get_event_bus()
        self._event_bus_subscription()

    def _event_bus_subscription(self):
        """Subscribe to model changes from the event bus."""
        self.event_bus.subscribe(
            Events.PROJECT_LIST_CHANGED, self._on_project_list_changed
        )
        self.event_bus.subscribe(Events.CONNECTION_STATE_CHANGED, self._handle_connection_change)
        self.event_bus.subscribe(Events.ADD_PROJECT, self.model.add_project)
        self.event_bus.subscribe(Events.DEL_PROJECT, self._handle_delete_project)
        self.event_bus.subscribe(Events.PROJECT_SELECTED, self._handle_project_selection)
        self.event_bus.subscribe(Events.MODIFY_JOB, self._handle_modify_job)
        self.event_bus.subscribe(Events.DEL_JOB, self._handle_delete_job)
        self.event_bus.subscribe(Events.DUPLICATE_JOB, self._handle_duplicate_job) 
        self.event_bus.subscribe(Events.JOB_SUBMITTED, self._handle_submit_job)
        self.event_bus.subscribe(Events.STOP_JOB, self._handle_stop_job)
        self.event_bus.subscribe(Events.OPEN_JOB_TERMINAL, self._handle_open_job_terminal)
        self.event_bus.subscribe(Events.VIEW_LOGS, self._handle_view_logs)
        self.event_bus.subscribe(Events.CREATE_JOB_DIALOG_REQUESTED, self._handle_create_job_dialog_request)

    def _handle_create_job_dialog_request(self, event: Event):
        """Handles the request to open the new job dialog."""
        project_name = event.data["project_name"]
        project = next((p for p in self.model.projects if p.name == project_name), None)
        
        cached_job = project.cached_job if project else None
        
        dialog = JobCreationDialog(
            parent=self.view, 
            project_name=project_name, 
            cached_job=cached_job
        )
        
        if dialog.exec():
            new_job_data = dialog.get_job()
            if new_job_data:
                self.event_bus.emit(
                    Events.ADD_JOB,
                    data={"project_name": project_name, "job_data": new_job_data},
                    source="JobsPanelController",
                )

    def _handle_connection_change(self, event: Event):
        new_state = event.data["new_state"]
        if new_state == ConnectionState.CONNECTED:
            self.model.load_from_remote()
        elif new_state == ConnectionState.DISCONNECTED:
            self.view.shutdown_ui(is_connected=False)
        
        if new_state == ConnectionState.DISCONNECTED:
            self.view.shutdown_ui(is_connected=False)
        elif new_state == ConnectionState.CONNECTED:
            self.view.shutdown_ui(is_connected=True)

    def _on_project_list_changed(self, event: Event):
        """Update the view when the project list in the model changes."""
        projects = event.data.get("projects", [])
        # Update the job tables in the right-hand panel first
        self.view.jobs_table_view.update_projects(projects)
        # Then, update the list of projects, which triggers selection
        self.view.project_group.update_view(projects)

    def _handle_delete_project(self, event):
        """Confirm and delete a project."""
        name = event.data["project_name"]
        reply = QMessageBox.question(
            self.view,
            "Delete Project",
            f"Are you sure you want to delete the project '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.remove_project(name)
    
    def _handle_modify_job(self, event: Event):
        """Brings up the job modification dialog."""
        project_name = event.data["project_name"]
        job_id = event.data["job_id"]
        
        job_to_modify = self.model.get_job_by_id(project_name, job_id)
        
        if job_to_modify and job_to_modify.status == "NOT_SUBMITTED":
            dialog = JobCreationDialog(parent=self.view, project_name=project_name, job_to_modify=job_to_modify)
            if dialog.exec():
                modified_job = dialog.get_job()
                if modified_job:
                    self.model.update_job_in_project(project_name, job_id, modified_job)

    def _handle_project_selection(self, event):
        """Update the active project in the model."""
        name = event.data["project"]
        self.model.set_active_project(name)
    
    def _handle_delete_job(self, event):
        """Confirm and delete a job."""
        project_name = event.data["project_name"]
        job_id = event.data["job_id"]
        job = self.model.get_job_by_id(project_name, job_id)
        if not job:
            return
        self.model.remove_job_from_project(project_name, job_id)

    def _handle_duplicate_job(self, event: Event):
        """Handle job duplication request."""
        project_name = event.data["project_name"]
        job_id = event.data["job_id"]
        self.model.duplicate_job(project_name, job_id)
    
    def _handle_submit_job(self, event: Event):
        """Handle job submission."""
        project_name = event.data["project_name"]
        job_id = event.data["job_id"]
        job_to_submit = self.model.get_job_by_id(project_name, job_id)

        if job_to_submit:
            slurm_api = SlurmAPI()
            new_job_id, error = slurm_api.submit_job(job_to_submit)
            
            if new_job_id:
                self.model.update_job_after_submission(project_name, job_id, new_job_id)
                show_success_toast(self.view, "Job Submitted", f"Job submitted successfully with ID: {new_job_id}")
            else:
                show_error_toast(self.view, "Submission Failed", f"Error: {error}")
    
    def _handle_stop_job(self, event: Event):
        """Handle job cancellation (scancel) request."""
        job_id = event.data["job_id"]
        slurm_api = SlurmAPI()
        
        if slurm_api.connection_status != ConnectionState.CONNECTED:
            show_error_toast(self.view, "Connection Error", "Not connected to the cluster.")
            return

        stdout, stderr = slurm_api.cancel_job(job_id)

        if stderr:
            show_error_toast(self.view, "Stop Job Failed", f"Could not stop job {job_id}: {stderr}")
        else:
            show_success_toast(self.view, "Job Stop Requested", f"Cancel signal sent to job {job_id}.")
    
    def _handle_open_job_terminal(self, event: Event):
        """Handle request to open a terminal for a running job."""
        job_id = event.data["job_id"]
        
        slurm_api = SlurmAPI()
        if slurm_api.connection_status != ConnectionState.CONNECTED:
            show_warning_toast(self.view, "Connection Required", "Please establish a SLURM connection first.")
            return
            
        try:
            helper = TerminalHelper()
            # Construct the command to attach to the job
            srun_command = f"srun --jobid={job_id} --pty bash"
            
            # Create connection details with the command to run
            connection_details = SSHConnectionDetails(
                host=slurm_api._config.host,
                username=slurm_api._config.username,
                password=slurm_api._config.password,
                command_to_run=srun_command
            )
            
            helper.open_ssh_terminal(connection_details, parent_widget=self.view)
            
        except Exception as e:
            show_error_toast(self.view, "Terminal Error", f"Failed to open terminal: {str(e)}")
    
    def _handle_view_logs(self, event: Event):
        """Handles the request to view job logs."""
        project_name = event.data["project_name"]
        job_id = event.data["job_id"]
        job = self.model.get_job_by_id(project_name, job_id)

        if not job:
            show_error_toast(self.view, "Error", f"Could not find job with ID {job_id}.")
            return

        # Create and show the log viewer dialog
        dialog = LogViewerDialog(job, parent=self.view)
        dialog.exec()
        
    def _shutdown(self, event):
        """Handle connection status changes."""
        new_state = event.data["new_state"]
        if new_state == ConnectionState.DISCONNECTED:
            self.view.shutdown_ui(is_connected=False)
        elif new_state == ConnectionState.CONNECTED:
            self.view.shutdown_ui(is_connected=True)
