import datetime as dt
import io
from typing import Any, Sequence

import polars as pl
from bayesline.api import (
    AsyncReadOnlyRegistry,
    AsyncSettingsRegistry,
    AsyncTask,
    EmptySettingsMenu,
    ReadOnlyRegistry,
    SettingsRegistry,
    Task,
    TaskResponse,
)
from bayesline.api.equity import (
    AsyncPortfolioHierarchyLoaderApi,
    AsyncReportAccessorApi,
    AsyncReportApi,
    AsyncReportLoaderApi,
    AsyncReportPersister,
    IllegalPathError,
    PortfolioHierarchyLoaderApi,
    PortfolioHierarchySettings,
    ReportAccessorApi,
    ReportAccessorSettings,
    ReportApi,
    ReportLoaderApi,
    ReportPersister,
    ReportSettings,
    ReportSettingsMenu,
)
from bayesline.api.types import (
    DateLike,
    DNFFilterExpressions,
    to_date,
    to_maybe_date_string,
)

from bayesline.apiclient._src.client import ApiClient, AsyncApiClient
from bayesline.apiclient._src.settings import (
    AsyncHttpSettingsRegistryClient,
    HttpSettingsRegistryClient,
)
from bayesline.apiclient._src.tasks import AsyncTaskClient, TaskClient


def _make_params_dict(**kwargs: Any) -> dict[str, Any]:
    """Remove None values from kwargs and return as dict."""
    return {k: v for k, v in kwargs.items() if v is not None}


class ReportAccessorClientImpl(ReportAccessorApi):

    def __init__(
        self,
        client: ApiClient,
        identifier: int,
        settings: ReportAccessorSettings,
        persister: ReportPersister,
    ) -> None:
        self._client = client
        self._identifier = identifier
        self._settings = settings
        self._persister = persister

    @property
    def identifier(self) -> int:
        return self._identifier

    @property
    def axes(self) -> dict[str, list[str]]:
        return self._settings.axes

    @property
    def metric_cols(self) -> list[str]:
        return self._settings.metric_cols

    @property
    def pivot_cols(self) -> list[str]:
        return self._settings.pivot_cols

    def get_level_values(
        self,
        levels: tuple[str, ...] = (),
        include_totals: bool = False,
        filters: DNFFilterExpressions | None = None,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/levels"
        response = self._client.post(
            url,
            body={
                "levels": levels,
                "include_totals": include_totals,
                "filters": filters,
                "axes": self._settings.axes,
                "metric_cols": self._settings.metric_cols,
            },
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get levels {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    def get_data(
        self,
        path: list[tuple[str, str]],
        *,
        expand: tuple[str, ...] = (),
        pivot_cols: tuple[str, ...] = (),
        value_cols: tuple[str, ...] = (),
        filters: DNFFilterExpressions | None = None,
        pivot_total: bool = False,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/data"
        response = self._client.post(
            url,
            body={
                "path": path,
                "expand": expand,
                "pivot_cols": pivot_cols,
                "value_cols": value_cols,
                "filters": filters,
                "pivot_total": pivot_total,
            },
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get report {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    def persist(self, name: str) -> int:
        return self._persister.persist(name, self._settings, [self])


class AsyncReportAccessorClientImpl(AsyncReportAccessorApi):

    def __init__(
        self,
        client: AsyncApiClient,
        identifier: int,
        settings: ReportAccessorSettings,
        persister: AsyncReportPersister,
    ) -> None:
        self._client = client
        self._identifier = identifier
        self._settings = settings
        self._persister = persister

    @property
    def identifier(self) -> int:
        return self._identifier

    @property
    def axes(self) -> dict[str, list[str]]:
        return self._settings.axes

    @property
    def metric_cols(self) -> list[str]:
        return self._settings.metric_cols

    @property
    def pivot_cols(self) -> list[str]:
        return self._settings.pivot_cols

    async def get_level_values(
        self,
        levels: tuple[str, ...] = (),
        include_totals: bool = False,
        filters: DNFFilterExpressions | None = None,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/levels"
        response = await self._client.post(
            url,
            body={
                "levels": levels,
                "include_totals": include_totals,
                "filters": filters,
                "axes": self._settings.axes,
                "metric_cols": self._settings.metric_cols,
            },
        )

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get levels {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    async def get_data(
        self,
        path: list[tuple[str, str]],
        *,
        expand: tuple[str, ...] = (),
        pivot_cols: tuple[str, ...] = (),
        value_cols: tuple[str, ...] = (),
        filters: DNFFilterExpressions | None = None,
        pivot_total: bool = False,
    ) -> pl.DataFrame:
        url = f"accessor/{self._identifier}/data"
        response = await self._client.post(
            url,
            body={
                "path": path,
                "expand": expand,
                "pivot_cols": pivot_cols,
                "value_cols": value_cols,
                "filters": filters,
                "pivot_total": pivot_total,
            },
        )

        if response.status_code == 400:
            raise IllegalPathError(response.json()["detail"])

        try:
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"could not get report {(response.json())}") from e

        return pl.read_parquet(io.BytesIO(response.content))

    async def persist(self, name: str) -> int:
        return await self._persister.persist(name, self._settings, [self])


class ReportAccessorTaskClient(TaskClient[ReportAccessorApi]):
    def __init__(
        self,
        *,
        api_client: ApiClient,
        task_id: str,
        tqdm_progress: bool,
        report_client: ApiClient,
        persister: ReportPersister,
    ) -> None:
        super().__init__(
            client=api_client, task_id=task_id, tqdm_progress=tqdm_progress
        )
        self._report_client = report_client
        self._persister = persister

    def get_result(self) -> ReportAccessorApi:
        response = self._api_client.get(
            f"{self.task_id}/result", params={"type": "json"}
        )
        self.raise_for_status(response)

        accessor_description = response.json()
        return ReportAccessorClientImpl(
            self._report_client,
            accessor_description["identifier"],
            ReportAccessorSettings(
                axes=accessor_description["axes"],
                metric_cols=accessor_description["metric_cols"],
                pivot_cols=accessor_description["pivot_cols"],
            ),
            persister=self._persister,
        )


class AsyncReportAccessorTaskClient(AsyncTaskClient[AsyncReportAccessorApi]):
    def __init__(
        self,
        *,
        api_client: AsyncApiClient,
        task_id: str,
        tqdm_progress: bool,
        report_client: AsyncApiClient,
        persister: AsyncReportPersister,
    ) -> None:
        super().__init__(
            client=api_client, task_id=task_id, tqdm_progress=tqdm_progress
        )
        self._report_client = report_client
        self._persister = persister

    async def get_result(self) -> AsyncReportAccessorApi:
        response = await self._api_client.get(
            f"{self.task_id}/result", params={"type": "json"}
        )

        self.raise_for_status(response)

        accessor_description = response.json()

        return AsyncReportAccessorClientImpl(
            self._report_client,
            accessor_description["identifier"],
            ReportAccessorSettings(
                axes=accessor_description["axes"],
                metric_cols=accessor_description["metric_cols"],
                pivot_cols=accessor_description["pivot_cols"],
            ),
            persister=self._persister,
        )


class ReportClientImpl(ReportApi):

    def __init__(
        self,
        client: ApiClient,
        tasks_client: ApiClient,
        report_id: str,
        settings: ReportSettings,
        persister: ReportPersister,
        tqdm_progress: bool,
    ):
        self._client = client
        self._tasks_client = tasks_client
        self._report_id = report_id
        self._settings = settings
        self._persister = persister
        self._tqdm_progress = tqdm_progress

    @property
    def settings(self) -> ReportSettings:
        return self._settings

    def get_report(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
    ) -> ReportAccessorApi:
        task = self.get_report_as_task(
            order,
            date=date,
            date_start=date_start,
            date_end=date_end,
            subtotals=subtotals,
        )
        return task.wait_result()

    def get_report_as_task(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
    ) -> Task[ReportAccessorApi]:
        url = self._report_id
        response = self._client.post(
            url,
            body={"order": order},
            params=_make_params_dict(
                date=to_maybe_date_string(date),
                date_start=to_maybe_date_string(date_start),
                date_end=to_maybe_date_string(date_end),
                subtotals=subtotals,
            ),
        )

        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return ReportAccessorTaskClient(
            api_client=self._tasks_client,
            task_id=response_model.task_id,
            tqdm_progress=self._tqdm_progress,
            report_client=self._client,
            persister=self._persister,
        )

    def dates(self) -> list[dt.date]:
        response = self._client.get(f"{self._report_id}/dates")
        return [to_date(d) for d in response.json()]


class AsyncReportClientImpl(AsyncReportApi):

    def __init__(
        self,
        client: AsyncApiClient,
        tasks_client: AsyncApiClient,
        report_id: str,
        settings: ReportSettings,
        persister: AsyncReportPersister,
        tqdm_progress: bool,
    ):
        self._client = client
        self._tasks_client = tasks_client
        self._report_id = report_id
        self._settings = settings
        self._persister = persister
        self._tqdm_progress = tqdm_progress

    @property
    def settings(self) -> ReportSettings:
        return self._settings

    async def get_report(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
    ) -> AsyncReportAccessorApi:
        task = await self.get_report_as_task(
            order,
            date=date,
            date_start=date_start,
            date_end=date_end,
            subtotals=subtotals,
        )
        return await task.wait_result()

    async def get_report_as_task(
        self,
        order: dict[str, list[str]],
        *,
        date: DateLike | None = None,
        date_start: DateLike | None = None,
        date_end: DateLike | None = None,
        subtotals: list[str] | None = None,
    ) -> AsyncTask[AsyncReportAccessorApi]:
        url = self._report_id
        response = await self._client.post(
            url,
            body={"order": order},
            params=_make_params_dict(
                date=to_maybe_date_string(date),
                date_start=to_maybe_date_string(date_start),
                date_end=to_maybe_date_string(date_end),
                subtotals=subtotals,
            ),
        )

        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncReportAccessorTaskClient(
            api_client=self._tasks_client,
            task_id=response_model.task_id,
            tqdm_progress=self._tqdm_progress,
            report_client=self._client,
            persister=self._persister,
        )

    async def dates(self) -> list[dt.date]:
        response = await self._client.get(f"{self._report_id}/dates")
        return [to_date(d) for d in response.json()]


class ReportLoaderTaskClient(TaskClient[ReportApi]):

    def __init__(
        self,
        *,
        api_client: ApiClient,
        task_id: str,
        tqdm_progress: bool,
        settings: ReportSettings,
        report_client: ApiClient,
        persister: ReportPersister,
    ):
        super().__init__(
            client=api_client, task_id=task_id, tqdm_progress=tqdm_progress
        )
        self._settings = settings
        self._report_client = report_client
        self._persister = persister

    def get_result(self) -> ReportApi:
        response = self._api_client.get(
            f"{self.task_id}/result", params={"type": "json"}
        )
        if response.status_code == 404:
            raise KeyError(f"Task {self.task_id} not found")
        self.raise_for_status(response)
        report_id = response.json()["report_id"]
        return ReportClientImpl(
            self._report_client,
            self._api_client,
            report_id,
            self._settings,
            persister=self._persister,
            tqdm_progress=self._tqdm_progress,
        )


class AsyncReportLoaderTaskClient(AsyncTaskClient[AsyncReportApi]):

    def __init__(
        self,
        *,
        api_client: AsyncApiClient,
        task_id: str,
        tqdm_progress: bool,
        settings: ReportSettings,
        report_client: AsyncApiClient,
        persister: AsyncReportPersister,
    ):
        super().__init__(
            client=api_client, task_id=task_id, tqdm_progress=tqdm_progress
        )
        self._settings = settings
        self._report_client = report_client
        self._persister = persister

    async def get_result(self) -> AsyncReportApi:
        response = await self._api_client.get(
            f"{self._task_id}/result", params={"type": "json"}
        )
        if response.status_code == 404:
            raise KeyError(f"Task {self.task_id} not found")
        self.raise_for_status(response)
        report_id = response.json()["report_id"]
        return AsyncReportClientImpl(
            self._report_client,
            self._api_client,
            report_id,
            self._settings,
            persister=self._persister,
            tqdm_progress=self._tqdm_progress,
        )


class ReportLoaderClientImpl(ReportLoaderApi):
    def __init__(
        self,
        client: ApiClient,
        tasks_client: ApiClient,
        portfoliohierarchy_api: PortfolioHierarchyLoaderApi,
        persister: ReportPersister | None = None,
        tqdm_progress: bool = False,
    ):
        self._client = client.append_base_path("portfolioreport")
        self._tasks_client = tasks_client
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/report"),
            ReportSettings,
            ReportSettingsMenu,
        )
        self._accessor_settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/report-accessor"),
            ReportAccessorSettings,
            EmptySettingsMenu,
        )
        self._portfoliohierarchy_api = portfoliohierarchy_api
        self._persister = persister or ReportPersisterClient(client)
        self._tqdm_progress = tqdm_progress

    @property
    def persister(self) -> ReportPersister:
        return self._persister

    @property
    def settings(
        self,
    ) -> SettingsRegistry[ReportSettings, ReportSettingsMenu]:
        return self._settings

    def load(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
    ) -> ReportApi:
        return self.load_as_task(
            ref_or_settings,
            hierarchy_ref_or_settings=hierarchy_ref_or_settings,
        ).wait_result()

    def load_as_task(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
    ) -> Task[ReportApi]:
        if isinstance(ref_or_settings, ReportSettings):
            settings = ref_or_settings
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(settings)
        else:
            ref = ref_or_settings
            settings = self.settings.get(ref)

        hierarchy: PortfolioHierarchySettings | None = None
        if hierarchy_ref_or_settings is not None:
            if isinstance(hierarchy_ref_or_settings, PortfolioHierarchySettings):
                hierarchy = hierarchy_ref_or_settings
            else:
                hierarchy = (
                    self._portfoliohierarchy_api.load(hierarchy_ref_or_settings)
                ).settings

        params: dict[str, Any | None] = {
            "settings": settings.model_dump(),
            "hierarchy": None,
        }

        if hierarchy:
            params["hierarchy"] = hierarchy.model_dump()

        response = self._client.post("", body=params)

        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return ReportLoaderTaskClient(
            api_client=self._tasks_client,
            task_id=response_model.task_id,
            tqdm_progress=self._tqdm_progress,
            settings=settings,
            report_client=self._client,
            persister=self._persister,
        )

    @property
    def persisted_report_settings(
        self,
    ) -> ReadOnlyRegistry[ReportAccessorSettings]:
        return self._accessor_settings

    def load_persisted(self, name_or_id: str | int) -> ReportAccessorApi:
        return self._persister.load_persisted(name_or_id)

    def delete_persisted(self, name_or_id: list[str | int]) -> None:
        self._persister.delete_persisted(name_or_id)


class AsyncReportLoaderClientImpl(AsyncReportLoaderApi):
    def __init__(
        self,
        client: AsyncApiClient,
        tasks_client: AsyncApiClient,
        portfoliohierarchy_api: AsyncPortfolioHierarchyLoaderApi,
        persister: AsyncReportPersister | None = None,
        tqdm_progress: bool = False,
    ):
        self._client = client.append_base_path("portfolioreport")
        self._tasks_client = tasks_client
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/report"),
            ReportSettings,
            ReportSettingsMenu,
        )
        self._accessor_settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/report-accessor"),
            ReportAccessorSettings,
            EmptySettingsMenu,
        )
        self._portfoliohierarchy_api = portfoliohierarchy_api
        self._persister = persister or AsyncReportPersisterClient(client)
        self._tqdm_progress = tqdm_progress

    @property
    def persister(self) -> AsyncReportPersister:
        return self._persister

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[ReportSettings, ReportSettingsMenu]:
        return self._settings

    async def load(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
        dates: list[DateLike] | tuple[DateLike, DateLike] | None = None,
    ) -> AsyncReportApi:
        task = await self.load_as_task(
            ref_or_settings,
            hierarchy_ref_or_settings=hierarchy_ref_or_settings,
            dates=dates,
        )
        return await task.wait_result()

    async def load_as_task(
        self,
        ref_or_settings: str | int | ReportSettings,
        *,
        hierarchy_ref_or_settings: str | int | PortfolioHierarchySettings | None = None,
        dates: list[DateLike] | tuple[DateLike, DateLike] | None = None,
    ) -> AsyncTask[AsyncReportApi]:
        if isinstance(ref_or_settings, ReportSettings):
            settings = ref_or_settings
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(settings)
        else:
            ref = ref_or_settings
            settings = await self.settings.get(ref)

        hierarchy: PortfolioHierarchySettings | None = None
        if hierarchy_ref_or_settings is not None:
            if isinstance(hierarchy_ref_or_settings, PortfolioHierarchySettings):
                hierarchy = hierarchy_ref_or_settings
            else:
                hierarchy = (
                    await self._portfoliohierarchy_api.load(hierarchy_ref_or_settings)
                ).settings

        params: dict[str, Any | None] = {
            "settings": settings.model_dump(),
            "hierarchy": None,
        }

        if hierarchy:
            params["hierarchy"] = hierarchy.model_dump()

        response = await self._client.post("", body=params)

        if response.status_code != 202:
            try:
                response.raise_for_status()
            except Exception as e:
                raise Exception(f"Failed to create task: {response.json()}") from e

        response_model = TaskResponse.model_validate(response.json())
        return AsyncReportLoaderTaskClient(
            api_client=self._tasks_client,
            task_id=response_model.task_id,
            tqdm_progress=self._tqdm_progress,
            settings=settings,
            report_client=self._client,
            persister=self._persister,
        )

    @property
    def persisted_report_settings(
        self,
    ) -> AsyncReadOnlyRegistry[ReportAccessorSettings]:
        return self._accessor_settings

    async def load_persisted(self, name_or_id: str | int) -> AsyncReportAccessorApi:
        return await self._persister.load_persisted(name_or_id)

    async def delete_persisted(self, name_or_id: list[str | int]) -> None:
        await self._persister.delete_persisted(name_or_id)


class AsyncReportPersisterClient(AsyncReportPersister):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("portfolioreport")
        self._settings_client = client.append_base_path("settings/report-accessor")

    async def persist(
        self,
        name: str,
        settings: ReportAccessorSettings,
        accessors: Sequence[AsyncReportAccessorApi],
    ) -> int:
        body = {
            "settings": settings.model_dump(),
            "accessor_identifiers": [a.identifier for a in accessors],  # type: ignore
        }
        response = await self._client.post(f"accessor/{name}", body=body)
        response.raise_for_status()
        return response.json()["id"]

    async def load_persisted(self, name_or_id: str | int) -> AsyncReportAccessorApi:
        accessor_settings = AsyncHttpSettingsRegistryClient(
            self._settings_client,
            ReportAccessorSettings,
            EmptySettingsMenu,
        )
        settings = await accessor_settings.get(name_or_id)

        identifier: int
        if isinstance(name_or_id, str):
            identifier = (await accessor_settings.names())[name_or_id]
        else:
            identifier = name_or_id

        return AsyncReportAccessorClientImpl(
            self._client, identifier, settings, persister=self
        )

    async def delete_persisted(self, name_or_id: list[str | int]) -> None:
        names: list[str] = []
        ids: list[int] = []
        for e in name_or_id:
            if isinstance(e, int):
                ids.append(e)
            else:
                names.append(e)
        params = {"name": names, "id": ids}
        result = await self._client.delete("accessor", params=params)
        result.raise_for_status()


class ReportPersisterClient(ReportPersister):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("portfolioreport")
        self._settings_client = client.append_base_path("settings/report-accessor")

    def persist(
        self,
        name: str,
        settings: ReportAccessorSettings,
        accessors: Sequence[ReportAccessorApi],
    ) -> int:
        body = {
            "settings": settings.model_dump(),
            "accessor_identifiers": [a.identifier for a in accessors],  # type: ignore
        }
        response = self._client.post(f"accessor/{name}", body=body)
        response.raise_for_status()
        return response.json()["id"]

    def load_persisted(self, name_or_id: str | int) -> ReportAccessorApi:
        accessor_settings = HttpSettingsRegistryClient(
            self._settings_client,
            ReportAccessorSettings,
            EmptySettingsMenu,
        )
        settings = accessor_settings.get(name_or_id)
        identifier: int
        if isinstance(name_or_id, str):
            identifier = (accessor_settings.names())[name_or_id]
        else:
            identifier = name_or_id

        return ReportAccessorClientImpl(
            self._client, identifier, settings, persister=self
        )

    def delete_persisted(self, name_or_id: list[str | int]) -> None:
        names: list[str] = []
        ids: list[int] = []
        for e in name_or_id:
            if isinstance(e, int):
                ids.append(e)
            else:
                names.append(e)
        params = {"names": names, "ids": ids}
        result = self._client.delete("accessor", params=params)
        result.raise_for_status()
