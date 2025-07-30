from playwright.sync_api import Playwright, sync_playwright, expect
from ConfigAutomation.Baseline.src.utils import *

def configure(playwright: Playwright, rowcount, datadict, videodir) -> dict:
    browser, context, page = OpenBrowser(playwright, False, videodir)
    page.goto(BASEURL)
    page.wait_for_timeout(5000)
    if page.get_by_placeholder("User ID").is_visible():
        page.get_by_placeholder("User ID").click()
        page.get_by_placeholder("User ID").fill(IMPLUSRID)
        page.get_by_placeholder("Password").fill(IMPLUSRPWD)
    else:
        page.get_by_placeholder("User name").click()
        page.get_by_placeholder("User name").fill(IMPLUSRID)
        page.get_by_role("textbox", name="Password").fill(IMPLUSRPWD)
    page.wait_for_timeout(5000)
    page.get_by_role("button", name="Sign In").click()
    page.locator("//a[@title=\"Settings and Actions\"]").click()
    page.get_by_role("link", name="Setup and Maintenance").click()
    page.wait_for_timeout(5000)
    page.get_by_role("link", name="Tasks").click()
    page.get_by_role("link", name="Manage Implementation Projects").click()
    page.get_by_label("Name").click()
    page.get_by_label("Name").type("HCM Implementation Project")
    page.get_by_role("button", name="Search", exact=True).click()
    page.wait_for_timeout(2000)
    # page.get_by_role("button", name="Done").click()
    page.get_by_role("cell", name="HCM Implementation Project", exact=True).click()
    page.get_by_role("button", name="Edit").click()
    page.wait_for_timeout(4000)
    page.get_by_role("cell", name="Expand Task ListWorkforce Deployment", exact=True).get_by_role("link").click()
    page.wait_for_timeout(1000)
    page.get_by_role("cell", name="Expand Task List*Define Common Applications Configuration for Human Capital Management", exact=True).get_by_role("link").click()
    page.wait_for_timeout(1000)
    page.get_by_role("cell", name="Expand Task List*Define Enterprise Structures for Human Capital Management", exact=True).get_by_role("link").click()
    page.wait_for_timeout(1000)
    page.get_by_role("cell", name="Expand Iterative Task List*Define Legal Entities for Human Capital Management", exact=True).get_by_role("link").click()
    page.wait_for_timeout(1000)
    page.get_by_role("cell", name="Expand Iterative Task List*Define Legal Reporting Units for Human Capital Management", exact=True).get_by_role("link").click()
    page.wait_for_timeout(6000)
    page.locator("//span[text()='Legal Reporting Unit Calculation Cards']//following::a[@title='Go to Task']").first.click()
    page.wait_for_timeout(7000)


    i = 0
    while i < rowcount:
        datadictvalue = datadict[i]
        page.get_by_label("Calculation Card").click()
        page.get_by_label("Calculation Card").fill("")
        page.get_by_label("Calculation Card").type(datadictvalue["C_NAME"])
        page.get_by_label("Calculation Card").press("Tab")
        page.locator("//label[text()='Effective As-of Date']//following::input[1]").click()
        page.locator("//label[text()='Effective As-of Date']//following::input[1]").fill("")
        page.locator("//label[text()='Effective As-of Date']//following::input[1]").type(datadictvalue["C_EFFCTV_DATE"])
        page.locator("//label[text()='Effective As-of Date']//following::input[1]").press("Tab")
        page.get_by_role("button", name="Search", exact=True).click()
        page.wait_for_timeout(3000)
        page.get_by_role("link", name=datadictvalue["C_NAME"]).first.click()
        page.wait_for_timeout(4000)

        page.get_by_role("link", name="Regional").first.click()
        page.wait_for_timeout(5000)
        #Actions > Create Add Calculation Component
        # page.locator("div").filter(has_text=re.compile(r"^Actions$")).get_by_role("link").first.click()
        page.locator("//a[text()='Actions']").nth(1).click()
        page.locator("[id=\"__af_Z_window\"]").get_by_text("Create").click()
        page.wait_for_timeout(2000)
        page.get_by_role("combobox", name="State").click()
        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_STATE"], exact=True).click(force=True)
        page.wait_for_timeout(6000)
        page.get_by_role("button", name="OK").click()
        page.wait_for_timeout(2000)
        page.get_by_role("button", name="Save", exact=True).click()
        page.pause()
        page.wait_for_timeout(10000)
        # page.get_by_role("row", name=datadictvalue["C_STATE"], exact=True).get_by_role("link").click()
        page.locator("//a[text()='Regional']//following::a[text()='"+datadictvalue["C_STATE"]+"']").click(force=True)
        if page.locator("[id=\"__af_Z_tooltip\"]").get_by_role("link", name=datadictvalue["C_STATE"]).is_visible():
            page.locator("[id=\"__af_Z_tooltip\"]").get_by_role("link", name=datadictvalue["C_STATE"]).click()
        print(datadictvalue["C_STATE"])
        page.wait_for_timeout(5000)
        # State Income Tax
        page.locator("//span[text()='" + datadictvalue["C_STATE"] + "']//preceding::span[text()='State Income Tax']").first.click()
        # page.get_by_role("cell", name="State Income Tax", exact=True).click()
        page.wait_for_timeout(5000)
        page.get_by_role("link", name="Calculation Component Details").click()
        page.wait_for_timeout(2000)
        page.locator("//a[text()='Edit']").nth(1).click()
        page.wait_for_timeout(1000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text("Correct").click()
        page.wait_for_timeout(3000)

        #page.get_by_label("Calculation Component Details").click()
        #page.wait_for_timeout(2000)
        # page.get_by_role("button", name="Add Row").click()
        # page.get_by_label("Calculation Component Details").click()
        # page.get_by_label("Calculation Component Details").type(datadictvalue["C_SIT_CLCLTN_COMP"])
        # page.get_by_label("Calculation Component Details").press("Tab")
        # page.get_by_role("button", name="OK").click()
        # page.wait_for_timeout(2000)

        page.get_by_label("Supplemental Tax Calculation").click()
        page.get_by_label("Supplemental Tax Calculation").type(datadictvalue["C_SPPLMNTL_TAX_CLCLTN"])
        page.get_by_label("Supplemental Tax Calculation").press("Tab")
        page.wait_for_timeout(2000)
        if page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_SPPLMNTL_TAX_CLCLTN"],exact=True).first.is_visible():
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_SPPLMNTL_TAX_CLCLTN"],exact=True).first.click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="OK").click()
            page.wait_for_timeout(2000)
        page.wait_for_timeout(1000)
        page.get_by_label("Resident Wage Accumulation").click()
        page.get_by_label("Resident Wage Accumulation").type(datadictvalue["C_RSDNT_WAGE_ACCMLTN"])
        page.get_by_label("Resident Wage Accumulation").press("Tab")
        page.wait_for_timeout(2000)
        if page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RSDNT_WAGE_ACCMLTN"]).first.is_visible():
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RSDNT_WAGE_ACCMLTN"]).first.click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="OK").click()
            page.wait_for_timeout(2000)
        page.wait_for_timeout(1000)
        page.get_by_label("County Tax Withholding Rule").click()
        page.get_by_label("County Tax Withholding Rule").type(datadictvalue["C_CNTY_TAX_WTHHLDNG_RULE"])
        page.get_by_label("County Tax Withholding Rule").press("Tab")
        page.wait_for_timeout(2000)
        if page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_CNTY_TAX_WTHHLDNG_RULE"]).first.is_visible():
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_CNTY_TAX_WTHHLDNG_RULE"]).first.click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="OK").click()
            page.wait_for_timeout(2000)

        page.wait_for_timeout(2000)
        page.get_by_label("City Tax Withholding Rule").click()
        page.get_by_label("City Tax Withholding Rule").type(datadictvalue["C_CITY_TAX_WTHHLDNG_RULE"])
        page.get_by_label("City Tax Withholding Rule").press("Tab")
        page.wait_for_timeout(2000)
        if page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_CITY_TAX_WTHHLDNG_RULE"]).first.is_visible():
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_CITY_TAX_WTHHLDNG_RULE"]).first.click()
            page.wait_for_timeout(1000)
            page.get_by_role("button", name="OK").click()
            page.wait_for_timeout(2000)

        # State Unemployment
        page.locator("//span[text()='" + datadictvalue["C_STATE"] + "']//preceding::span[text()='State Unemployment']").first.click()
        # page.get_by_role("cell", name="State Unemployment", exact=True).click()
        page.wait_for_timeout(4000)
        page.get_by_role("link", name="Calculation Component Details").click()
        page.wait_for_timeout(2000)
        page.locator("//a[text()='Edit']").nth(1).click()
        page.wait_for_timeout(1000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text("Correct").click()
        page.wait_for_timeout(2000)
        #page.get_by_label("Calculation Component Details").click()
        #page.wait_for_timeout(2000)
        # page.get_by_role("button", name="Add Row").click()
        # page.get_by_label("Calculation Component Details").click()
        # page.get_by_label("Calculation Component Details").type(datadictvalue["C_SUI_CLCLTN_COMP"])
        # page.get_by_label("Calculation Component Details").press("Tab")
        # page.get_by_role("button", name="OK").click()
        # page.wait_for_timeout(2000)
        page.get_by_title("Search: Self Adjustment Method").click()
        page.get_by_role("link", name="Search...").click()
        page.get_by_label("Value").click()
        page.get_by_label("Value").type(datadictvalue["C_SUI_SELF_ADJSTMNT_MTHD"])
        page.get_by_role("button", name="Search", exact=True).click()
        page.wait_for_timeout(2000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_SUI_SELF_ADJSTMNT_MTHD"], exact=True).click()
        page.get_by_role("button", name="OK").click()
        page.wait_for_timeout(2000)

        #Enterable Calculation Values on Calculation Cards
        if datadictvalue["C_SUI_DSPLY_VALUE"] != "":
            page.get_by_role("link", name="Enterable Calculation Values on Calculation Cards").click()
            page.wait_for_timeout(4000)
            page.get_by_role("button", name="Create").nth(2).click()
            page.wait_for_timeout(2000)
            page.locator("[id=\"__af_Z_window\"]").get_by_title("Search").click()
            page.get_by_role("link", name="Search...").click()
            page.get_by_role("textbox", name="Display Value").click()
            page.get_by_role("textbox", name="Display Value").type(datadictvalue["C_SUI_DSPLY_VALUE"])
            page.get_by_role("button", name="Search", exact=True).click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_SUI_DSPLY_VALUE"]).click()
            page.get_by_role("button", name="OK").nth(1).click()
            page.wait_for_timeout(2000)

            # page.get_by_role("combobox", name="Value", exact=True).click()
            # page.get_by_text(datadictvalue["C_FIT_VALUE_TYPE"], exact=True).click()
            # page.get_by_role("button", name="OK").click()

            page.get_by_label("Rate").click()
            page.get_by_label("Rate").type(str(datadictvalue["C_SUI_VALUE"]))
            page.get_by_role("button", name="OK").click()

        page.wait_for_timeout(4000)
        # page.get_by_role("button", name="Save", exact=True).click()
        page.get_by_role("button", name="Save and Close").click()
        page.wait_for_timeout(5000)

        #State Income Tax for 1099-R
        # page.get_by_role("cell", name="State Income Tax for 1099-R", exact=True).click()
        # page.wait_for_timeout(5000)
        # page.get_by_role("link", name="Calculation Component Details").click()
        # page.wait_for_timeout(4000)
        # page.get_by_role("button", name="Add Row").click()
        i = i + 1
        try:
            expect(page.get_by_role("heading", name="Tax Reporting Unit")).to_be_visible()
            print("Added Legal Reporting Unit Calculation Regional Saved Successfully")
            datadictvalue["RowStatus"] = "Added Legal Reporting Unit Calculation Regional"
        except Exception as e:
            print("Unable to save Legal Reporting Unit Calculation Regional")
            datadictvalue["RowStatus"] = "Unable to Add Legal Reporting Unit Calculation Regional"


    OraSignOut(page, context, browser, videodir)
    return datadict

print("Process Started At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
if CheckWrkbkForProcessing(SOURCE_DIR_PATH + PAYROLL_CONFIG_WRKBK, LEGAL_RPT_CALCULATION_REGION):
    CreateWrkbkForProcessing(SOURCE_DIR_PATH + PAYROLL_CONFIG_WRKBK, LEGAL_RPT_CALCULATION_REGION, PRCS_DIR_PATH + PAYROLL_CONFIG_WRKBK)
    rows, cols, datadictwrkbk = ImportWrkbk(PRCS_DIR_PATH + PAYROLL_CONFIG_WRKBK, LEGAL_RPT_CALCULATION_REGION)
    if rows > 0:
        with sync_playwright() as pw:
            output = configure(pw, rows, datadictwrkbk, VIDEO_DIR_PATH + re.split(".xlsx", PAYROLL_CONFIG_WRKBK)[0] + "_" + LEGAL_RPT_CALCULATION_REGION)
        write_status(output, RESULTS_DIR_PATH + re.split(".xlsx", PAYROLL_CONFIG_WRKBK)[0] + "_" + LEGAL_RPT_CALCULATION_REGION + "_Results_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx")
    else:
        print("No data rows to process. Check the source workbook to ensure it is valid!")
print("Process Ended At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
