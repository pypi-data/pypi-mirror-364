import minto
import minto.v0


def migrate_to_v1_from_v0(experiment: minto.v0.Experiment) -> minto.Experiment:
    import jijmodeling as jm
    import numpy as np

    df = experiment.table(enable_sampleset_expansion=False)
    exp_v1 = minto.Experiment(name=experiment.name)
    ignored_key = ["experiment_name", "run_id"]
    for row_id, row in df.iterrows():
        run = exp_v1.create_run()
        with run:
            for name, value in row.items():
                if name in ignored_key:
                    continue
                name_str = str(name)  # Convert to string to satisfy type checker
                if isinstance(value, (str, int, float)):
                    run.log_parameter(name_str, value)
                elif isinstance(value, jm.Problem):
                    run._datastore.add(name_str, value, "problems")
                elif isinstance(value, jm.experimental.SampleSet):
                    run.log_sampleset(name_str, value)
                elif isinstance(value, (list, np.ndarray)):
                    run.log_object(name_str, {name_str: value})
                elif isinstance(value, dict):
                    run.log_object(
                        name_str, dict(value)
                    )  # Convert to ensure proper typing
    return exp_v1
