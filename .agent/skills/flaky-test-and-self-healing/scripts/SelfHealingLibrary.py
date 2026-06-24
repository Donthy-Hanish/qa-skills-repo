import os
import json
import time
import re
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
try:
    from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
    from selenium.webdriver.common.by import By
except ImportError:
    # Fallbacks for validation environment
    class NoSuchElementException(Exception): pass
    class StaleElementReferenceException(Exception): pass
    class TimeoutException(Exception): pass
    class By:
        XPATH = "xpath"
        CSS_SELECTOR = "css"

class SelfHealingLibrary:
    """
    SelfHealingLibrary is a custom Robot Framework library designed to detect flaky locators,
    retry stale elements, and auto-heal locator failures using accessibility-first strategies.
    It strictly adheres to the Test Locator Standard.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self, report_path="./self_healing_report.json"):
        self.report_path = os.path.abspath(report_path)
        self.sel_lib = None
        self._load_or_init_report()

    def register_selenium_instance(self, selenium_instance=None):
        """
        Registers the active SeleniumLibrary instance.
        """
        if selenium_instance:
            self.sel_lib = selenium_instance
            logger.info("SelfHealingLibrary: SeleniumLibrary instance registered manually.")
        else:
            try:
                self.sel_lib = BuiltIn().get_library_instance('SeleniumLibrary')
                logger.info("SelfHealingLibrary: SeleniumLibrary instance auto-registered.")
            except Exception as e:
                logger.warn(f"SelfHealingLibrary: Could not auto-register SeleniumLibrary: {e}")

    @property
    def driver(self):
        if not self.sel_lib:
            self.register_selenium_instance()
        if not self.sel_lib or not hasattr(self.sel_lib, 'driver') or not self.sel_lib.driver:
            raise RuntimeError("SelfHealingLibrary: No active SeleniumLibrary driver found. Register Selenium Instance first.")
        return self.sel_lib.driver

    def _load_or_init_report(self):
        if not os.path.exists(self.report_path):
            with open(self.report_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def _log_healing_event(self, original_locator, healed_locator, context_html, url, healing_type="Locator Healing"):
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
        except Exception:
            report = []
            
        event = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "original_locator": original_locator,
            "healed_locator": healed_locator,
            "healing_type": healing_type,
            "context_html_snippet": context_html[:300],
            "status": "Suggested",
            "action_required": f"Update locator from '{original_locator}' to '{healed_locator}' in accordance with Test Locator Standard."
        }
        report.append(event)
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

    def parse_locator_hints(self, locator):
        """
        Parses locator string to extract attributes, tag names, or text hints.
        """
        hints = {"tag": None, "text": None, "id": None, "data_testid": None, "aria_label": None, "classes": []}
        
        # Strip selenium prefix if present
        clean_loc = locator
        if "=" in locator:
            parts = locator.split("=", 1)
            strategy, clean_loc = parts[0].strip().lower(), parts[1].strip()
        else:
            strategy = "default"

        # Check for CSS testid patterns e.g. [data-testid="submit-btn"]
        testid_match = re.search(r'\[data-testid=["\']([^"\']+)["\']\]', clean_loc)
        if testid_match:
            hints["data_testid"] = testid_match.group(1)
            
        qa_match = re.search(r'\[data-qa=["\']([^"\']+)["\']\]', clean_loc)
        if qa_match:
            hints["data_testid"] = qa_match.group(1)

        # Check for standard text or ID patterns
        if strategy == "id" or (strategy == "default" and not clean_loc.startswith(("/", "."))):
            hints["id"] = clean_loc
        elif "xpath" in strategy or clean_loc.startswith("//"):
            # Try to extract text from xpath
            text_match = re.search(r'text\(\)\s*=\s*["\']([^"\']+)["\']', clean_loc)
            if text_match:
                hints["text"] = text_match.group(1)
            tag_match = re.search(r'//([a-zA-Z0-9_*]+)', clean_loc)
            if tag_match:
                hints["tag"] = tag_match.group(1)
                
        return hints

    def smart_click(self, locator, timeout=5.0):
        """
        Attempts to click the locator. Automatically handles stale elements, retries,
        and triggers self-healing if not found.
        """
        logger.info(f"SelfHealingLibrary: Smart Click requested for '{locator}'")
        driver = self.driver
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                element = self._find_element_with_stale_retry(locator)
                if not element.is_enabled():
                    raise AssertionError(f"Element '{locator}' is found but is disabled (Functional Block). Refusing to over-heal.")
                
                element.click()
                logger.info(f"SelfHealingLibrary: Clicked '{locator}' successfully.")
                return
            except StaleElementReferenceException:
                logger.warn("SelfHealingLibrary: Stale element detected during click. Retrying...")
                time.sleep(0.5)
                continue
            except NoSuchElementException:
                # Primary locator failed, attempt healing
                healed_locator = self._attempt_self_healing(locator)
                if healed_locator:
                    logger.warn(f"SelfHealingLibrary: [HEALED] Original locator '{locator}' failed. Found replacement '{healed_locator}' using Test Locator Standard fallbacks.")
                    healed_element = driver.find_element(By.CSS_SELECTOR, healed_locator)
                    if not healed_element.is_enabled():
                        raise AssertionError(f"Healed element '{healed_locator}' is found but disabled. Refusing to click.")
                    healed_element.click()
                    return
                else:
                    raise NoSuchElementException(f"Element '{locator}' not found and self-healing could not locate any viable candidate.")
            except Exception as e:
                # Do not heal other exceptions (e.g. JavaScript click errors, user permissions, page load issues)
                raise e
        raise TimeoutException(f"Timed out trying to click '{locator}' after {timeout} seconds.")

    def smart_input_text(self, locator, text, timeout=5.0):
        """
        Input text resiliently, retrying on stale references and healing broken locators.
        """
        logger.info(f"SelfHealingLibrary: Smart Input Text requested for '{locator}'")
        driver = self.driver
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                element = self._find_element_with_stale_retry(locator)
                if not element.is_enabled() or element.get_attribute("readonly"):
                    raise AssertionError(f"Input '{locator}' is disabled or read-only (Functional Block). Refusing to over-heal.")
                
                element.clear()
                element.send_keys(text)
                logger.info(f"SelfHealingLibrary: Inputted text in '{locator}' successfully.")
                return
            except StaleElementReferenceException:
                logger.warn("SelfHealingLibrary: Stale element detected during input. Retrying...")
                time.sleep(0.5)
                continue
            except NoSuchElementException:
                healed_locator = self._attempt_self_healing(locator)
                if healed_locator:
                    logger.warn(f"SelfHealingLibrary: [HEALED] Original input locator '{locator}' failed. Using replacement '{healed_locator}'.")
                    healed_element = driver.find_element(By.CSS_SELECTOR, healed_locator)
                    if not healed_element.is_enabled():
                        raise AssertionError(f"Healed input '{healed_locator}' is disabled. Refusing to input.")
                    healed_element.clear()
                    healed_element.send_keys(text)
                    return
                else:
                    raise NoSuchElementException(f"Input field '{locator}' not found and self-healing failed.")
            except Exception as e:
                raise e
        raise TimeoutException(f"Timed out trying to input text in '{locator}' after {timeout} seconds.")

    def smart_wait_for_element(self, locator, timeout=10.0):
        """
        Resilient wait. If the original locator is missing, it polls and tries to heal it.
        """
        logger.info(f"SelfHealingLibrary: Resiliently waiting for '{locator}'")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                el = self._find_element_with_stale_retry(locator)
                if el:
                    return True
            except NoSuchElementException:
                # Check if we can heal
                healed = self._attempt_self_healing(locator, write_report=False)
                if healed:
                    logger.warn(f"SelfHealingLibrary: Element '{locator}' not found, but healed candidate '{healed}' is available.")
                    return True
                time.sleep(0.5)
        raise TimeoutException(f"Element '{locator}' was not visible/found within {timeout} seconds, and no healing candidates were detected.")

    def _find_element_with_stale_retry(self, locator, retries=3):
        """
        Retrieves element based on standard locator patterns, with stale-retries.
        """
        driver = self.driver
        strategy, value = self._parse_locator(locator)
        
        for attempt in range(retries):
            try:
                if strategy == "css":
                    return driver.find_element(By.CSS_SELECTOR, value)
                elif strategy == "xpath":
                    return driver.find_element(By.XPATH, value)
                elif strategy == "id":
                    return driver.find_element(By.ID, value)
                else:
                    # Fallback to general finding
                    return driver.find_element(By.XPATH, f"//*[@id='{locator}' or @name='{locator}']")
            except StaleElementReferenceException:
                if attempt == retries - 1:
                    raise
                time.sleep(0.2)
            except NoSuchElementException:
                raise

    def _parse_locator(self, locator):
        if "=" in locator:
            strategy, value = locator.split("=", 1)
            strategy = strategy.strip().lower()
            if strategy in ["css", "xpath", "id"]:
                return strategy, value.strip()
        
        # Auto-detect strategy
        loc_str = locator.strip()
        if loc_str.startswith("//") or loc_str.startswith("("):
            return "xpath", loc_str
        elif loc_str.startswith(".") or loc_str.startswith("#") or "[" in loc_str:
            return "css", loc_str
        return "id", loc_str

    def _attempt_self_healing(self, original_locator, write_report=True):
        """
        Executes accessibility-first fallback DOM scanning to identify replacement candidate.
        """
        driver = self.driver
        url = driver.current_url
        hints = self.parse_locator_hints(original_locator)
        
        # Scrape interactive elements from current DOM using high-speed JS snippet
        js_scraper = """
        const candidates = [];
        const elements = document.querySelectorAll("button, input, a, select, [role], [data-testid], [data-qa], [automation-id], [aria-label]");
        for (let i = 0; i < elements.length; i++) {
            const el = elements[i];
            candidates.push({
                tag: el.tagName.toLowerCase(),
                id: el.getAttribute("id") || "",
                testid: el.getAttribute("data-testid") || el.getAttribute("data-qa") || el.getAttribute("automation-id") || "",
                aria_label: el.getAttribute("aria-label") || "",
                role: el.getAttribute("role") || "",
                text: el.innerText || el.textContent || el.value || "",
                classes: el.className || "",
                outerHTML: el.outerHTML.substring(0, 300)
            });
        }
        return JSON.stringify(candidates);
        """
        try:
            raw_candidates = driver.execute_script(js_scraper)
            candidates = json.loads(raw_candidates)
        except Exception as e:
            logger.warn(f"SelfHealingLibrary: DOM Scraper execution failed: {e}")
            return None

        best_candidate = None
        best_score = 0.0
        
        for cand in candidates:
            score = 0.0
            # 1. Custom QA test attributes (data-testid) - Highest Weight
            if hints["data_testid"] and cand["testid"]:
                if hints["data_testid"] == cand["testid"]:
                    score += 100.0
                elif hints["data_testid"] in cand["testid"] or cand["testid"] in hints["data_testid"]:
                    score += 50.0
                    
            # 2. Match ID attribute (check for non-dynamic matching)
            if hints["id"] and cand["id"]:
                if hints["id"] == cand["id"]:
                    score += 80.0
                # Filter out dynamic framework-generated IDs (e.g. k-1234- or long numeric sequences)
                elif not re.search(r'\d{5,}', cand["id"]) and (hints["id"] in cand["id"] or cand["id"] in hints["id"]):
                    score += 30.0

            # 3. Match Text Content
            if hints["text"] and cand["text"]:
                cand_text = cand["text"].strip().lower()
                hint_text = hints["text"].strip().lower()
                if cand_text == hint_text:
                    score += 60.0
                elif hint_text in cand_text or cand_text in hint_text:
                    score += 30.0
            
            # 4. Role & accessibility label matches
            if hints["aria_label"] and cand["aria_label"]:
                if hints["aria_label"] == cand["aria_label"]:
                    score += 70.0
            
            # 5. Tag match boosting
            if hints["tag"] and cand["tag"] == hints["tag"].lower():
                score += 10.0
                
            if score > best_score:
                best_score = score
                best_candidate = cand

        # Threshold to verify similarity and avoid false match
        if best_candidate and best_score >= 40.0:
            # Construct healed locator following priority from Test Locator Standard
            healed_locator = None
            if best_candidate["testid"]:
                healed_locator = f"[data-testid='{best_candidate['testid']}']"
            elif best_candidate["aria_label"]:
                healed_locator = f"[aria-label='{best_candidate['aria_label']}']"
            elif best_candidate["id"] and not re.search(r'\d{5,}', best_candidate["id"]):
                healed_locator = f"#{best_candidate['id']}"
            elif best_candidate["text"]:
                # Escape single/double quotes in xpath visible text
                escaped_text = best_candidate["text"].replace("'", "\\'")
                healed_locator = f"xpath=//{best_candidate['tag']}[contains(text(), '{escaped_text}')]"
            else:
                healed_locator = f"css={best_candidate['tag']}.{best_candidate['classes'].replace(' ', '.')}"

            if healed_locator:
                if write_report:
                    self._log_healing_event(
                        original_locator=original_locator,
                        healed_locator=healed_locator,
                        context_html=best_candidate["outerHTML"],
                        url=url
                    )
                return healed_locator

        return None

# Self-test code to allow offline validation
if __name__ == "__main__":
    print("SelfHealingLibrary: Initializing offline self-test...")
    library = SelfHealingLibrary("./test_healing_report.json")
    test_loc = 'css=[data-testid="submit-btn"]'
    hints = library.parse_locator_hints(test_loc)
    print(f"Parsed Hints for '{test_loc}': {hints}")
    assert hints["data_testid"] == "submit-btn"
    print("Offline parsing validation: PASSED")
    if os.path.exists("./test_healing_report.json"):
        os.remove("./test_healing_report.json")
