from backend_central_dev.constant import *
import lightning as L
import sys
import os

from lightning.pytorch.loggers import CSVLogger

from backend_central_dev.xai_sdk import (
    get_trained_model_and_dataset_from_services,
    download_xai_modules_source_code_and_load,
    get_pipeline_execution_from_ticket
)
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


def task_wrapper(task_ticket, publisher_endpoint_url, task_parameters, xai_eval_func):
    L.seed_everything(42)
    run_mode = task_parameters.get('run_mode', 'run_batch')
    if run_mode == 'run_batch':
        pipeline_ticket = task_parameters[PipelineExecution.pipeline_ticket]
        pipeline_execution = get_pipeline_execution_from_ticket(
            publisher_endpoint_url,
            pipeline_ticket)

        trained_model_task_ticket = pipeline_execution[PipelineExecution.task_execution_tickets][0]

        print("Get model from: ", trained_model_task_ticket)
        model, datamodule = get_trained_model_and_dataset_from_services(
            publisher_endpoint_url,
            trained_model_task_ticket,
            task_parameters
        )

        xai_modules = download_xai_modules_source_code_and_load(
            task_parameters[TaskExecution.xai_service_url]
        )

        xai_eval_result = xai_eval_func(model, datamodule, xai_modules)

        logger = CSVLogger(
            os.environ['COMPONENT_STATIC_PATH'],
            name="rs", version=task_ticket
        )

        csv_files = os.path.join(
            os.environ['COMPONENT_STATIC_PATH'], 'rs', task_ticket, 'metrics.csv')
        os.makedirs(os.path.dirname(csv_files), exist_ok=True)
        df = pd.DataFrame([xai_eval_result])
        df['epoch'] = df.index
        df = df[['epoch', 'rcap']]
        df.to_csv(
            csv_files, index=False, encoding='utf-8'
        )

        # device = get_device()
        # map = xai_func(
        #     model.to(device), image_tensor.to(device), None,
        #     **task_parameters.get('xai_parameters', {})
        # ).detach().cpu().numpy()[0]

    else:
        print(task_parameters)
        ...
