"""Utility helpers for automated website testing using Selenium."""

from __future__ import annotations

from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

DEFAULT_BROWSER = "chrome"


def get_driver(*, browser: str = DEFAULT_BROWSER, headless: bool = True):
    """Return a Selenium WebDriver instance.

    :param browser: Browser backend to use (``"chrome"`` or ``"firefox"``).
    :type browser: str
    :param headless: Launch the browser without a visible window.
    :type headless: bool
    :returns: Configured Selenium WebDriver.
    :rtype: selenium.webdriver.Remote
    :provides: selenium.webdriver.Remote
    """
    browser = browser.lower()
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")


_active_driver = None
_active_config: tuple[str, bool] | None = None


@contextmanager
def browse(
    *,
    url: str | None = None,
    browser: str = DEFAULT_BROWSER,
    headless: bool = True,
    driver=None,
    close: bool = False,
):
    """Context manager that yields a cached WebDriver.

    :param url: Optional URL to open before yielding the driver.
    :type url: str | None
    :param browser: Browser backend to use.
    :type browser: str
    :param headless: Whether to run in headless mode.
    :type headless: bool
    :param driver: Existing driver object or sequence containing one.
    :type driver: selenium.webdriver.Remote | iterable | None
    :param close: If ``True`` the provided driver is closed and ``None`` yielded.
    :type close: bool
    :returns: Active WebDriver instance.
    :rtype: selenium.webdriver.Remote
    """
    global _active_driver, _active_config

    # Try to unwrap an existing driver from the given object (tuple/list etc)
    try:
        match driver:
            case webdriver.Remote() as d:
                driver = d
            case list() | tuple() as seq:
                driver = next((x for x in seq if isinstance(x, webdriver.Remote)), None)
            case None:
                driver = None
            case _ if isinstance(driver, webdriver.Remote):
                pass
            case _ if hasattr(driver, "__iter__") and not isinstance(driver, (str, bytes, bytearray)):
                driver = next((x for x in driver if isinstance(x, webdriver.Remote)), None)
            case _:
                driver = None
    except Exception:
        pass

    if close:
        target = driver or _active_driver
        if target:
            try:
                target.quit()
            except Exception:
                pass
            if target is _active_driver:
                _active_driver = None
                _active_config = None
        yield None
        return

    desired_cfg = (browser.lower(), bool(headless))

    if driver:
        _active_driver = driver
        _active_config = desired_cfg
    else:
        if (
            _active_driver is None
            or _active_config != desired_cfg
            or getattr(_active_driver, "service", None) is None
        ):
            if _active_driver:
                try:
                    _active_driver.quit()
                except Exception:
                    pass
            _active_driver = get_driver(browser=browser, headless=headless)
            _active_config = desired_cfg

    if url:
        _active_driver.get(url)

    try:
        yield _active_driver
    finally:
        # Do not quit driver here; it can be reused. Call with driver=None
        # and contradictory params to force recreation.
        pass


def capture_page_source(
    url: str,
    *,
    browser_name: str = DEFAULT_BROWSER,
    headless: bool = True,
    wait: float = 2.0,
    screenshot: str | None = None,
) -> str:
    """Return page source for ``url``.

    :param url: Page URL to fetch.
    :type url: str
    :param browser_name: Browser backend to use.
    :type browser_name: str
    :param headless: Whether to run in headless mode.
    :type headless: bool
    :param wait: Seconds to wait after navigation.
    :type wait: float
    :param screenshot: Optional path for a screenshot of the page.
    :type screenshot: str | None
    :returns: HTML source of the page.
    :rtype: str
    """
    import time

    with browse(url=url, browser=browser_name, headless=headless) as drv:
        if wait:
            time.sleep(wait)
        if screenshot:
            drv.save_screenshot(screenshot)
        return drv.page_source
