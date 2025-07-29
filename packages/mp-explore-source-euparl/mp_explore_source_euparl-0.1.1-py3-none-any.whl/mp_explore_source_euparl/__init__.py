# SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mp_explore_core import DataSource, ModuleDescription, ModuleArgument, ModuleDefinition, ModuleMaintainer
from playwright.async_api import async_playwright
import pandas as pd

import xml.etree.ElementTree as ET
import subprocess
import logging
import os
import urllib.request

COMMITTEES = {
    "AFET": "Foreign Affairs",
    "DROI": "Human Rights",
    "SEDE": "Security and Defence",
    "DEVE": "Development",
    "INTA": "International Trade",
    "BUDG": "Budgets",
    "CONT": "Budgetary Control",
    "ECON": "Economic and Monetary Affairs",
    "FISC": "Tax Matters",
    "EMPL": "Employment and Social Affairs",
    "ENVI": "Environment, Climate and Food Safety",
    "SANT": "Public Health",
    "ITRE": "Industry, Research and Energy",
    "IMCO": "Internal Market and Consumer Protection",
    "TRAN": "Transport and Tourism",
    "REGI": "Regional Development",
    "AGRI": "Agriculture and Rural Development",
    "PECH": "Fisheries",
    "CULT": "Culture and Education",
    "JURI": "Legal Affairs",
    "LIBE": "Civil Liberties, Justice and Home Affairs",
    "AFCO": "Constitutional Affairs",
    "FEMM": "Women’s Rights and Gender Equality",
    "PETI": "Petitions",
    "EUDS": "European Democracy Shield",
    "HOUS": "Housing Crisis in the EU",
}

class EUParlSource(DataSource):
    def __init__(self, display_browser: bool = False, mep_url_template: str = "https://www.europarl.europa.eu/meps/en/{ID}", full_list_url: str = "https://www.europarl.europa.eu/meps/en/full-list/xml/", retrieve_emails: bool = False, retrieve_committees: bool = False, timeout: int = 400):
        """
        Retrieve the information of members from the EU parliament.

        :param bool display_browser: (Display browser) When enabled, a browser window is opened displaying the actions being performed.
        :param str mep_url_template: (MEP URL template) URL template to obtain data from each MEP, `{ID}` will be replaced with the MEP ID.
        :param str full_list_url: (Full list URL) URL from where the full list of MEPs is extracted.
        :param bool retrieve_emails: (Retrieve e-mails) When enabled, e-mails will be retrieved. This takes a long time.
        :param bool retrieve_committees: (Retrieve committees) When enabled, membership to committees will be retrieves. This takes a long time.
        :param int timeout: (Timeout) Only valid when `retrieve_emails` or `retrieve_committees` are true, time to wait between pages.
        """

        # See https://docs.python.org/3/library/urllib.request.html
        os.environ["no_proxy"] = "*"

        self.display_browser = display_browser
        self.full_list_url = full_list_url
        self.mep_url_template = mep_url_template
        self.retrieve_emails = retrieve_emails
        self.retrieve_committees = retrieve_committees
        self.timeout = timeout

    @staticmethod
    def metadata() -> ModuleDefinition:
        return ModuleDefinition({
            "name": "EU Parliament",
            "identifier": "euparl",
            "description": ModuleDescription.from_init(EUParlSource.__init__),
            "arguments": ModuleArgument.list_from_init(EUParlSource.__init__),
            "maintainers": [
                ModuleMaintainer({
                    "name": "Free Software Foundation Europe",
                    "email": "mp-explore@fsfe.org"
                }),
                ModuleMaintainer({
                    "name": "Sofía Aritz",
                    "email": "sofiaritz@fsfe.org"
                }),
            ],
        })
    
    async def fetch_data(self, logger: logging.Logger) -> pd.DataFrame:
        logger.warn("installing playwright browsers, if this fails try to run 'playwright install firefox --with-deps'")
        subprocess.run(["playwright", "install", "firefox"])

        response = urllib.request.urlopen(self.full_list_url).read()
        root = ET.fromstring(response)

        meps = []
        for mep in root:
            full_name = mep.find("fullName").text
            name = " ".join(filter(lambda x: x.isupper() is False, full_name.split(" ")))
            surname = " ".join(filter(lambda x: x.isupper(), full_name.split(" ")))
            mep_id = mep.find("id").text

            logger.debug(f"[Phase 0: Basic data] Current MEP: {name} {surname} ({mep_id})")
            meps.append({
                "Euparl ID": mep_id,
                "Name": name,
                "Surname": surname,
                "Country": mep.find("country").text,
                "EU Group": mep.find("politicalGroup").text,
                "National Group": mep.find("nationalPoliticalGroup").text,
            })

        if self.retrieve_committees is True or self.retrieve_emails is True:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=self.display_browser is False)
                page = await browser.new_page()

                for i, mep in enumerate(meps):
                    logger.debug(f"[Phase 1: Committees + Contact] Current MEP: {mep['Name']} {mep['Surname']} ({mep['Euparl ID']})")
                    await page.goto(self.mep_url_template.replace("{ID}", mep["Euparl ID"]))
                    await page.wait_for_load_state()

                    if self.retrieve_emails:
                        logger.debug("> Retrieving contact information")
                        email = await page.evaluate("""() => {
                            let share = document.getElementsByClassName("erpl_social-share-horizontal")[0]
                            return share.getElementsByClassName("link_email")[0]?.href.replace("mailto:", "").trim()
                        }""")

                        meps[i]["Email"] = email

                    if self.retrieve_committees:
                        logger.debug("> Retrieving committee information")
                        committees = await page.evaluate("""() => {
                            let values = {}
                            
                            let status = Array.from(document.getElementsByClassName("erpl_meps-status"))
                            for (const item of status) {
                                let title = item.children[0].innerText
                                let committees = Array.from(item.getElementsByClassName("erpl_badge-committee"))
                                for (const committee of committees) {
                                    values["Committee " + committee.innerText] = title
                                }
                            }

                            return values
                        }""")

                        committees = dict(filter(lambda x: x[0].replace("Committee", "").strip() in COMMITTEES.keys(), committees.items()))

                        meps[i] = mep | committees

                    mep_full_name = meps[i]["Name"] + " " + meps[i]["Surname"]
                    logger.debug(f"finished retrieving {mep_full_name}'s page and data")

                    await page.wait_for_timeout(self.timeout)

        return pd.DataFrame.from_dict(meps)