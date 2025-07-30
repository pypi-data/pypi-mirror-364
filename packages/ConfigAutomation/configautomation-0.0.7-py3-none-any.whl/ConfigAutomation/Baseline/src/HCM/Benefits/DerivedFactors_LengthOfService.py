from playwright.sync_api import Playwright, sync_playwright, expect
from ConfigAutomation.Baseline.src.utils import *


def configure(playwright: Playwright, rowcount, datadict, videodir) -> dict:
    browser, context, page = OpenBrowser(playwright, False, videodir)
    page.goto(BASEURL)

    # Login to application
    page.wait_for_timeout(5000)
    if page.get_by_placeholder("User ID").is_visible():
        page.get_by_placeholder("User ID").click()
        page.get_by_placeholder("User ID").fill(IMPLUSRID)
        page.get_by_placeholder("Password").fill(IMPLUSRPWD)
    else:
        page.get_by_placeholder("User name").click()
        page.get_by_placeholder("User name").fill(IMPLUSRID)
        page.get_by_role("textbox", name="Password").fill(IMPLUSRPWD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(5000)

    # Navigate to Derived Factors page
    page.get_by_role("link", name="Navigator").click()
    page.get_by_title("Benefits Administration", exact=True).click()
    page.get_by_role("link", name="Plan Configuration").click()
    page.wait_for_timeout(5000)
    page.get_by_role("link", name="Tasks").click()
    page.wait_for_timeout(5000)
    page.get_by_role("link", name="Derived Factors").click()
    page.get_by_role("link", name="Length of Service", exact=True).click()

    i = 0
    while i < rowcount:
        datadictvalue = datadict[i]
        print(i)
        page.wait_for_timeout(3000)
        page.get_by_role("button", name="Create", exact=True).click()
        page.wait_for_timeout(3000)

        # Entering Name
        page.locator("//div[text()='Create Derived Factor Length of Service']//following::label[text()='Name']//following::input[1]").type(datadictvalue["C_NAME"])

        # Unit of Measure
        if datadictvalue["C_UNIT_OF_MSR"]!='':
            page.get_by_role("combobox", name="Unit of Measure").click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_UNIT_OF_MSR"], exact=True).click()

        # Greater than or Equal to Length of Service
        if datadictvalue["C_GRTR_THAN_OR_EQUAL_TO_LNGTH_OF_SRVC"]!='':
            page.get_by_label("Greater than or Equal to").clear()
            page.get_by_label("Greater than or Equal to").fill(str(datadictvalue["C_GRTR_THAN_OR_EQUAL_TO_LNGTH_OF_SRVC"]))

        # Less Than Length of Service
        if datadictvalue["C_LESS_THAN_LNGTH_OF_SRVC"] != '':
            page.get_by_label("Less Than Length of Service").clear()
            page.get_by_label("Less Than Length of Service").fill(str(datadictvalue["C_LESS_THAN_LNGTH_OF_SRVC"]))

        # Period Start Date Rule
        if datadictvalue["C_PRD_START_DATE"] != '':
            page.get_by_role("combobox", name="Period Start Date Rule").click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_PRD_START_DATE"], exact=True).click()

        # Determination Rule
        if datadictvalue["C_DTRMNTN_RULE"] != '':
            page.get_by_role("combobox", name="Determination Rule").click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_DTRMNTN_RULE"], exact=True).click()

        # Rounding Rule
        if datadictvalue["C_RNDNG_RULE"] != '':
            page.get_by_role("combobox", name="Rounding Rule").click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_RNDNG_RULE"], exact=True).click()
        page.pause()
        page.get_by_role("button", name="Save and Close").click()
        page.wait_for_timeout(2000)
        try:
            expect(page.get_by_role("heading", name="Derived Factors")).to_be_visible()
            page.wait_for_timeout(3000)
            print("Derived Factor LOS Created Successfully")
            datadictvalue["RowStatus"] = "Derived Factor LOS Created Successfully"
        except Exception as e:
            print("Unable to Create Derived Factor LOS")
            datadictvalue["RowStatus"] = "Unable to Save Derived Factor LOS"

        i = i + 1

    OraSignOut(page, context, browser, videodir)
    return datadict


# ****** Execution Starts Here ******
print("Process Started At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
if CheckWrkbkForProcessing(SOURCE_DIR_PATH + BENEFITS_CONFIG_WRKBK, DERIVEDFACTORS_LOS):
    CreateWrkbkForProcessing(SOURCE_DIR_PATH + BENEFITS_CONFIG_WRKBK, DERIVEDFACTORS_LOS,PRCS_DIR_PATH + BENEFITS_CONFIG_WRKBK)
    rows, cols, datadictwrkbk = ImportWrkbk(PRCS_DIR_PATH + BENEFITS_CONFIG_WRKBK, DERIVEDFACTORS_LOS)
    if rows > 0:
        with sync_playwright() as pw:
            output = configure(pw, rows, datadictwrkbk, VIDEO_DIR_PATH + re.split(".xlsx", BENEFITS_CONFIG_WRKBK)[0] + "_" + DERIVEDFACTORS_LOS)
        write_status(output, RESULTS_DIR_PATH + re.split(".xlsx", BENEFITS_CONFIG_WRKBK)[0] + "_" + DERIVEDFACTORS_LOS + "_Results_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx")
    else:
        print("No data rows to process. Check the source workbook to ensure it is valid!")
print("Process Ended At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
