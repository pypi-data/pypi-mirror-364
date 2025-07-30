from playwright.sync_api import Playwright, sync_playwright, expect
from ConfigAutomation.Baseline.src.ConfigFileNames import *
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

    # Navigate to Setup and Maintenance
    page.locator("//a[@title=\"Settings and Actions\"]").click()
    page.get_by_role("link", name="Setup and Maintenance").click()
    page.wait_for_timeout(5000)
    page.get_by_role("link", name="Tasks").click()
    page.locator("[id=\"__af_Z_window\"]").get_by_role("link", name="Search").click()
    page.wait_for_timeout(3000)
    page.get_by_role("textbox").fill("Manage Value Sets")
    page.get_by_role("textbox").press("Enter")
    page.get_by_role("link", name="Manage Value Sets", exact=True).click()

    PreValue = ''
    i = 0
    while i < rowcount:
        datadictvalue = datadict[i]
        page.wait_for_timeout(4000)
        if datadictvalue["C_VALUE_SET_CODE"] != PreValue:
            # Save the prev type data if the row contains a new type
            if i > 0:
                page.wait_for_timeout(3000)
                if page.get_by_role("heading", name="Manage Values").is_visible():
                    page.get_by_role("button", name="Save and Close", exact=True).click()
                page.wait_for_timeout(3000)
                if page.get_by_role("heading", name="Create Value Set").is_visible():
                    page.get_by_role("button", name="Save and Close", exact=True).click()
                page.wait_for_timeout(3000)


            page.get_by_role("button", name="Create").click()
            page.wait_for_timeout(2000)
            page.get_by_label("Value Set Code").fill(datadictvalue["C_VALUE_SET_CODE"])
            page.get_by_label("Description").fill(datadictvalue["C_DSCRPTN"])
            page.get_by_label("Module").fill(datadictvalue["C_MDL"])
            page.get_by_label("Validation Type").select_option(datadictvalue["C_VLDTN_TYPE"])
            page.get_by_label("Value Data Type").select_option(datadictvalue["C_VALUE_DATA_TYPE"])
            if datadictvalue["C_SCRTY_ENBLD"] == 'Yes':
                page.get_by_text("Security enabled").check()
            if datadictvalue["C_SCRTY_ENBLD"] == 'No' or '':
                page.get_by_text("Security enabled").uncheck()

            page.get_by_label("Value Subtype").click()
            page.get_by_label("Value Subtype").select_option(datadictvalue["C_VALUE_SBTYP"])
            page.wait_for_timeout(2000)
            page.get_by_label("Maximum Length").fill(str(datadictvalue["C_MXMM_LNGTH"]))
            page.get_by_label("Minimum Value").fill(str(datadictvalue["C_MNMM_VALUE"]))
            page.get_by_label("Maximum Value").click()
            page.get_by_label("Maximum Value").fill(str(datadictvalue["C_MXMM_VALUE"]))
            if datadictvalue["C_UPPER_CASE"] == 'Yes':
                page.get_by_text("Uppercase only").check()
            if datadictvalue["C_UPPER_CASE"] == 'No' or '':
                page.get_by_text("Uppercase only").uncheck()
            if datadictvalue["C_ZERO_FILL"] == 'Yes':
                page.get_by_text("Zero fill").check()
            if datadictvalue["C_ZERO_FILL"] == 'No' or '':
                page.get_by_text("Zero fill").uncheck()
            page.get_by_role("button", name="Save", exact=True).click()
            page.wait_for_timeout(2000)
            if page.get_by_role("button", name="Manage Values").is_enabled():
                page.get_by_role("button", name="Manage Values").click()
                page.wait_for_timeout(2000)
            else:
                page.get_by_role("button", name="Save and Close", exact=True).click()
            PreValue = datadictvalue["C_VALUE_SET_CODE"]

        if datadictvalue["C_VALUE"] != '':
            page.get_by_role("button", name="Create").click()
            page.wait_for_timeout(2000)
            page.locator("// span[text() = 'Value'] // following::input[1]").click()
            page.locator("// span[text() = 'Value'] // following::input[1]").fill(datadictvalue["C_VALUE"])
            page.locator("//span[text()='Description']//following::input[2]").fill(datadictvalue["C_VALUE_DSCRPTN"])
            if datadictvalue["C_ENBLD"] == 'Yes':
                page.locator("//span[text()='Enabled']//following::label[contains(@id,'Label0')][1]").check()
            if datadictvalue["C_ENBLD"] == 'No':
                page.locator("//span[text()='Enabled']//following::label[contains(@id,'Label0')][1]").uncheck()
            page.locator("//span[text()='Start Date']//following::input[contains(@placeholder,'m/d/yy')][1]").fill(datadictvalue["C_START_DATE"])
            page.locator("//span[text()='End Date']//following::input[contains(@placeholder,'m/d/yy')][2]").fill(datadictvalue["C_END_DATE"])
            page.locator("//span[text()='Sort Order']//following::input[contains(@id,'ot9::content')][1]").fill(datadictvalue["C_SORT_ORDER"])


        print("Row Added - ", str(i))
        datadictvalue["RowStatus"] = "Row Added"

        i = i + 1

        # Do the save of the last DFF Values before signing out
        if i == rowcount:
            page.wait_for_timeout(3000)
            if page.get_by_role("heading", name="Manage Values").is_visible():
                page.get_by_role("button", name="Save and Close", exact=True).click()
            page.wait_for_timeout(3000)
            if page.get_by_role("heading", name="Create Value Set").is_visible():
                page.get_by_role("button", name="Save and Close", exact=True).click()
            page.wait_for_timeout(3000)


    if page.get_by_role("heading", name="Manage Value Sets").is_visible():
        page.get_by_role("button", name="Save and Close", exact=True).click()


    try:
        expect(page.get_by_role("button", name="Done")).to_be_visible()
        print("Payables DFF vaues Saved Successfully")
        # datadictvalue["RowStatus"] = "Payables DFF vaues are added successfully"

    except Exception as e:
        print("Payables DFF vaues not saved")
        # datadictvalue["RowStatus"] = "Payables DFF vaues not added"

    page.wait_for_timeout(2000)
    OraSignOut(page, context, browser, videodir)
    return datadict


# ****** Execution Starts Here ******
print("Process Started At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
if CheckWrkbkForProcessing(SOURCE_DIR_PATH + AP_WORKBOOK, DFF_VALUES):
    CreateWrkbkForProcessing(SOURCE_DIR_PATH + AP_WORKBOOK, DFF_VALUES, PRCS_DIR_PATH + AP_WORKBOOK)
    rows, cols, datadictwrkbk = ImportWrkbk(PRCS_DIR_PATH + AP_WORKBOOK, DFF_VALUES)
    if rows > 0:
        with sync_playwright() as pw:
            output = configure(pw, rows, datadictwrkbk,
                               VIDEO_DIR_PATH + re.split(".xlsx", AP_WORKBOOK)[0] + "_" + DFF_VALUES)
        write_status(output, RESULTS_DIR_PATH + re.split(".xlsx", AP_WORKBOOK)[
            0] + "_" + DFF_VALUES + "_Results_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx")
    else:
        print("No data rows to process. Check the source workbook to ensure it is valid!")
print("Process Ended At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))