import datetime as dt
from typing import Any

import polars as pl
from bayesline.api import (
    AsyncSettingsRegistry,
    SettingsRegistry,
)
from bayesline.api._src.tasks import AsyncTask, Task, TaskResponse
from bayesline.api.equity import (
    AsyncFactorModelApi,
    AsyncFactorModelEngineApi,
    AsyncFactorModelLoaderApi,
    FactorModelApi,
    FactorModelEngineApi,
    FactorModelLoaderApi,
    FactorRiskModelSettings,
    FactorRiskModelSettingsMenu,
    FactorType,
    UniverseSettings,
    UniverseSettingsMenu,
)
from bayesline.api.types import (
    DateLike,
    IdType,
    to_date,
    to_date_string,
)

from bayesline.apiclient._src.client import ApiClient, AsyncApiClient
from bayesline.apiclient._src.settings import (
    AsyncHttpSettingsRegistryClient,
    HttpSettingsRegistryClient,
)
from bayesline.apiclient._src.tasks import (
    AsyncDataFrameTaskClient,
    AsyncTaskClient,
    DataFrameTaskClient,
    TaskClient,
)


class FactorModelClientImpl(FactorModelApi):

    def __init__(
        self,
        client: ApiClient,
        model_id: int,
        settings: FactorRiskModelSettings,
        tasks_client: ApiClient,
        tqdm_progress: bool,
    ):
        self._client = client
        self._model_id = model_id
        self._settings = settings
        self._tasks_client = tasks_client
        self._tqdm_progress = tqdm_progress

    def dates(self) -> list[dt.date]:
        response = self._client.get(f"model/{self._model_id}/dates")
        return [to_date(d) for d in response.json()]

    def factors(self, *which: FactorType) -> list[str]:
        response = self._client.get(
            f"model/{self._model_id}/factors",
            params={"which": list(which)},
        )
        return response.json()

    def exposures(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        task = self.exposures_as_task(
            start=start, end=end, id_type=id_type, stage=stage
        )
        return task.wait_result(check_interval=1)

    def exposures_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(f"model/{self._model_id}/exposures", params=params)
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        task = self.universe_as_task(start=start, end=end, id_type=id_type, stage=stage)
        return task.wait_result(check_interval=1)

    def universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(f"model/{self._model_id}/universe", params=params)
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def estimation_universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        task = self.estimation_universe_as_task(
            start=start, end=end, id_type=id_type, stage=stage
        )
        return task.wait_result(check_interval=1)

    def estimation_universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(
            f"model/{self._model_id}/estimation-universe", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def market_caps(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        task = self.market_caps_as_task(start=start, end=end, id_type=id_type)
        return task.wait_result(check_interval=1)

    def market_caps_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(
            f"model/{self._model_id}/market-caps", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def weights(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        task = self.weights_as_task(start=start, end=end, id_type=id_type)
        return task.wait_result(check_interval=1)

    def weights_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(f"model/{self._model_id}/weights", params=params)
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def future_asset_returns(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        task = self.future_asset_returns_as_task(start=start, end=end, id_type=id_type)
        return task.wait_result(check_interval=1)

    def future_asset_returns_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = self._client.get(
            f"model/{self._model_id}/future-asset-returns", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def t_stats(self) -> pl.DataFrame:
        task = self.t_stats_as_task()
        return task.wait_result(check_interval=1)

    def t_stats_as_task(self) -> Task[pl.DataFrame]:
        response = self._client.get(f"model/{self._model_id}/t-stats")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def p_values(self) -> pl.DataFrame:
        task = self.p_values_as_task()
        return task.wait_result(check_interval=1)

    def p_values_as_task(self) -> Task[pl.DataFrame]:
        response = self._client.get(f"model/{self._model_id}/p-values")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def r2(self) -> pl.DataFrame:
        task = self.r2_as_task()
        return task.wait_result(check_interval=1)

    def r2_as_task(self) -> Task[pl.DataFrame]:
        response = self._client.get(f"model/{self._model_id}/r2")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def sigma2(self) -> pl.DataFrame:
        task = self.sigma2_as_task()
        return task.wait_result()

    def sigma2_as_task(self) -> Task[pl.DataFrame]:
        response = self._client.get(f"model/{self._model_id}/sigma2")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    def fret(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> pl.DataFrame:
        task = self.fret_as_task(freq=freq, cumulative=cumulative, start=start, end=end)
        return task.wait_result(check_interval=1)

    def fret_as_task(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> Task[pl.DataFrame]:
        params: dict[str, Any] = {}
        if freq is not None:
            params["freq"] = freq
        if cumulative:
            params["cumulative"] = cumulative
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = self._client.get(
            f"model/{self._model_id}/fret",
            params=params,
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return DataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )


class AsyncFactorModelClientImpl(AsyncFactorModelApi):

    def __init__(
        self,
        client: AsyncApiClient,
        model_id: int,
        settings: FactorRiskModelSettings,
        tasks_client: AsyncApiClient,
        tqdm_progress: bool,
    ):
        self._client = client
        self._model_id = model_id
        self._settings = settings
        self._tasks_client = tasks_client
        self._tqdm_progress = tqdm_progress

    async def dates(self) -> list[dt.date]:
        response = await self._client.get(f"model/{self._model_id}/dates")
        return [to_date(d) for d in response.json()]

    async def factors(self, *which: FactorType) -> list[str]:
        response = await self._client.get(
            f"model/{self._model_id}/factors",
            params={"which": list(which)},
        )
        return response.json()

    async def exposures(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        task = await self.exposures_as_task(
            start=start, end=end, id_type=id_type, stage=stage
        )
        return await task.wait_result(check_interval=1)

    async def exposures_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/exposures", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        task = await self.universe_as_task(
            start=start, end=end, id_type=id_type, stage=stage
        )
        return await task.wait_result(check_interval=1)

    async def universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/universe", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def estimation_universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        task = await self.estimation_universe_as_task(
            start=start, end=end, id_type=id_type, stage=stage
        )
        return await task.wait_result(check_interval=1)

    async def estimation_universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {"stage": stage}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/estimation-universe", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def market_caps(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        task = await self.market_caps_as_task(start=start, end=end, id_type=id_type)
        return await task.wait_result(check_interval=1)

    async def market_caps_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/market-caps", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def weights(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        task = await self.weights_as_task(start=start, end=end, id_type=id_type)
        return await task.wait_result(check_interval=1)

    async def weights_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/weights", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def future_asset_returns(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        task = await self.future_asset_returns_as_task(
            start=start, end=end, id_type=id_type
        )
        return await task.wait_result(check_interval=1)

    async def future_asset_returns_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {}
        if start is not None:
            params["start"] = to_date(start)
        if end is not None:
            params["end"] = to_date(end)
        if id_type:
            params["id_type"] = id_type
        response = await self._client.get(
            f"model/{self._model_id}/future-asset-returns", params=params
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def t_stats(self) -> pl.DataFrame:
        task = await self.t_stats_as_task()
        return await task.wait_result(check_interval=1)

    async def t_stats_as_task(self) -> AsyncTask[pl.DataFrame]:
        response = await self._client.get(f"model/{self._model_id}/t-stats")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def p_values(self) -> pl.DataFrame:
        task = await self.p_values_as_task()
        return await task.wait_result(check_interval=1)

    async def p_values_as_task(self) -> AsyncTask[pl.DataFrame]:
        response = await self._client.get(f"model/{self._model_id}/p-values")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def r2(self) -> pl.DataFrame:
        task = await self.r2_as_task()
        return await task.wait_result(check_interval=1)

    async def r2_as_task(self) -> AsyncTask[pl.DataFrame]:
        response = await self._client.get(f"model/{self._model_id}/r2")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def sigma2(self) -> pl.DataFrame:
        task = await self.sigma2_as_task()
        return await task.wait_result()

    async def sigma2_as_task(self) -> AsyncTask[pl.DataFrame]:
        response = await self._client.get(f"model/{self._model_id}/sigma2")
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )

    async def fret(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> pl.DataFrame:
        task = await self.fret_as_task(
            freq=freq, cumulative=cumulative, start=start, end=end
        )
        return await task.wait_result(check_interval=1)

    async def fret_as_task(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> AsyncTask[pl.DataFrame]:
        params: dict[str, Any] = {}
        if freq is not None:
            params["freq"] = freq
        if cumulative:
            params["cumulative"] = cumulative
        if start is not None:
            params["start"] = to_date_string(start)
        if end is not None:
            params["end"] = to_date_string(end)
        response = await self._client.get(
            f"model/{self._model_id}/fret",
            params=params,
        )
        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncDataFrameTaskClient(
            self._tasks_client,
            response_model.task_id,
            tqdm_progress=self._tqdm_progress,
        )


class FactorModelTaskClient(TaskClient[FactorModelApi]):

    def __init__(
        self,
        *,
        api_client: ApiClient,
        task_id: str,
        tqdm_progress: bool,
        model_id: int,
        settings: FactorRiskModelSettings,
        factorrisk_client: ApiClient,
    ):
        super().__init__(
            client=api_client, task_id=task_id, tqdm_progress=tqdm_progress
        )
        self._model_id = model_id
        self._settings = settings
        self._factorrisk_client = factorrisk_client

    def get_result(self) -> FactorModelApi:
        response = self._api_client.get(
            f"{self.task_id}/result", params={"type": "json"}
        )
        if response.status_code == 404:
            raise KeyError(f"Task {self.task_id} not found")
        self.raise_for_status(response)
        return FactorModelClientImpl(
            self._factorrisk_client,
            self._model_id,
            self._settings,
            self._api_client,
            self._tqdm_progress,
        )


class AsyncFactorModelTaskClient(AsyncTaskClient[AsyncFactorModelApi]):

    def __init__(
        self,
        *,
        api_client: AsyncApiClient,
        task_id: str,
        tqdm_progress: bool,
        model_id: int,
        settings: FactorRiskModelSettings,
        factorrisk_client: AsyncApiClient,
    ):
        super().__init__(
            client=api_client, task_id=task_id, tqdm_progress=tqdm_progress
        )
        self._model_id = model_id
        self._settings = settings
        self._factorrisk_client = factorrisk_client

    async def get_result(self) -> AsyncFactorModelApi:
        response = await self._api_client.get(
            f"{self._task_id}/result", params={"type": "json"}
        )
        if response.status_code == 404:
            raise KeyError(f"Task {self.task_id} not found")
        self.raise_for_status(response)
        return AsyncFactorModelClientImpl(
            self._factorrisk_client,
            self._model_id,
            self._settings,
            self._api_client,
            self._tqdm_progress,
        )


class FactorModelEngineClientImpl(FactorModelEngineApi):

    def __init__(
        self,
        client: ApiClient,
        tasks_client: ApiClient,
        settings: FactorRiskModelSettings,
        model_id: int | None = None,
        tqdm_progress: bool = False,
    ):
        self._client = client
        self._tasks_client = tasks_client
        self._settings = settings
        self._model_id = model_id
        self._tqdm_progress = tqdm_progress

    @property
    def settings(self) -> FactorRiskModelSettings:
        return self._settings

    def get(self) -> FactorModelApi:
        task = self.get_as_task()
        return task.wait_result()

    def get_as_task(self) -> Task[FactorModelApi]:
        params = {}
        if self._model_id is not None:
            params["model_id"] = self._model_id
        response = self._client.post(
            "model", body=self._settings.model_dump(), params=params
        )

        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        self._model_id = response_model.extra["model_id"]
        return FactorModelTaskClient(
            api_client=self._tasks_client,
            task_id=response_model.task_id,
            tqdm_progress=self._tqdm_progress,
            model_id=self._model_id,
            settings=self._settings,
            factorrisk_client=self._client,
        )


class AsyncFactorModelEngineClientImpl(AsyncFactorModelEngineApi):

    def __init__(
        self,
        client: AsyncApiClient,
        tasks_client: AsyncApiClient,
        settings: FactorRiskModelSettings,
        model_id: int | None = None,
        tqdm_progress: bool = False,
    ):
        self._client = client
        self._tasks_client = tasks_client
        self._settings = settings
        self._model_id = model_id
        self._tqdm_progress = tqdm_progress

    @property
    def settings(self) -> FactorRiskModelSettings:
        return self._settings

    async def get(self) -> AsyncFactorModelApi:
        task = await self.get_as_task()
        return await task.wait_result()

    async def get_as_task(self) -> AsyncTask[AsyncFactorModelApi]:
        params = {}
        if self._model_id is not None:
            params["model_id"] = self._model_id
        response = await self._client.post(
            "model", body=self._settings.model_dump(), params=params
        )

        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        self._model_id = response_model.extra["model_id"]
        return AsyncFactorModelTaskClient(
            api_client=self._tasks_client,
            task_id=response_model.task_id,
            model_id=self._model_id,
            settings=self._settings,
            factorrisk_client=self._client,
            tqdm_progress=self._tqdm_progress,
        )


class FactorModelLoaderClientImpl(FactorModelLoaderApi):

    def __init__(
        self, client: ApiClient, tasks_client: ApiClient, tqdm_progress: bool = False
    ):
        self._client = client.append_base_path("riskmodels")
        self._tasks_client = tasks_client
        self._tqdm_progress = tqdm_progress
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/factor-risk-model"),
            FactorRiskModelSettings,
            FactorRiskModelSettingsMenu,
        )
        self._universe_settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/universe"),
            UniverseSettings,
            UniverseSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[FactorRiskModelSettings, FactorRiskModelSettingsMenu]:
        return self._settings

    def load(
        self, ref_or_settings: str | int | FactorRiskModelSettings
    ) -> FactorModelEngineApi:
        if isinstance(ref_or_settings, FactorRiskModelSettings):
            settings = ref_or_settings
            if isinstance(settings.universe[0], UniverseSettings):
                dataset = settings.universe[0].dataset
            else:
                universe_settings = self._universe_settings.get(settings.universe[0])
                dataset = universe_settings.dataset
            settings_menu = self._settings.available_settings(dataset)
            settings_menu.validate_settings(settings)
            return FactorModelEngineClientImpl(
                self._client,
                self._tasks_client,
                settings,
                tqdm_progress=self._tqdm_progress,
            )
        else:
            ref = ref_or_settings
            settings_obj = self.settings.get(ref)
            if isinstance(ref, str):
                model_id = self.settings.names()[ref]
            else:
                model_id = ref
            return FactorModelEngineClientImpl(
                self._client,
                self._tasks_client,
                settings_obj,
                model_id,
                tqdm_progress=self._tqdm_progress,
            )


class AsyncFactorModelLoaderClientImpl(AsyncFactorModelLoaderApi):

    def __init__(
        self,
        client: AsyncApiClient,
        tasks_client: AsyncApiClient,
        tqdm_progress: bool = False,
    ):
        self._client = client.append_base_path("riskmodels")
        self._tasks_client = tasks_client
        self._tqdm_progress = tqdm_progress
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/factor-risk-model"),
            FactorRiskModelSettings,
            FactorRiskModelSettingsMenu,
        )
        self._universe_settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/universe"),
            UniverseSettings,
            UniverseSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[FactorRiskModelSettings, FactorRiskModelSettingsMenu]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | FactorRiskModelSettings
    ) -> AsyncFactorModelEngineApi:
        if isinstance(ref_or_settings, FactorRiskModelSettings):
            settings = ref_or_settings
            if isinstance(settings.universe[0], UniverseSettings):
                dataset = settings.universe[0].dataset
            else:
                universe_settings = await self._universe_settings.get(
                    settings.universe[0]
                )
                dataset = universe_settings.dataset

            settings_menu = await self._settings.available_settings(dataset)
            settings_menu.validate_settings(settings)
            return AsyncFactorModelEngineClientImpl(
                self._client,
                self._tasks_client,
                settings,
                tqdm_progress=self._tqdm_progress,
            )
        else:
            ref = ref_or_settings
            settings_obj = await self.settings.get(ref)
            if isinstance(ref, str):
                names = await self.settings.names()
                model_id = names[ref]
            else:
                model_id = ref
            return AsyncFactorModelEngineClientImpl(
                self._client,
                self._tasks_client,
                settings_obj,
                model_id,
                tqdm_progress=self._tqdm_progress,
            )
