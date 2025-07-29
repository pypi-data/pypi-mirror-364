"""Module for managing optimization experiments.

This module provides the `Experiment` class for managing optimization experiments.
The `Experiment` class handles experiment-level data (problems, instances, global parameters)
while the `Run` class handles run-specific data (solutions, run parameters).
This explicit separation replaces the previous implicit with-clause behavior.

"""

import json
import pathlib
import typing as typ
import uuid
from dataclasses import dataclass, field
from datetime import datetime

import jijmodeling as jm
import numpy as np
import ommx.artifact as ox_artifact
import ommx.v1 as ommx_v1
import pandas as pd

from .environment import EnvironmentInfo, collect_environment_info
from .run import Run
from .table import create_table, create_table_from_stores
from .utils import type_check
from .v1.datastore import DataStore
from .v1.exp_dataspace import ExperimentDataSpace

DEFAULT_RESULT_DIR = pathlib.Path(".minto_experiments")
"""Default directory `.minto_experiments` for saving experiment data. You can change this by setting `savedir` in the `Experiment` class."""


@dataclass
class Experiment:
    """Class to manage optimization experiments.

    This class provides a structured way to manage optimization experiments,
    handling experiment-level data (problems, instances, global parameters).
    Run-specific data is handled by the Run class through explicit run creation.

    This design eliminates the previous implicit with-clause behavior where
    the storage location depended on context. Now, experiment-level and
    run-level operations are explicitly separated.

    Attributes:
        name (str): Name of the experiment.
        savedir (pathlib.Path): Directory path for saving experiment data.
        auto_saving (bool): Flag to enable automatic saving of experiment data.
        collect_environment (bool): Flag to enable environment metadata collection.
        timestamp (datetime): Timestamp of the experiment creation.

    Properties:
        experiment_name (str): Full name of the experiment with timestamp.
        dataspace (ExperimentDataSpace): Data storage space for the experiment.
    """

    name: str = field(default_factory=lambda: str(uuid.uuid4().hex[:8]))
    savedir: str | pathlib.Path = DEFAULT_RESULT_DIR
    auto_saving: bool = True
    collect_environment: bool = True

    timestamp: datetime = field(default_factory=datetime.now, init=False)

    def __post_init__(self):
        """Post-initialization method for Experiment class."""
        # Add timestamp to experiment name
        self.experiment_name = f"{self.name}_{self.timestamp.strftime('%Y%m%d%H%M%S')}"
        # Set save directory path
        self.savedir = pathlib.Path(self.savedir) / self.experiment_name
        # Create directory if auto_saving is enabled
        if self.auto_saving:
            self.savedir.mkdir(exist_ok=True, parents=True)
        # Initialize dataspace
        self.dataspace = ExperimentDataSpace(self.name)

        # Collect environment metadata at experiment level (once at start)
        if self.collect_environment:
            self._collect_and_log_environment_info()

    def create_run(self) -> Run:
        """Create a new run for this experiment.

        This method explicitly creates a new Run object for logging run-specific data.
        Unlike the previous implicit with-clause behavior, this makes it clear that
        data logged to the returned Run object will be stored at the run level.

        Returns:
            Run: A new Run instance for logging run-specific data.
        """
        run = Run()
        run._experiment = self  # Set parent reference
        run._run_id = self.dataspace.add_run_datastore(
            run._datastore, with_save=self.auto_saving, save_dir=self.savedir
        )
        return run

    def save(self, path: typ.Optional[str | pathlib.Path] = None):
        """Save the experiment data to disk.

        Args:
            path: Optional path to save to. If None, uses default savedir.
        """
        if path is not None:
            self.dataspace.save_dir(path)
        else:
            self.dataspace.save_dir(self.savedir)

    def log_problem(
        self, problem_name: str | jm.Problem, problem: typ.Optional[jm.Problem] = None
    ):
        """Log an optimization problem to the experiment (experiment-level data).

        Args:
            problem_name: Name of the problem, or the problem object itself.
            problem: Problem object (if problem_name is a string).
        """
        _name, _problem = self._get_name_or_default(
            problem_name, problem, self.dataspace.experiment_datastore.problems
        )
        self.dataspace.add_exp_data(
            _name,
            _problem,
            "problems",
            with_save=self.auto_saving,
            save_dir=self.savedir,
        )

    def log_instance(
        self,
        instance_name: str | ommx_v1.Instance,
        instance: typ.Optional[ommx_v1.Instance] = None,
    ):
        """Log an optimization problem instance to the experiment (experiment-level data).

        Args:
            instance_name: Name of the instance, or the instance object itself.
            instance: Instance object (if instance_name is a string).
        """
        _name, _instance = self._get_name_or_default(
            instance_name, instance, self.dataspace.experiment_datastore.instances
        )
        self.dataspace.add_exp_data(
            _name,
            _instance,
            "instances",
            with_save=self.auto_saving,
            save_dir=self.savedir,
        )

    def log_parameter(
        self,
        name: str,
        value: float | int | str | list | dict | np.ndarray,
    ):
        """Log a parameter to the experiment (experiment-level data).

        This method logs parameters that apply to the entire experiment,
        such as global configuration, dataset properties, or experiment setup.
        For run-specific parameters, use the Run.log_parameter() method.

        Args:
            name (str): Name of the parameter.
            value: Value of the parameter. Can be scalar or complex data structure.
        """
        if isinstance(value, (list, dict, np.ndarray)):
            # Check value is serializable
            try:
                from minto.v1.json_encoder import NumpyEncoder

                json.dumps(value, cls=NumpyEncoder)
            except TypeError:
                raise ValueError(f"Value is not serializable.")

            self.log_object(name, {"parameter_" + name: value})

        self.dataspace.add_exp_data(
            name, value, "parameters", with_save=self.auto_saving, save_dir=self.savedir
        )

    def log_params(self, params: dict[str, float | int | str]):
        """Log multiple parameters to the experiment (experiment-level data).

        Args:
            params: Dictionary of parameter names and values.
        """
        for name, value in params.items():
            self.log_parameter(name, value)

    def log_object(self, name: str, value: dict[str, typ.Any]):
        """Log a custom object to the experiment (experiment-level data).

        Args:
            name: Name of the object
            value: Dictionary containing the object data
        """
        type_check([("name", name, str), ("value", value, dict)])
        self.dataspace.add_exp_data(
            name, value, "objects", with_save=self.auto_saving, save_dir=self.savedir
        )

    def _get_name_or_default(
        self, name: str | typ.Any, obj: typ.Optional[typ.Any], storage: dict
    ) -> tuple[str, typ.Any]:
        """Get the name or generate a default name if the object is provided.

        Args:
            name: Name of the object or the object itself.
            obj: The object itself (optional).
            storage: Storage dictionary to generate default names.

        Returns:
            Tuple of (name, object).
        """
        if not isinstance(name, str) and obj is None:
            return str(len(storage)), name
        elif isinstance(name, str) and (obj is not None):
            return name, obj
        else:
            raise ValueError(
                "Invalid arguments: name must be a string or obj must be provided."
            )

    @classmethod
    def load_from_dir(cls, savedir: str | pathlib.Path) -> "Experiment":
        """Load an experiment from a directory containing saved data.

        Args:
            savedir: Directory path containing the saved experiment data.

        Returns:
            Experiment: Instance of the loaded experiment.
        """
        savedir = pathlib.Path(savedir)

        # check directory exists
        if not savedir.exists():
            raise FileNotFoundError(f"Directory not found: {savedir}")

        dataspace = ExperimentDataSpace.load_from_dir(savedir)
        exp_name = dataspace.experiment_datastore.meta_data["experiment_name"]
        experiment = cls(exp_name, auto_saving=False)
        experiment.dataspace = dataspace
        return experiment

    def save_as_ommx_archive(
        self, savefile: typ.Optional[str | pathlib.Path] = None
    ) -> ox_artifact.Artifact:
        """Save the experiment data as an OMMX artifact.

        Args:
            savefile: Path to save the OMMX artifact. If None, a default name is generated.
        """
        if savefile is None:
            # Generate default filename with timestamp
            savefile = (
                pathlib.Path(self.savedir)
                / f"{self.name}_{self.timestamp.strftime('%Y%m%d%H%M%S')}.ommx"
            )
        builder = ox_artifact.ArtifactBuilder.new_archive_unnamed(savefile)
        self.dataspace.add_to_artifact_builder(builder)
        return builder.build()

    @classmethod
    def load_from_ommx_archive(cls, savefile: str | pathlib.Path) -> "Experiment":
        """Load an experiment from an OMMX artifact file.

        Args:
            savefile: Path to the OMMX artifact file.

        Returns:
            Experiment: Instance of the loaded experiment.
        """
        dataspace = ExperimentDataSpace.load_from_ommx_archive(savefile)
        exp_name = dataspace.experiment_datastore.meta_data["experiment_name"]
        experiment = cls(exp_name, auto_saving=False)
        experiment.dataspace = dataspace
        return experiment

    def get_run_table(self) -> pd.DataFrame:
        """Get the run data as a table.

        Returns:
            pd.DataFrame: DataFrame containing the run data.
        """
        run_table = create_table_from_stores(self.dataspace.run_datastores)
        run_table.index.name = "run_id"
        return run_table

    def get_experiment_tables(self) -> dict[str, pd.DataFrame]:
        """Get the experiment data as a table.

        Returns:
            dict[str, pd.DataFrame]: Dictionary containing the experiment data tables.
        """
        exp_table = create_table(self.dataspace.experiment_datastore)
        return exp_table

    def push_github(
        self,
        org: str,
        repo: str,
        name: typ.Optional[str] = None,
        tag: typ.Optional[str] = None,
    ) -> ox_artifact.Artifact:
        """Push the experiment data to a GitHub repository.

        Returns:
            ox_artifact.Artifact: OMMX artifact containing the experiment data.
        """
        builder = ox_artifact.ArtifactBuilder.for_github(
            org=org,
            repo=repo,
            name=name if name else self.name,
            tag=tag if tag else self.timestamp.strftime("%Y%m%d%H%M%S"),
        )
        self.dataspace.add_to_artifact_builder(builder)
        artifact = builder.build()
        artifact.push()
        return artifact

    @property
    def runs(self) -> list[DataStore]:
        """Get the list of run datastores in the experiment.

        This property provides access to all run datastores in the experiment.
        Returns the same result as `self.dataspace.run_datastores`.

        Returns:
            list[DataStore]: List of run datastores in the experiment.
        """
        return self.dataspace.run_datastores

    @classmethod
    def load_from_registry(cls, imagename: str) -> "Experiment":
        """Load an experiment from a Docker registry.

        Args:
            imagename: Name of the Docker image containing the experiment data.

        Returns:
            Experiment: Instance of the loaded experiment.
        """
        artifact = ox_artifact.Artifact.load(imagename)
        dataspace = ExperimentDataSpace.load_from_ommx_artifact(artifact)
        exp_name = dataspace.experiment_datastore.meta_data["experiment_name"]
        experiment = cls(exp_name, auto_saving=False)
        experiment.dataspace = dataspace
        return experiment

    @classmethod
    def concat(
        cls,
        experiments: list["Experiment"],
        name: typ.Optional[str] = None,
        savedir: str | pathlib.Path = DEFAULT_RESULT_DIR,
        auto_saving: bool = True,
    ) -> "Experiment":
        """Concatenate multiple experiments into a single experiment.

        Args:
            experiments: List of Experiment instances to concatenate.
            name: Name of the concatenated experiment.
            savedir: Directory path for saving the concatenated experiment data.
            auto_saving: Flag to enable automatic saving of the concatenated experiment

        Example:
            ```python
            import minto
            exp1 = minto.Experiment("exp1")
            exp2 = minto.Experiment("exp2")
            exp3 = minto.Experiment("exp3")
            new_exp = minto.Experiment.concat([exp1, exp2, exp3])
            ```

        Returns:
            Experiment: Instance of the concatenated experiment.
        """

        name = name or uuid.uuid4().hex[:8]

        if len(experiments) == 0:
            raise ValueError("No experiments provided.")

        # check if dataspaces have the same experiment-wide data
        first_datastore = experiments[0].dataspace.experiment_datastore
        for experiment in experiments[1:]:
            datastore = experiment.dataspace.experiment_datastore
            if datastore.problems.keys() != first_datastore.problems.keys():
                raise ValueError("Experiments have different problems.")
            if datastore.instances.keys() != first_datastore.instances.keys():
                raise ValueError("Experiments have different instances.")
            if datastore.solutions.keys() != first_datastore.solutions.keys():
                raise ValueError("Experiments have different solutions.")
            if datastore.objects.keys() != first_datastore.objects.keys():
                raise ValueError("Experiments have different objects.")
            if datastore.parameters.keys() != first_datastore.parameters.keys():
                raise ValueError("Experiments have different parameters.")
            if datastore.meta_data.keys() != first_datastore.meta_data.keys():
                raise ValueError("Experiments have different meta data.")

        new_experiment = cls(name, savedir, auto_saving)
        new_experiment.dataspace.experiment_datastore = first_datastore

        for experiment in experiments:
            for datastore in experiment.dataspace.run_datastores:
                new_experiment.dataspace.add_run_datastore(
                    datastore,
                    with_save=new_experiment.auto_saving,
                    save_dir=new_experiment.savedir,
                )

        return new_experiment

    def _collect_and_log_environment_info(self):
        """Collect and log environment metadata."""
        try:
            env_info = collect_environment_info()

            # Save environment info as experiment-level metadata
            self.dataspace.experiment_datastore.add(
                "environment_info",
                env_info.to_dict(),
                "meta_data",
                with_save=self.auto_saving,
                save_dir=self.savedir,
            )

            # Also save as object for reliable persistence
            self.dataspace.experiment_datastore.add(
                "environment_info",
                env_info.to_dict(),
                "objects",
                with_save=self.auto_saving,
                save_dir=self.savedir,
            )

            # Save key environment info as parameters (for table display)
            self.dataspace.experiment_datastore.add(
                "python_version",
                env_info.python_version,
                "parameters",
                with_save=self.auto_saving,
                save_dir=self.savedir,
            )
            self.dataspace.experiment_datastore.add(
                "os_name",
                env_info.os_name,
                "parameters",
                with_save=self.auto_saving,
                save_dir=self.savedir,
            )
            self.dataspace.experiment_datastore.add(
                "platform_info",
                env_info.platform_info,
                "parameters",
                with_save=self.auto_saving,
                save_dir=self.savedir,
            )

        except Exception as e:
            # Show warning if environment info collection fails but continue experiment
            print(f"Warning: Failed to collect environment information: {e}")

    def get_environment_info(self) -> typ.Optional[dict]:
        """Get experiment environment metadata.

        Returns:
            Environment metadata dictionary, or None if not collected.
        """
        # First try to get from metadata
        env_info = self.dataspace.experiment_datastore.meta_data.get("environment_info")
        if env_info is not None:
            return env_info

        # If not in metadata, try to get from objects
        return self.dataspace.experiment_datastore.objects.get("environment_info")

    def print_environment_summary(self):
        """Print a summary of environment information."""
        env_info = self.get_environment_info()
        if env_info is None:
            print("Environment information not available.")
            print(
                "Set collect_environment=True when creating the experiment to collect environment metadata."
            )
            return

        print("=== Experiment Environment Information ===")
        print(f"OS: {env_info['os_name']} {env_info['os_version']}")
        print(f"Platform: {env_info['platform_info']}")
        print(f"Python: {env_info['python_version']}")
        print(f"CPU: {env_info['cpu_info']} ({env_info['cpu_count']} cores)")
        print(f"Memory: {env_info['memory_total'] // (1024**3)} GB")
        print(f"Architecture: {env_info['architecture']}")

        if env_info.get("virtual_env"):
            print(f"Virtual Environment: {env_info['virtual_env']}")

        print(f"Timestamp: {env_info['timestamp']}")

        print(f"\nKey Package Versions:")
        for pkg, version in env_info["package_versions"].items():
            print(f"  {pkg}: {version}")
