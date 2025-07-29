from __future__ import absolute_import, division, print_function

from typing import TYPE_CHECKING

from .schema import (
    CheckSettings,
    CloseBatchSettings,
    CloseSettings,
    DeleteTestSettings,
    ECClientSettings,
    ExtractTextSettings,
    EyesConfig,
    ImageTarget,
    LocateSettings,
    OCRSearchSettings,
    OpenSettings,
    Size,
)

if TYPE_CHECKING:
    from typing import List, Tuple

    from .. import common
    from . import config as cfg
    from . import ec_client_settings, extract_text, locators
    from . import target as t
    from .batch_close import _EnabledBatchClose  # noqa
    from .fluent import selenium_check_settings as cs
    from .object_registry import ObjectRegistry
    from .optional_deps import WebDriver
    from .utils.custom_types import ViewPort


class Marshaller(object):
    def __init__(self, object_registry):
        # type: (ObjectRegistry) -> None
        self._object_registry = object_registry
        self._sa = dict(context={"registry": object_registry})

    def marshal_viewport_size(self, viewport_size):
        # type: (ViewPort) -> dict
        return Size(**self._sa).dump(viewport_size)

    def marshal_webdriver_ref(self, driver):
        # type: (WebDriver) -> dict
        return self._object_registry.marshal_driver(driver)

    def marshal_ec_client_settings(self, client_settings):
        # type: (ec_client_settings.ECClientSettings) -> dict
        return ECClientSettings().dump(client_settings)

    def marshal_enabled_batch_close(self, close_batches):
        # type: (_EnabledBatchClose) -> dict
        return CloseBatchSettings(**self._sa).dump(close_batches)

    def marshal_delete_test_settings(self, test_results):
        # type: (common.TestResults) -> dict
        return DeleteTestSettings(**self._sa).dump(test_results)

    def marshal_configuration(self, configuration):
        # type: (cfg.Configuration) -> dict
        open = OpenSettings(**self._sa).dump(configuration)
        config = EyesConfig(**self._sa).dump(configuration)
        close = CloseSettings(**self._sa).dump(configuration)
        return {"open": open, "screenshot": config, "check": config, "close": close}

    def marshal_check_settings(self, check_settings):
        # type: (cs.SeleniumCheckSettings) -> dict
        return CheckSettings(**self._sa).dump(check_settings.values)

    def marshal_image_target(self, image_target):
        # type: (t.ImageTarget) -> dict
        return ImageTarget(**self._sa).dump(image_target)

    def marshal_locate_settings(self, locate_settings):
        # type: (locators.VisualLocatorSettings) -> dict
        return LocateSettings(**self._sa).dump(locate_settings.values)

    def marshal_ocr_extract_settings(self, extract_settings):
        # type: (Tuple[extract_text.OCRRegion, ...]) -> List[dict]
        return [ExtractTextSettings(**self._sa).dump(s) for s in extract_settings]

    def marshal_ocr_search_settings(self, search_settings):
        # type: (extract_text.TextRegionSettings) -> dict
        return OCRSearchSettings(**self._sa).dump(search_settings)
